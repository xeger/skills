---
name: golangci-lint-tool-version
description: Use when auditing, pinning, upgrading, or reproducing golangci-lint version management across Go repositories, especially with .tool-versions, scripts/setup, scripts/lint, GitHub Actions, asdf, mise, or CI cache keys.
---

# Golangci-Lint Tool Version

## Overview

Use one source of truth for `golangci-lint`: `.tool-versions`. Our repo scripts and CI must consume that pin instead of copying the version into workflows, lint wrappers, Dockerfiles, or README commands.

## Requirements

Before changing another repository, you MUST:

1. Audit `.tool-versions`, `.github/**`, and `scripts/**`.
2. Verify exactly where `golangci-lint` is installed and where it is executed.
3. Keep install/setup separate from lint execution.
4. Key CI binary caches on both `.tool-versions` and the setup script that installs tools.
5. Report every duplicate hard-coded `golangci-lint` version before editing.

## Reference Pattern

The elegant pattern has four parts:

| Concern | File | Required behavior |
|---------|------|-------------------|
| Version pin | `.tool-versions` | Contains the only `golangci-lint` version, plus local tool manager guidance. |
| Installation | `scripts/setup` | Reads the desired version from `.tool-versions`, compares the installed binary, installs when mismatched. |
| Execution | `scripts/lint` | Runs `golangci-lint run`; it does not install or pin versions. |
| CI cache | `.github/workflows/*.yml` | Cache key includes `.tool-versions` and `scripts/setup`, so version or installer changes invalidate stale binaries. |

## Audit Workflow

1. Search for all references:

```bash
rg 'golangci|tool-versions|scripts/setup|scripts/lint|gobin_cache_key|GOBIN|GOPATH' .tool-versions .github scripts
```

2. Classify every match:

| Match type | Keep? | Action |
|------------|-------|--------|
| `.tool-versions` pin | Yes | Make this the source of truth. |
| asdf/mise install comment | Yes | Keep local onboarding near the pin. |
| setup script reading `.tool-versions` | Yes | Ensure it installs the exact pinned version. |
| lint script running `golangci-lint run` | Yes | Keep it version-agnostic. |
| CI cache hashing `.tool-versions` and setup | Yes | Preserve or add it. |
| Workflow hard-coding `golangci-lint` version | No | Replace with setup script consumption. |
| README hard-coding version | No | Point to `.tool-versions` and `scripts/setup`. |

3. Confirm the setup/lint split:

```bash
# setup owns installation
desired_lint=$(grep -E '^golangci-lint' .tool-versions | cut -d' ' -f2)
installed_lint=$(golangci-lint --version 2> /dev/null | cut -d' ' -f4)
if [ "$installed_lint" != "$desired_lint" ]; then
  curl -sSfL https://raw.githubusercontent.com/golangci/golangci-lint/HEAD/install.sh | sh -s -- -b "$(go env GOPATH)/bin" "v${desired_lint}"
fi

# lint owns execution only
golangci-lint run "$@"
```

4. Confirm CI invalidates stale tools:

```yaml
gobin_cache_key: gobin-${{ hashFiles('.tool-versions', 'scripts/setup') }}
```

If CI uses a different cache input name, apply the same invariant: the Go binary cache key MUST change when `.tool-versions` or the installer script changes.

## Reproduction Checklist

When porting this pattern, implement these in order:

1. Add `.tool-versions` entry:

```text
# asdf plugin add golangci-lint https://github.com/hypnoglow/asdf-golangci-lint
golangci-lint 2.11.4
```

2. Add or update `scripts/setup` so it reads the version from `.tool-versions` and installs that exact release.
3. Add or update `scripts/lint` so it only runs `golangci-lint run`, preserving repo-specific args like `DEBUG`, `--verbose`, or default `./...`.
4. Update GitHub Actions setup steps so the tool cache key hashes `.tool-versions` and `scripts/setup`.
5. Remove duplicate version pins from workflows, README snippets, Makefiles, Dockerfiles, and ad hoc install commands.
6. Run setup, lint, and CI-equivalent verification.

## Common Mistakes

| Mistake | Result | Fix |
|---------|--------|-----|
| Hard-coding the version in GitHub Actions | Local and CI lint drift | Always read the version from `.tool-versions` through setup. |
| Installing inside `scripts/lint` | Every lint run mutates tools and slows feedback | Keep installation in `scripts/setup`; keep lint execution pure. |
| Caching only on Go version or lockfiles | CI reuses an old `golangci-lint` binary after upgrades | Include `.tool-versions` and `scripts/setup` in the binary cache key. |
| Updating `.tool-versions` without setup verification | Developers believe the pin changed while CI still runs the old binary | Run setup before lint and inspect `golangci-lint --version`. |
| Treating asdf/mise as the CI installer | CI behavior depends on local dev tooling assumptions | Let setup install the binary directly; keep asdf/mise comments as local guidance. |

## Verification

After edits, run:

```bash
scripts/setup
golangci-lint --version
scripts/lint
```

The reported `golangci-lint` version MUST match `.tool-versions`. If the repo has CI setup locally available, run the same command path CI uses instead of inventing a separate verification path.
