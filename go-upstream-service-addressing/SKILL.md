---
name: go-upstream-service-addressing
description: Standardize Go upstream service addressing for flag.String defaults and service dependency configuration. Use when auditing, converting, re-normalizing, or creating upstream service address flags, especially repos with localhost, bare :port, logical service-name guesses, or svc.cluster.local values that should support Kubernetes, Tilt/kind local dev, and host lazy dev via ACCOUNT_NAME/Tailnet defaults.
---

# Go Upstream Service Addressing

## Overview

Convert only real upstream service flags to defaults that work in all three standard runtime modes:

- Real Kubernetes deployment: pods resolve `service.namespace:port`; deployment YAML may still pass explicit `*.svc.cluster.local` args.
- Tilt/kind local dev: the service also runs inside Kubernetes and resolves `service.namespace:port`; Tilt `forward_services` may back those names with cloud dependencies.
- Host lazy dev: the service runs outside Kubernetes and resolves Tailnet names from `ACCOUNT_NAME`, as `service-namespace-account:port`.

The concrete Kubernetes Service name, namespace, and exposed port are the source of truth. Never derive the helper args from the flag name, package name, or a "friendly" logical service name.

## Requirements

Before changing code, you MUST:

1. Use `superpowers:test-driven-development` for helper changes and call-site behavior changes.
2. Inspect the Go `flag.String` call sites, Kubernetes deployment args, matching Service manifests, and any Tilt `forward_services` entries for the same upstream.
3. Classify each flag as upstream-service or not. Convert only upstream-service flags.
4. Take service name, namespace, and port from the concrete Kubernetes Service/deployment contract. Do not infer them from memory, flag names, client package names, or abbreviated component names.
5. Import any `shared/setup` helper package with alias `sharedsetup`, never the default `setup` name.
6. Read `support/defaults.go` and `support/defaults_test.go` only when copying or adapting the helper/tests.

## What To Convert

Convert `flag.String` defaults for service dependencies: gRPC/HTTP addresses used by clients to call another service. Typical bad defaults are `":10570"`, `"localhost:8091"`, `"http://localhost:8091"`, and hard-coded `*.svc.cluster.local` values.

Never convert listen addresses or infrastructure settings: `grpc-addr`, `http-addr`, `metrics-addr`, `otel-addr`, Redis, Temporal, credentials, external APIs, or model/provider config.

## Conversion Rules

Use the concrete Kubernetes Service identity as truth:

- `-agent-addr=agent.iam:10570` -> `DefaultUpstreamAddr("agent", "iam", 10570)`
- `-mapping-addr=mapping.narrator:8080` -> `DefaultUpstreamAddr("mapping", "narrator")`
- `-registry-addr=scheduling-registry.scheduling:10220` -> `DefaultUpstreamAddr("scheduling-registry", "scheduling", 10220)`, even if the Go flag is named `registry-addr`
- `-foo-url=http://foo.bar:8080` -> `"http://" + DefaultUpstreamAddr("foo", "bar")` when the scheme is fixed.

When the helper lives in an imported `shared/setup` package, always write the import as `sharedsetup "path/to/shared/setup"` and call `sharedsetup.DefaultUpstreamAddr(...)`.

The helper MUST use `KUBERNETES_SERVICE_HOST` to choose Kubernetes DNS. In a real cluster or a Tilt/kind local cluster, return `service.namespace:port`. Outside Kubernetes for host lazy dev, return `service-namespace-account:port`, with `ACCOUNT_NAME` defaulting to `sandbox`.

Tailscale exposes all ports on exposed services and derives hostnames from the actual exposed Service identity, not from the consuming flag name. Preserve legacy magic ports from the Service/deployment contract until a human harmonizes the service to standard `8080`.

If deployment YAML passes a fully qualified name like `foo.bar.svc.cluster.local.:1234`, drop only the Kubernetes suffix when calling the helper: `DefaultUpstreamAddr("foo", "bar", 1234)`.

## Support Files

The main skill stays small. When exact code is needed, read:

- `support/defaults.go` for the helper
- `support/defaults_test.go` for table-driven tests

Copy both files together unless the repo already has an equivalent helper. If adapting them, write failing tests first.

## Common Mistakes

| Mistake | Result | Fix |
|---------|--------|-----|
| Converting listen flags | Service binds to an upstream hostname instead of a local port | Never convert listen, metrics, or otel flags |
| Guessing ports from conventions | Local defaults connect to the wrong exposed port | Always copy the port from deployment YAML |
| Guessing service names from flag names | Lazy dev tries `registry-scheduling-office` when Tailscale exposes `scheduling-registry-scheduling-office` | Always use the actual Kubernetes Service name |
| Treating Tilt local dev as host lazy dev | Pods in kind use Tailnet names even though Kubernetes DNS is available | Always branch on `KUBERNETES_SERVICE_HOST`; Tilt/kind is in-cluster |
| Inlining helper/tests in the skill body | Every skill load burns context on code not always needed | Keep code in support files |
| Importing `shared/setup` as `setup` | Call sites read like generic setup and drift from local convention | Always alias the import as `sharedsetup` |
| Using Tailnet defaults in Kubernetes | Pods require every upstream flag to be specified | Always branch on `KUBERNETES_SERVICE_HOST` |
| Skipping tests when copying helper code | Diverged helpers silently break local or cluster defaults | Copy/adapt the tests with the helper |
