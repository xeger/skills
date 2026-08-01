---
name: process-view
description: >-
  Edit and rebuild ATLAS process views on atlaslive.io (facility Process tab /
  process-view URL) by placing equipment and positioning React Flow nodes
  programmatically. Use when recreating a SCADA/process diagram, adding or
  arranging equipment on a process canvas, or when the user mentions process
  view, process diagram, Add equipment, or atlaslive process-view editing.
---

# Process View

Build and rearrange process diagrams in the atlaslive.io Process View editor.
Prefer programmatic React Flow updates over mouse drag — drag is slow, zoom-
sensitive, and fails when labels have `pointer-events-none`.

## Before you touch the canvas

Complete this checklist:

1. Confirm the facility URL (e.g. `…/amrize/<site>/process-view`).
2. Confirm **Editing Enabled** is on.
3. Snapshot / screenshot current zoom and node positions — the user may have
   panned or zoomed; never assume the prior turn's viewport.
4. Never Save or Discard unless the user explicitly asks.

## Adding equipment

1. Open **Tools → Add equipment** (or the empty-state **Add equipment** button).
2. Switch to the **All** tab (Recommended is a subset).
3. **Expand All** or search by tag (e.g. `321-VF01`).
4. Check a device checkbox — that **places** it on the canvas immediately.
   Unchecking removes it.
5. Close the drawer when done adding; then position.

Equipment tags in the drawer are the source of truth. SCADA OCR is unreliable —
validate tags in All before planning a batch.

## Positioning nodes (required method)

Do **not** drag with the mouse as the primary method. Use React Flow's
`onNodesChange` via CDP `Runtime.evaluate`.

### Locate the handler

```js
(() => {
  const pane = document.querySelector(".react-flow");
  const key = Object.keys(pane).find((k) => k.startsWith("__reactFiber$"));
  let f = pane[key];
  const seen = new Set();
  while (f && !seen.has(f)) {
    seen.add(f);
    const props = f.memoizedProps || {};
    if (props.nodes && props.onNodesChange) {
      return { onNodesChange: props.onNodesChange, nodes: props.nodes };
    }
    f = f.return;
  }
  throw new Error("React Flow onNodesChange not found");
})();
```

Map `nodes` by `n.data.displayName` → `n.id`. Positions are **flow coordinates**
(`n.position`), not viewport pixels. Read the viewport only when you need to
correlate with a screenshot:

```js
document.querySelector(".react-flow__viewport")?.getAttribute("style");
// e.g. transform: translate(…) scale(…);
```

### Apply positions

Bare `{ type: 'position', …, dragging: false }` is ignored. Always use the
drag lifecycle pair:

```js
onNodesChange([{ type: "position", id, position: { x, y }, dragging: true }]);
onNodesChange([{ type: "position", id, position: { x, y }, dragging: false }]);
```

Batch every node in the batch this way, then **IMMEDIATELY** verify DOM
transforms match the targets:

```js
[...document.querySelectorAll(".react-flow__node")].map((el) => ({
  name: (el.innerText || "").trim().split(/\n/).pop(),
  style: el.getAttribute("style"), // transform: translate(Xpx, Ypx)
}));
```

If transforms did not update, re-resolve `onNodesChange` from the fiber (stale
closure) and retry once. Only fall back to `browser_drag` if programmatic
updates fail twice.

### Layout conventions

When recreating a SCADA diagram:

- Flow is generally **left → right**, **top → bottom**.
- Place a small validated batch first; arrange; confirm with the user before
  the next band of equipment.
- Leave room for downstream equipment — do not pack the first batch into the
  full canvas width.
- After large moves, **Fit View** only if the user has not set a deliberate zoom
  they want to keep; prefer asking when unsure.

## Typical rebuild loop

1. Identify the next band of devices from the reference image (head of process
   first).
2. Validate every tag exists under **All** (note mismatches like SCADA `P55`
   vs ATLAS `P90`).
3. Present the plan; wait for approval before placing when the user asked for a
   plan-only step.
4. Check boxes to place; position via `onNodesChange`.
5. Screenshot and report what landed — then stop for the next band.

## Hard rules

- Never invent equipment tags that are not in the Add equipment drawer.
- Never Save / Discard / Exit edit mode without an explicit user request.
- Never rely on OCR alone for tags — confirm in the drawer.
- Prefer flow-coordinate placement over drag for all rearrangements.
