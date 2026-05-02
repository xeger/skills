---
name: honeycomb-triggers
description: Use when writing Terraform for honeycombio_trigger or honeycombio_query_specification resources - covers provider constraints on granularity, frequency, filter value types, and dataset selection that cause plan/apply failures
---

# Honeycomb Terraform Triggers

## Overview

The `honeycombio` Terraform provider (v0.33.x) has several non-obvious hard constraints that only surface at apply time. Know them before writing resources.

## Hard Constraints

| Constraint | Rule | Formula |
|---|---|---|
| Filter `value` for `in`/`not-in` | Comma-separated **string**, not HCL list | `value = "a,b,c"` |
| Granularity | Must be ≤ time_range / 10 | `granularity ≤ time_range / 10` |
| Trigger frequency | time_range cannot exceed 4× frequency | `time_range ≤ 4 × frequency` |
| Dataset | Column must exist in the specified dataset | Verify before assuming |

## Constraint Details

### Filter value for `in` / `not-in`

```hcl
# ❌ WRONG - HCL list fails with "string required"
filter {
  column = "k8s.namespace.name"
  op     = "in"
  value  = ["agent-control", "agent-hardware", "edge"]
}

# ✅ CORRECT - comma-separated string
filter {
  column = "k8s.namespace.name"
  op     = "in"
  value  = "agent-control,agent-hardware,edge"
}
```

### Granularity

With `time_range = 300`, max granularity is `300 / 10 = 30`.
With `time_range = 3600`, max granularity is `360`.

```hcl
# ❌ granularity = 60 with time_range = 300  →  60 > 30, fails
time_range  = 300
granularity = 60

# ✅
time_range  = 300
granularity = 30
```

### Trigger frequency vs. time_range

Error: `query duration cannot be more than 4 times the trigger frequency`

With `time_range = 3600`, minimum `frequency` is `3600 / 4 = 900`.

```hcl
# ❌ time_range = 3600, frequency = 300  →  3600 > 4×300, fails
time_range = 3600
...
frequency = 300

# ✅
time_range = 3600
...
frequency = 900
```

### Dataset / column availability

Columns only exist in the dataset where they're collected. The provider error is:

```
missing unknown column or derived column "k8s.container.restarts"
```

**Don't assume a column is in `logs` or `metrics`.** When uncertain, run the query in the Honeycomb UI against **All Datasets** first to confirm which dataset contains the column.

Common split in this repo:
- `logs` — Kubernetes log/event data (`reason`, `body.type`, …)
- `metrics` — Kubernetes metrics (`k8s.container.restarts`, …)
- `agent-hardware.parameters` — filesystem/hardware telemetry

## Quick Reference: Error Messages

| Error | Cause | Fix |
|---|---|---|
| `Incorrect attribute value type … string required` | Used HCL list for `value` | Use comma-separated string |
| `invalid granularity … not be greater than time_range/10` | granularity too large | Set `granularity ≤ time_range / 10` |
| `query duration cannot be more than 4 times the trigger frequency` | time_range too large for frequency | Set `frequency ≥ time_range / 4` |
| `missing unknown column or derived column "…"` | Wrong dataset | Verify column in Honeycomb UI under All Datasets |

## Checklist Before Writing a New Trigger

- [ ] Which dataset contains the columns I need? (verify in UI if unsure)
- [ ] Is `granularity ≤ time_range / 10`?
- [ ] Is `frequency ≥ time_range / 4`?
- [ ] Are all `in`/`not-in` filter values comma-separated strings?
