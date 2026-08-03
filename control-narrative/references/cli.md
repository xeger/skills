# ck-ecp cookbook

`ck-ecp` wraps the Goa-generated CLI for the `front` service (source:
`~/Code/crossnokaye/tools/ck-ecp/`). Endpoints are flat:
`ck-ecp <endpoint> [flags]`. Body endpoints take `--body` with raw JSON.
`--help` on any endpoint is always safe (token fetch is skipped) and prints
an example body — but the example values are Goa-generated gibberish; treat
it as a field-name inventory only. `--debug` traces HTTP requests/responses.

**Any non-help invocation authenticates and executes immediately.** There is
no dry-run and no confirmation. Read/write endpoint names differ by one word
(`internal-get-draft-…` vs `internal-delete-draft-…`) — read your command
back before running it.

**Failure output is huge.** On any client-side validation error the CLI
prints a one-line error and then a multi-kilobyte usage dump listing every
endpoint — only the first line matters. Contain it: run body-bearing writes
as `… > "$SCRATCH/out.json" 2>&1 || true; head -3 "$SCRATCH/out.json"`, and
inspect the rest of the file only on failure. Better still, avoid the errors:
use the exact body templates below (the common trap is the undocumented
required `"view": "default"` field, and the 250-char cap on every
`description` — see instance-schema.md).

## Environment & auth

Env comes from `ATLAS_ENV` (or `ACCOUNT_NAME`); **unset defaults to
production**: production→atlaslive.io, office→atlasoffice.io,
sandbox→atlassandbox.io, janeway→atlasjaneway.io. Auth uses per-env refresh
tokens in `~/.config/atlas/config.toml` (or `ATLAS_ACCESS_TOKEN[_<ENV>]`).
Verify with `ck-ecp config test`; `invalid grant` means that env's refresh
token is expired — tell the user, don't improvise. Internal endpoints need
the `internal_app_admin` role.

Prefer `env ATLAS_ENV=<env> ck-ecp …` on every command so the target
environment is visible in the command itself.

## ID resolution (URL → flags)

Narrative endpoints take a UUID triple:

- `--internal-org-id` — **your own (CrossnoKaye) org's UUID** in that env, an
  authorization scope. Using the customer org here yields
  `insufficient privileges`.
- `--org-id` — the customer org that owns the facility.
- `--agent-id` — the facility's agent.

Recipe (user id = `https://crossnokaye.com/principal` claim in the JWT, or
ask the user):

    ck-ecp list-user-orgs --user-id <uuid>          # find your org (Name: crossnokaye) and the customer org
    ck-ecp list-user-facilities --user-id <uuid>    # take OrganizationID + Agents[].AgentID

Facilities can be named several ways; resolve whatever the user gives you
against the `list-user-facilities` output:

- **Facility short name** (`jolietsouth`) — exact match on `ShortName`.
- **Display name** ("Joliet South Lineage") — case-insensitive substring
  match on `DisplayName`; if several match, list them and ask.
- **`orgShortName-agentShortName`** (common in chats, e.g.
  `lineage-jolietsouth`) — do NOT naively split on the hyphen: facility
  short names may themselves contain hyphens (`salemhenningsenct-2`). First
  try the whole token as a `ShortName`; failing that, for each org `Name`
  from `list-user-orgs`, if the token starts with `<orgName>-`, strip that
  prefix and match the remainder against `ShortName`s of facilities whose
  `OrganizationID` belongs to that org.
- **atlaslive URL** `https://atlaslive.io/f/<slug>/facility-config/
  narratives/<version>/instances/<alias>/…` — the slug resolves like the
  combined notation above, and the path also gives the narrative version and
  instance alias.

If nothing matches, show the near-misses and ask — never guess a facility.
Confirm the resolved facility (`DisplayName`, `ShortName`, env) back to the
user before any write.

Known CLI wart: `list-user-facilities --view extended` fails client-side
validation (`sheet_id` length) — use the default view.

## Reading narratives

    env ATLAS_ENV=<env> ck-ecp internal-list-site-narratives \
      --internal-org-id <iod> --org-id <org> --agent-id <agent> \
      --include-draft true --count 5

Newest first. Per version: `Version` (semver; drafts look like
`N.0.0-draft`, `IsDraft: true`), `IsActive`, `IsLatest`, `ParentVersion`,
`DeployedAt` (**null = published but never deployed** — the authorization
ladder cares), `BlueprintVersion` (an integer — the device-blueprint version
this narrative binds to; create-draft and `list-devices` need it),
`Description`, created/updated audit fields.

    env ATLAS_ENV=<env> ck-ecp internal-get-site-narrative \
      --internal-org-id <iod> --org-id <org> --agent-id <agent> \
      --version <version> --view extended

- `--version` is REQUIRED in practice: the CLI's flag default is the literal
  string `REQUIRED`, which fails semver validation despite help text
  promising "active version if blank". Always pass one.
- **`--view extended` is required to see `NarrativeInstances` at all** — the
  default view returns the version envelope with an empty instance list.
- Output can exceed 1 MB on busy sites (one office site: 168 instances,
  1.2 MB). **GET once into a scratch file, then filter locally** — never pull
  the full JSON into context, and never re-GET what a saved file already
  answers (re-GET only after a write, per SKILL.md rail 3):

      … --view extended > "$SCRATCH/narrative_<version>.json"
      jq '.NarrativeInstances[] | select(.Alias == "<alias>")' "$SCRATCH/narrative_<version>.json"

Responses use PascalCase keys (`ComputedMetrics`, `ExpressionText`); see
`instance-schema.md` for the shape and the snake_case mapping upsert needs.

Known wart: a draft's version string from the list (`16.0.0-draft`) is
REJECTED by `internal-get-site-narrative --version` with `site narrative
version 16.0.0-draft not found`, even though the list returns it. If you need
the draft body and this fails, stop and report — do not report on the parent
version as though it were the draft.

## Merging template members (do this before reporting)

**An instance body shows only its CUSTOM members.** Template-defined members
— often the interesting ones, like a `resetDailyCounters` condition every
other instance maps to — never appear in the instance JSON at any view.
`"Conditions": null` on an instance means "no custom conditions", not "no
conditions". The web UI renders the difference ("Template Defined
Conditions", padlocked, above the custom ones); the API leaves you to
reconstruct it. Per SKILL.md rail 6, merge before you report:

    jq -r '[.NarrativeInstances[].NarrativeTemplateID] | unique[]' "$SCRATCH/narrative_<version>.json"
    # then, once per distinct ID:
    env ATLAS_ENV=<env> ck-ecp internal-get-narrative-template \
      --internal-org-id <iod> --org-id <org> \
      --id <templateID> > "$SCRATCH/tmpl_<id>.json"

Take the `NarrativeTemplateID` from **each instance's own body** — never
assume one template covers the site.
Sibling instances sharing a naming convention routinely sit on different
templates — at one quarry, ten `*_performance` instances were on
`generic_calculator` (a deliberately empty template) while the lone
`*_global_constants` instance was on `global_constant`, which carried all
the shared conditions. Assuming one template for the site hides exactly the
instance you were asked about.

Two gotchas on `internal-get-narrative-template`: it needs BOTH
`--internal-org-id` and `--org-id` (omitting either yields the
`must be formatted as a uuid but got value "REQUIRED"` error plus the usage
dump), and its `--id` is the `NarrativeTemplateID` from the instance, not an
alias.

Also: `internal-list-narrative-references` RESOLVES references. If a member
name appears there as a key with consumers listed, that member exists —
template-defined if the instance body lacks it. A hit is proof of presence,
never evidence of a dangling reference.

Other reads: `internal-list-narrative-templates --internal-org-id --org-id`
(returns `values[]` with `Alias`, `DisplayName`, `Version`, `ID`, member
collections, `Overridables`); `internal-get-narrative-template
--internal-org-id --org-id --id` (see Merging template members above);
`internal-list-site-narrative-instance-mapping-options` (the API behind the
UI's mapping dropdowns; filter by `--mapping-kind input`, `--mapping-type`,
`--mapping-units`); `internal-list-narrative-references` (who references an
instance's members — check before renames);
`internal-list-expression-functions`; `list-units`;
`internal-list-orphaned-i-o`; `diff-site-narrative-versions`;
`internal-list-deployments` / `internal-get-current-deployment`.

## Device discovery & topology

When a request is phrased in terms of devices ("every pile", "the stacker
that feeds X") rather than instance aliases, resolve devices first:

    env ATLAS_ENV=<env> ck-ecp list-devices \
      --org-id <org> --agent-id <agent> --version <BlueprintVersion> \
      > "$SCRATCH/devices.json"

`--version` is the integer `BlueprintVersion` from the site-narrative
envelope (no `--internal-org-id` on this endpoint). Returns `values[]` with
`ID`, `Alias`, `Name`, `Kind` (device type — filter on this), `Upstream[]` /
`Downstream[]` (lists of `{DeviceID}` — join through `ID` to walk the
material-flow topology), and `Properties`. Tie devices to instances through
the instance's `DeviceAlias`. A device with no matching instance has no
narrative yet — creating one is a change-list item, not something to skip
silently.

## Writing (see instance-schema.md first)

- `internal-create-draft-site-narrative --version <base>` — idempotent:
  returns the existing draft if one exists. One draft per site. Base must be
  the active or latest version (`0.0.0` for a site's first narrative). The
  body requires more than the help suggests — use exactly this shape:

      --body '{"blueprint_version": <BlueprintVersion of base version>,
               "description": "<user-visible summary of the change>",
               "is_draft_blueprint": false, "view": "default"}'

  Omitting `view` fails with `value of body.view must be one of "default",
  "extended" but got value ""` (plus the usage dump).
- `internal-upsert-narrative-instance --alias <alias>
  --site-narrative-version <draft-version> --body <json>` — creates or
  replaces an instance. FULL REPLACE: round-trip per SKILL.md rail 2.
- `internal-append-narrative-instances` / `internal-remove-narrative-instances`
  — attach/detach instances (by `narrative_instance_ids`) to a version.
  After upserting a NEW instance, list the draft again to confirm it is
  attached; append explicitly if not.
- `internal-validate-draft-site-narrative --version <draft>` — returns the
  error list. This is the only type-check; run it after every write batch.
- `internal-publish-draft-site-narrative` — validates and creates a new
  version number. `internal-deploy-site-narrative --version <v>` — pushes a
  version to the live facility. Separate endpoints, separate explicit
  authorizations (SKILL.md rail 4).
- `internal-reset-draft-site-narrative` / `internal-delete-draft-site-narrative`
  — destructive; user consent required.

## State-report grammar

Present instance state to the user in this shape, rendered from the JSON:

    INSTANCE: <alias>  (template: <template DisplayName>, device: <DeviceAlias>)
      INPUTS
        <Name> | <type> | <unit or -> | mapping: <point alias or source.construct or -> | <custom|template>
      SETTINGS
        <Name> | <type> | <unit or -> | default: <value> | <normal|one_shot if bool> | <custom|template>
      COMPUTED_METRICS
        <Name> | <type> | <unit or -> | expr: <VERBATIM ExpressionText> | <custom|template>
      CONDITIONS / ACTIONS / VIRTUAL_OUTPUTS / ALARMS / OVERRIDES
        <same idea, or: (empty)>

Rules: expressions VERBATIM — exact spacing, capitalization, parentheses;
member names exactly as stored (flag convention violations in a NOTES block,
never silently correct); `-` for absent values.

The `<custom|template>` tag is REQUIRED on every line, which means you cannot
render this grammar at all from an unmerged read — that is the point. Report
a collection as `(empty)` only after the template merge shows it empty on
BOTH sides; "empty" is a finding, and a false one is worse than none. Before
`(empty)` reaches the user, ask: did I fetch THIS instance's template, or a
sibling's? If the merge is impossible (template fetch fails), say
"instance-level only, template unresolved" rather than "(empty)".
