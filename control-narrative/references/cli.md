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
    ck-ecp list-user-facilities --user-id <uuid>    # match ShortName to the URL slug; take OrganizationID + Agents[].AgentID

An atlaslive URL `https://atlaslive.io/f/<slug>/facility-config/narratives/
<version>/instances/<alias>/…` gives the facility slug (matches
`ShortName`), the narrative version, and the instance alias.

Known CLI wart: `list-user-facilities --view extended` fails client-side
validation (`sheet_id` length) — use the default view.

## Reading narratives

    env ATLAS_ENV=<env> ck-ecp internal-list-site-narratives \
      --internal-org-id <iod> --org-id <org> --agent-id <agent> \
      --include-draft true --count 5

Newest first. Per version: `Version` (semver; drafts look like
`N.0.0-draft`, `IsDraft: true`), `IsActive`, `IsLatest`, `ParentVersion`,
`DeployedAt` (**null = published but never deployed** — the authorization
ladder cares), `Description`, created/updated audit fields.

    env ATLAS_ENV=<env> ck-ecp internal-get-site-narrative \
      --internal-org-id <iod> --org-id <org> --agent-id <agent> \
      --version <version> --view extended

- `--version` is REQUIRED in practice: the CLI's flag default is the literal
  string `REQUIRED`, which fails semver validation despite help text
  promising "active version if blank". Always pass one.
- **`--view extended` is required to see `NarrativeInstances` at all** — the
  default view returns the version envelope with an empty instance list.
- Output can exceed 1 MB on busy sites (one office site: 168 instances,
  1.2 MB). Always filter, e.g.:

      … --view extended | jq '.NarrativeInstances[] | select(.Alias == "<alias>")'

Responses use PascalCase keys (`ComputedMetrics`, `ExpressionText`); see
`instance-schema.md` for the shape and the snake_case mapping upsert needs.

Other reads: `internal-list-narrative-templates --internal-org-id --org-id`
(returns `values[]` with `Alias`, `DisplayName`, `Version`, `ID`, member
collections, `Overridables`); `internal-get-narrative-template --id`;
`internal-list-site-narrative-instance-mapping-options` (the API behind the
UI's mapping dropdowns; filter by `--mapping-kind input`, `--mapping-type`,
`--mapping-units`); `internal-list-narrative-references` (who references an
instance's members — check before renames);
`internal-list-expression-functions`; `list-units`;
`internal-list-orphaned-i-o`; `diff-site-narrative-versions`;
`internal-list-deployments` / `internal-get-current-deployment`.

## Writing (see instance-schema.md first)

- `internal-create-draft-site-narrative --version <base>` — idempotent:
  returns the existing draft if one exists. One draft per site. Base must be
  the active or latest version (`0.0.0` for a site's first narrative). Give
  the body a meaningful `description`; it is user-visible.
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
never silently correct); `-` for absent values; report empty collections
explicitly — "empty" is a finding. Instance-level collections hold only
custom members; template-defined members come from the template (fetch it
via `NarrativeTemplateID` when the user needs the full picture).
