---
name: converting-services-to-standard-ports
description: Use when migrating a Kubernetes microservice off legacy per-service "magic ports" to a shared standard pair (8080 for primary protocol, 8081 for ops — metrics, health, pprof) while keeping unconverted callers working via a dual-port Service. Covers discovery of legacy references, the entrypoint/Deployment/Service transformation, verification, and retirement of the compat layer.
---

# Converting Services to Standard Ports

## Overview

The pattern: every microservice's **Pod** listens on the same pair of container ports — **8080** for its primary protocol (gRPC, HTTP, GraphQL, whatever is user-facing) and **8081** for the operations mux (Prometheus metrics, health/readiness, pprof, debug). Services are distinguished by DNS and Service objects, not by port numbers.

The migration: flip the Pod to the standard ports while keeping the legacy "magic port" reachable **on the Service object**, so unconverted callers keep working. The Pod speaks only the new pattern; the Service speaks both.

**Core rule:** the Pod listens on {8080, 8081}. The Service fans each legacy port number into the corresponding named container port alongside the standard one. The compat layer lives in the Service manifest and nowhere else.

## When to Use

- A service whose process binds legacy magic ports (e.g. 9080, 14000, 10420) and you want it on 8080/8081.
- Any time you touch ports on a service that isn't yet on the standard pattern.

**Do NOT use for:**
- Services already on 8080/8081 with no legacy callers — just verify.
- Upstream-address configuration (flags/env vars like `BLUEPRINT_ADDR=...:14000`) in *this* service's Deployment that dials a different service. Those track the *upstream's* current listening port and are a separate migration per upstream.

Note the distinction: this carveout is about *this* service's Deployment dialing *other* services. It does **not** forbid updating *downstream callers* of the service being migrated — CLIs, tools, and sibling services whose default points at this service's legacy port are in scope for the inventory step below.

## Before You Start: Inventory Legacy References

Skipping this is how callers get broken. For each legacy port the service currently exposes:

1. **Grep the monorepo** (and any sibling repos you can reach) for the literal port number:
   ```bash
   # Replace <N> with each legacy port number. Run for both the primary and metrics ports.
   # The (^|[^0-9]) and ([^0-9]|$) anchors keep 10580 from matching 105800.
   rg -n --hidden -g '!.git' '(^|[^0-9])<N>([^0-9]|$)'
   ```
   Look for:
   - Deployment args, ConfigMaps, Secrets referencing `:<port>`
   - Client code dialing `<host>:<port>`
   - CI/deploy scripts, Makefiles, Tiltfiles, docker-compose files
   - Tool binaries (CLIs, migrations, one-offs) that default to the legacy port
   - Centralized port-default helpers (e.g. a shared `DefaultUpstreamAddr(service, namespace, port...)` utility where callers pass a per-service port override). Converting the service means dropping the override at each call site so the helper falls back to the new standard — not editing the helper itself.
   - CI workflow YAMLs (`.github/workflows/*.yaml`, GitLab `.gitlab-ci.yml`, CircleCI, etc.) — port numbers show up in integration-test services, healthcheck URLs, and smoke-test scripts.
2. **Check Kubernetes surfaces that reference Service ports by number:**
   - `Ingress` / `HTTPRoute` / `Gateway` backend refs
   - `NetworkPolicy` ingress/egress rules
   - `ServiceMonitor` / `PodMonitor` (Prometheus Operator) — **often scrapes the metrics port directly**
   - Service mesh configs: Istio `VirtualService`/`DestinationRule`, Linkerd, Consul
   - Any `NodePort`/`LoadBalancer` Service declarations
   - **Exposure annotations on the Service being converted** (`tailscale.com/expose`, cloud LB annotations, Cloudflare Tunnel, ngrok). If present, note it — the compat entries will be exposed through the same mechanism, which is usually desired (see §3) but must be a conscious decision.
   - **Kustomize overlays / Helm values** that patch port numbers per environment
3. **Check external references:**
   - External DNS records / LB target groups
   - Observability scrape configs outside the cluster
   - Runbooks, dashboards, alert queries that hardcode the port
4. **Record what you find, and decide per hit** whether it moves now or later:
   - **Update in this commit** if the caller is in-repo, trivial to change, and you're confident the change is safe. This shortens the path to retiring the compat layer.
   - **Leave on the legacy port, covered by the compat Service entry** if the caller is out-of-repo, high-risk, or large-surface. The compat Service port keeps it working unchanged.
   - Pick one policy per migration and apply it consistently. Drifting between "update this caller but not that one" creates an ambiguous state for the next engineer.

   You cannot safely retire the compat layer until every caller has been moved off the legacy port.

If the service has separate legacy ports for primary protocol and metrics (common), run this for **each** one. Metrics ports especially get forgotten because Prometheus scrapes are invisible from the service's own code.

## Multi-Protocol Services

The pattern allocates exactly two ports. Fit your service to it:

| Situation | 8080 | 8081 |
|---|---|---|
| Pure gRPC | gRPC | metrics + health + pprof |
| Pure HTTP/REST/GraphQL | HTTP | metrics + health + pprof |
| gRPC + HTTP (both user-facing) | Choose one as primary; multiplex (e.g. gRPC-Web, connect-go) or run the secondary on 8081 alongside ops only if unavoidable | metrics + health + pprof |
| HTTP + metrics only | HTTP | metrics + health |

The 8081 mux always carries ops endpoints. If you need a second user-facing protocol on its own port, that's a design decision to raise explicitly — the pattern doesn't reserve a third standard port.

## The Transformation

Four surfaces, in this order:

### 1. Service entrypoint (main.go / main.py / server.ts / etc.)

- The listener for the primary protocol defaults to `:8080`.
- The listener for the ops mux (metrics + health + pprof + debug) defaults to `:8081`.
- Delete any knob that binds a legacy port. The process does not need to know the legacy number exists.
- Whatever mechanism you use for addresses — CLI flags, env vars, a config struct — update the **defaults** so the service starts correctly with no configuration.
- **Only the defaults change.** Flag/env-var *names* (`-grpc-addr`, `METRICS_ADDR`, etc.) stay the same. Renaming the knobs breaks operators and Deployment args for no benefit.

### 2. Deployment manifest

```yaml
ports:
  - containerPort: 8080
    name: grpc            # or "http" — name reflects the primary protocol
  - containerPort: 8081
    name: http-metrics    # ops mux; "http-metrics" or "http-ops" are common
readinessProbe:
  httpGet:
    path: /healthz
    port: 8081
livenessProbe:            # if present
  httpGet:
    path: /livez
    port: 8081
```

- **Name** the container ports. The Service will reference them by name so two Service ports can fan into one container port.
- Probes target 8081.
- Remove any legacy `containerPort` entries. The Pod does not listen on them anymore.
- Leave upstream-address configuration (args dialing *other* services) untouched.

**Why no legacy port on the Pod:** duplicating listeners inside the process doubles the attack surface, drifts TLS/auth config between the two ports, and defeats the point. The Service is the compat boundary; the Pod is forward-looking.

### 3. Service manifest — the compat layer

For **each** container port that previously had a legacy equivalent, expose both the standard and legacy Service port, both pointing at the **named** container port:

```yaml
spec:
  type: ClusterIP
  ports:
    # Legacy ports — kept for unconverted callers. Remove once all callers migrate.
    # Prefix with "deprecated-" so the entries are obvious in `kubectl get svc` output and grep-able at retirement.
    - name: deprecated-grpc
      targetPort: grpc            # NAMED, not numeric
      port: <LEGACY_PRIMARY>      # e.g. 9080, 14000
    - name: deprecated-http-metrics
      targetPort: http-metrics
      port: <LEGACY_METRICS>      # e.g. 9081, 14001
    # Standard ports.
    - name: grpc
      targetPort: grpc
      port: 8080
    - name: http-metrics
      targetPort: http-metrics
      port: 8081
  selector:
    app: <svc>
```

Rules:
- `targetPort` uses the **name** from the Deployment's `containerPort`, not the number. This is what enables the fan-in.
- **Prefix legacy entries with `deprecated-`.** It's fully spelled out, unambiguous, and matches existing conventions in production services. Apply it consistently so the retirement sweep is mechanical (`grep 'deprecated-'` across Service manifests).
- **Naming rules (for reference — `deprecated-*` on a Service port is fine; you're well within the DNS-1123 label limit):**
  - `ServicePort.name` is a DNS-1123 label: up to **63 chars**, lowercase alphanumeric + hyphens. `deprecated-http-metrics` is fine here.
  - `ContainerPort.name` (in the Pod/Deployment spec) is stricter: IANA_SVC_NAME, **up to 15 chars**, must contain a letter. You are **not** renaming container ports in this migration, so this limit only matters if you want to rename the container port (don't).
  - A string `targetPort` must match an existing `ContainerPort.name` exactly — so it inherits that 15-char ceiling by reference.
- If the service had only one legacy port (e.g. no separate metrics exposure), add only the one legacy entry.
- If an `Ingress`/`HTTPRoute`/`ServiceMonitor`/etc. you found during inventory points at the legacy port *number* on this Service, it keeps working unchanged — the whole point of the compat layer. You'll update those callers incrementally, then retire the legacy entries.
- **Exposure side-effect.** Annotations like `tailscale.com/expose: "true"`, cloud LB configs, or similar that expose the Service externally will now expose the legacy ports too. That is the intent of the compat layer. If you don't want the legacy ports reachable externally (rare), you'll need a separate ClusterIP Service for the compat entries and the exposure annotation on the standard-ports Service only.

### 4. Documentation

Document the **destination state**, not the migration shim:

- **Do update** dev/usage instructions that reference port numbers (`grpc_cli localhost:<port>`, `kubectl port-forward svc/<svc> <port>`, README snippets showing the service's bind address). Post-migration the binary binds 8080/8081; that's what local devs will see. Leaving the old numbers in examples confuses readers.
- **Do not add** a new "legacy port also supported" section. The legacy Service entries are a transitional shim, not contract.
- **Repo-wide port catalogs / service indexes** (a top-level README or docs page listing every service's exposed ports) are a judgment call. Use the table's framing:
  - **Titled "exposed ports," "service endpoints," "dial these":** it's the caller-facing contract. Update only when all callers have migrated and you retire the compat layer.
  - **Titled "container ports," "internal ports," or describing what the Pod binds:** update now — the Pod now binds 8080/8081.
  - **Ambiguous or untitled** (very common: pre-migration, both were the same number, so the table's intent was never forced):  leave it alone and flag in the PR description. A cross-cutting doc sweep is a separate piece of work and trying to do it here expands blast radius.

## Verification Checklist

After deploying the change to a non-prod environment:

- [ ] `kubectl get svc <svc> -o wide` shows four ports (two standard, two prefixed legacy entries) — or two and one if there's only one legacy port.
- [ ] `kubectl get endpoints <svc>` shows every Pod IP on both `8080` and `8081`. (Endpoints list resolved container ports, so legacy Service ports don't appear here — that's expected.)
- [ ] `kubectl port-forward svc/<svc> 8080:8080` + a real RPC/request succeeds.
- [ ] `kubectl port-forward svc/<svc> 18080:<LEGACY_PRIMARY>` + the same request succeeds. This proves the compat fan-in works.
- [ ] `kubectl port-forward svc/<svc> 8081:8081` → `curl localhost:8081/healthz` returns 200 and `/metrics` returns Prometheus output.
- [ ] Same via the legacy metrics port if present.
- [ ] Readiness probe passing: `kubectl get pod` shows `Ready 1/1`.
- [ ] Prometheus (or whatever scrapes metrics) is still receiving samples — confirm in the UI, not just in config.
- [ ] Any Ingress/NetworkPolicy/ServiceMonitor you touched still resolves (no stale named-port references).

Do not claim the migration complete on the strength of "it deployed." A `ServiceMonitor` that silently stopped scraping is a regression you won't notice for hours.

## Retiring the Compat Layer

Prerequisites before removing the legacy entries:

1. Inventory from "Before You Start" is re-run and shows zero remaining references to the legacy port number.
2. Traffic on the deprecated Service port is zero over a meaningful window (check via metrics — connection counters, access logs, or a sidecar/mesh view). Grep alone misses dynamic and out-of-repo clients.
3. Any observability scrape has been re-pointed at the standard port and has been producing samples for that window.

Then:
1. Delete the legacy entries from the Service manifest.
2. Commit separately from any functional change, with a message that names the port being retired so future archaeology can find it.

No change is needed in the Deployment or in the service's code at retirement time — the Pod never knew about the legacy port.

## Common Mistakes

- **Numeric `targetPort` in the Service.** Works, but hides the fan-in relationship and breaks when the container is renumbered. Use the name.
- **Leaving the legacy port bound in the process.** Doubles listeners, splits config, and means the compat layer isn't actually centralized in the Service.
- **Forgetting the metrics legacy port.** Prometheus scrapes are invisible from the service's code. If the old metrics port was 9081, callers (ServiceMonitors, external scrapers) may still be hitting it.
- **Changing upstream-address flags along the way.** Those point at *other* services. Touch only this service's exposed ports in this migration.
- **Naming drift.** Service `targetPort: grpc` only works if the Deployment container's port is `name: grpc`. Keep the names identical across both manifests.
- **Dropping legacy entries before observability confirms silence.** Grep is necessary but not sufficient — dynamic and external clients don't show up in `grep`.
- **Using a different prefix than `deprecated-`** for legacy Service entries. `old-*`, `legacy-*`, `dep-*` all work mechanically but diverge from the team convention and make the retirement sweep non-mechanical. Stick to `deprecated-`.
- **Confusing the Service port name limit (63) with the container port name limit (15).** `ServicePort.name` is a DNS-1123 label, so `deprecated-http-metrics` is fine. `ContainerPort.name` is IANA_SVC_NAME (15 chars max) — that limit only bites if you rename container ports, which this migration does not.
- **Renaming the container port during this migration.** If the legacy Deployment used a different port name, leaving it as-is and adding the new one is fine; but don't *rename* during the cutover — ServiceMonitors and other named-port references break silently.

## Quick Reference

| Surface | Legacy ports appear? | Why |
|---|---|---|
| Process entrypoint (main/server) | No | Binds new ports only |
| Deployment `containerPort` | No | Pod listens on new ports only |
| Deployment probes | No | Target 8081 |
| Deployment upstream-addr config | Yes, unchanged | Dials other services at their current ports |
| Service `ports` | **Yes, alongside new** | Compat fan-in via named `targetPort` |
| Ingress/NetworkPolicy/ServiceMonitor | Depends — audit during inventory | May reference legacy port number; update in lockstep or rely on compat Service entry |
| Documentation | No | Describe destination state only |
