---
name: converting-go-upstream-flags
description: Use when auditing or converting Go flag.String defaults for upstream service address flags, especially repos with localhost, bare :port, or svc.cluster.local values that should support no-flag local development via ACCOUNT_NAME and safe Kubernetes defaults.
---

# Converting Go Upstream Flags

## Overview

Convert only real upstream service flags to account-aware defaults. Our standard is: local development resolves Tailnet names from `ACCOUNT_NAME`; Kubernetes resolves `service.namespace:port`; deployment YAML is the source of truth for service, namespace, and port.

## Requirements

Before changing code, you MUST:

1. Use `superpowers:test-driven-development` for helper changes and call-site behavior changes.
2. Inspect the Go `flag.String` call sites and Kubernetes deployment args for the same service.
3. Classify each flag as upstream-service or not. Convert only upstream-service flags.
4. Take service, namespace, and port from deployment YAML. Do not infer ports from memory or flag names.
5. Import any `shared/setup` helper package with alias `sharedsetup`, never the default `setup` name.
6. Read `support/defaults.go` and `support/defaults_test.go` only when copying or adapting the helper/tests.

## What To Convert

Convert `flag.String` defaults for service dependencies: gRPC/HTTP addresses used by clients to call another service. Typical bad defaults are `":10570"`, `"localhost:8091"`, `"http://localhost:8091"`, and hard-coded `*.svc.cluster.local` values.

Never convert listen addresses or infrastructure settings: `grpc-addr`, `http-addr`, `metrics-addr`, `otel-addr`, Redis, Temporal, credentials, external APIs, or model/provider config.

## Conversion Rules

Use deployment YAML as truth:

- `-agent-addr=agent.iam:10570` -> `DefaultUpstreamAddr("agent", "iam", 10570)`
- `-mapping-addr=mapping.narrator:8080` -> `DefaultUpstreamAddr("mapping", "narrator")`
- `-foo-url=http://foo.bar:8080` -> `"http://" + DefaultUpstreamAddr("foo", "bar")` when the scheme is fixed.

When the helper lives in an imported `shared/setup` package, always write the import as `sharedsetup "path/to/shared/setup"` and call `sharedsetup.DefaultUpstreamAddr(...)`.

The helper MUST use `KUBERNETES_SERVICE_HOST` to choose Kubernetes DNS. In cluster, return `service.namespace:port`. Outside cluster, return `service-namespace-account:port`, with `ACCOUNT_NAME` defaulting to `sandbox`.

Tailscale exposes all ports on exposed services. Preserve legacy magic ports from deployment YAML until a human harmonizes the service to standard `8080`.

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
| Inlining helper/tests in the skill body | Every skill load burns context on code not always needed | Keep code in support files |
| Importing `shared/setup` as `setup` | Call sites read like generic setup and drift from local convention | Always alias the import as `sharedsetup` |
| Using Tailnet defaults in Kubernetes | Pods require every upstream flag to be specified | Always branch on `KUBERNETES_SERVICE_HOST` |
| Skipping tests when copying helper code | Diverged helpers silently break local or cluster defaults | Copy/adapt the tests with the helper |
