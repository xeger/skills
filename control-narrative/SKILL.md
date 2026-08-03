---
name: control-narrative
description: Work with ATLAS narrative instances (L1 control narratives) via the ck-ecp CLI — inspecting, designing, creating, modifying, renaming, or reviewing instances and their inputs, settings, metrics, conditions, actions, outputs, or alarms; managing draft site-narrative versions; validating, diffing, publishing, or deploying them. Use whenever a request mentions a narrative instance, a member of one, a site narrative version or draft, or an atlaslive.io facility-config URL. All work happens through ck-ecp; there is no browser flow.
---

# Control Narrative (ck-ecp)

A narrative instance is a per-device L1 program evaluated at ~1 Hz by the ATLAS
agent at a facility. All of its state lives in versioned **site narratives**
reachable through the `ck-ecp` CLI. Design, change-lists, writes, and
verification happen in the root context; bulk reading should usually be
delegated (see Delegation below). There is no browser flow — if the API
cannot do something the user asked for, stop and report; never fall back to
the UI.

Read `references/cli.md` before running commands, `references/expressions.md`
before composing or reviewing any member content, and
`references/instance-schema.md` before any write.

## Safety rails (read first)

1. **Environment check first.** Before the first real command of a session run
   `ck-ecp config test` and state which environment is active (`ATLAS_ENV` /
   `ACCOUNT_NAME`; **unset means production, atlaslive.io**). The CLI has no
   dry-run and no confirmation prompt — the change-list you show the user IS
   the confirmation, and it must name the environment. In the same breath,
   state which model YOU are: **write tasks require an Opus-class model or
   better**. On anything smaller (Sonnet, Haiku), read and design freely but
   stop before the first mutating command and tell the user to re-run the
   write on a stronger model.
2. **Round-trip rule.** `internal-upsert-narrative-instance` is a full
   replace, not a patch. Its own help text warns: *"If mappings of any of the
   inputs, settings, computed metrics, conditions, virtual outputs or actions
   are missing or set to empty then the narrative instance will be updated to
   set corresponding fields to empty."* Always: GET the draft narrative,
   extract the target instance's complete body, apply only the change-list
   edits, send the entire body back. Never send a partial body; never
   hand-construct a body for an existing instance.
3. **Read-back verification.** After every write, GET again and diff: edited
   fields show their NEW values, everything under DO NOT TOUCH is unchanged,
   and no member collection shrank (compare per-collection counts — a shrink
   means the round-trip dropped something). Report final expression text from
   the read-back, not from what you sent.
4. **Authorization ladder.** Validate is safe and expected. **Publish and
   deploy each require the user's explicit words in this conversation,
   separately.** Silence is not authorization, and neither is a validated
   draft, a successful publish, or your own judgment that the change is
   ready. An uninstructed deployment to a live facility is the single worst
   outcome of this role. The authorization must come AFTER the user has seen
   the final change-list — a blanket "go ahead and publish" from before the
   work does not count. Before publishing, list earlier
   published-but-never-deployed versions (`DeployedAt: null`) and tell the
   user what a deploy would carry beyond this change; if there are any, get
   their acknowledgment before proceeding.
5. **Draft awareness.** Writes target the draft version only. Reads that
   inform a write must target the draft explicitly (`--include-draft true` on
   list; the draft's version string on get — the CLI requires an explicit
   `--version`). Creating, resetting, or deleting a draft is a user-visible
   act that needs the user's consent, even though create is idempotent.
6. **The instance JSON is not the whole instance.** Instance-level
   collections carry ONLY custom members; everything else lives on the
   narrative template and is invisible in the instance body. A collection
   that reads `null`/`[]` therefore means "no custom members here", NEVER
   "this instance has no conditions". Before reporting on, designing
   against, or calling anything missing, resolve each instance's OWN
   template and merge (recipe in `references/cli.md`): instances that look
   alike routinely sit on different templates, and the odd one out is
   usually the interesting one. A name that resolves in
   `internal-list-narrative-references` but has no instance-level definition
   is template-defined, not dangling — that endpoint resolves references, so
   a hit there is evidence the member EXISTS. The UI shows this provenance
   ("Template Defined Conditions", with a lock); the API does not, so you
   must reconstruct it. Never report a member as missing, dangling, or
   unresolved on the strength of the instance body alone.
7. **Stop, don't guess.** If current state does not match the change-list's
   OLD values (member missing, capitalization differs, expression text
   differs), if an endpoint errors unexpectedly, or if the API lacks a needed
   capability — stop and report precisely what was and was not done. A
   stopped run is a success; a guessed edit to a live control narrative is
   not. Never write from remembered or assumed state; if you have not read it
   this session since the last write, read it again.

## Delegation

Root context is for judgment — keep it semantically dense. Delegate bulk
reading to parallel subagents on a cheap model (`model: haiku`, or `sonnet`
for anything needing interpretation): surveying the instances of a large
narrative in slices, mapping device topology from the blueprint, gathering
mapping options or cross-narrative references, comparing resource sets
across blueprint and narrative. Give each subagent a narrow, non-overlapping
slice; tell it exactly which ck-ecp reads to run, always including the
template fetch-and-merge (rail 6) — without it the subagent cannot tag
members `custom` vs `template`. Require its report in the state-report
grammar from `references/cli.md` — expressions VERBATIM, empty collections
reported, `-` for absent values — so the relay loses nothing you'd need for
design. What comes back replaces, not accompanies,
the raw JSON in your context.

Two hard limits:

- **Never write from subagent-reported state.** Subagent reports are a map
  for design. Before any upsert, the root context re-reads the target
  instance itself (rail 7) and builds the round-trip body from that read.
- Change-list composition, user confirmation, writes, and read-back
  verification never delegate.

## Workflow

1. **Orient.** Resolve `--internal-org-id` (your own org's UUID), `--org-id`
   (the customer org), and `--agent-id` from the user's words or an
   atlaslive.io URL, per the recipe in `references/cli.md`. Harvest version
   and instance alias from the URL path when present
   (`…/narratives/<version>/instances/<alias>/…`). Then the env check.
2. **Read.** `internal-list-site-narratives --include-draft true` for
   versions, draft existence, active/latest flags. Then
   `internal-get-site-narrative --view extended`, saved once to a scratch
   file and filtered locally with jq/python (big sites exceed a megabyte;
   never re-fetch what the file answers, but always re-fetch after a write).
   On big sites or multi-resource surveys, fan the reading out to cheap
   parallel subagents per the Delegation section.
   If the request is phrased in terms of devices ("every pile") rather than
   instance aliases, resolve them first via `list-devices` (recipe in
   `references/cli.md`).
   **Then resolve templates before reporting anything** (rail 6): collect the
   distinct `NarrativeTemplateID`s across the instances in scope, fetch each
   once with `internal-get-narrative-template`, and merge template members
   with instance members so every collection is complete. This is not
   optional and not "as needed" — an unmerged read is unreportable, because
   its empty collections are indistinguishable from genuinely empty ones.
   Present the merged state in the state-report grammar from
   `references/cli.md`, tagging every member `custom` or `template`.
   Supporting reads as needed: mapping options,
   `internal-list-expression-functions`, `list-units`,
   `internal-list-narrative-references`.
3. **Design.** Apply `references/expressions.md`. Compose the change-list in
   the format below, then run the proof checklist against it yourself.
4. **Confirm.** For any non-trivial change — new members, expression edits,
   renames, new instances, anything touching an instance the user did not
   name — show the change-list and the target environment and wait for
   approval. A trivial single-field edit the user dictated verbatim may
   proceed once you have stated it.
5. **Write.** Ensure the draft exists (create only with consent). Round-trip
   upsert per instance, per rail 2 and `references/instance-schema.md`.
6. **Verify.** Read-back diff (rail 3), then
   `internal-validate-draft-site-narrative`. Optionally
   `diff-site-narrative-versions` for a human-readable draft-vs-published
   summary.
7. **Report.** What changed (one line per edit), verbatim final text of every
   touched expression as read back, per-upsert outcomes, the validate result,
   anything stopped and why — and end by stating that nothing was published
   or deployed (or, if explicitly authorized and done, the new version number
   and deployment confirmation).

## Change-list format

Compose changes in this grammar before writing anything:

    INSTANCE: <alias>
      COLLECTION: <inputs|settings|computed_metrics|conditions|actions|virtual_outputs|alarms|input_mappings|output_mappings|overrides>
        <Member> . <field> : <old value> -> <new value>
      COLLECTION: computed_metrics
        <Member> . expression_text :
          OLD: <verbatim>
          NEW: <verbatim>
    DO NOT TOUCH: <members, collections, instances left alone>
    VALIDATE: yes
    PUBLISH: no

For new members give every field: name, type (`number|bool|enum|schedule|
sequence`), unit (by ShortName — `A`, `ton/h`, `none`), description (**250
characters max** — the API rejects longer), default,
mapping, expression, and for Boolean settings the
`bool_setting_kind` (`normal` or `one_shot`). State final expression text
verbatim, character for character, preserving spacing and parenthesization the
change does not affect.

Follow with a short RATIONALE block covering only decisions the user must
proof: unit choice, setting-vs-literal, a dependency they did not mention. If
the user's intent conflicts with the conventions in
`references/expressions.md`, follow the user and note the conflict — their
call, not yours.

## Proof checklist

Run this against the change-list before anything mutates:

- Any member the user did not ask to touch?
- Every rename traced into EVERY expression that references the old name —
  including the member's own expression when it self-references
  (accumulators)? Cross-instance references too: other instances can consume
  this instance's conditions, metrics, and outputs via their input mappings
  (check `internal-list-narrative-references`).
- A unit on every `number` member (`none` for dimensionless)?
- Anything you inferred rather than were told?
- Re-read the list as a literal-minded executor: any step that requires an
  inference is a defect — resolve it now.
