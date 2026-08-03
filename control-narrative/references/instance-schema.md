# Instance schema & the upsert round-trip

Read this before any `internal-upsert-narrative-instance`. The GET response
and the upsert body describe the same object in different casings: GET
returns Go-style PascalCase (`ComputedMetrics`, `ExpressionText`), the body
wants snake_case (`computed_metrics`, `expression_text`).

## The hazard, verbatim

From the endpoint's own help: *"If mappings of any of the inputs, settings,
computed metrics, conditions, virtual outputs or actions are missing or set
to empty then the narrative instance will be updated to set corresponding
fields to empty."* An omitted collection is a CLEARED collection. Always
send the complete instance.

## Body shape (top level)

    {
      "view":                  "default",   <- REQUIRED; omitting it fails
      "narrative_template_id": <GET .NarrativeTemplateID>,
      "narrative_instance_id": <GET .ID>,
      "device_alias":          <GET .DeviceAlias>,
      "description":           <GET .Description>,
      "wildcard":              <GET .Wildcard>,
      "inputs": [...], "settings": [...], "computed_metrics": [...],
      "conditions": [...], "actions": [...], "virtual_outputs": [...],
      "alarms": [...], "input_mappings": [...], "output_mappings": [...],
      "overrides": [...]
    }

**Every `description` — instance-level and member-level — is capped at 250
characters** (client-side validation; the error names the field and comes
with the full usage dump). Write descriptions to fit from the start; put
longer rationale in the draft's `description` or the report to the user, not
in the member. `scripts/to_upsert_body.py` warns on over-length descriptions
and sets `view` for you.

Strip from the GET object: `OrgID`, `AgentID`, `Version`, `CreatedAt`,
`CreatedBy`, `UpdatedAt`, `UpdatedBy` (they are path flags or audit fields).
The instance identity goes in the flags: `--alias`, `--site-narrative-version`
(the draft version), plus the usual org/agent triple.

Use `scripts/to_upsert_body.py` to do the conversion mechanically:

    ck-ecp internal-get-site-narrative … --view extended \
      | python3 scripts/to_upsert_body.py <alias> > body.json
    # edit body.json per the change-list, then:
    env ATLAS_ENV=<env> ck-ecp internal-upsert-narrative-instance \
      --internal-org-id <iod> --org-id <org> --agent-id <agent> \
      --site-narrative-version <draft-version> --alias <alias> \
      --body "$(cat body.json)"

## Member shapes (as stored; real values, lowercase types)

Types are lowercase: `number`, `bool`, `enum`, `schedule`, `sequence`.
Units are ShortName strings from `list-units` (`°F`, `psig`, `%`, `sec`,
`hr`, `count`, `none`, `ton`, `ton/h`).

- **input**: `{name, description, type, unit, validations{…}}`
- **setting**: input fields plus `default` (a JSON-encoded string: `"0.1"`,
  `"true"`), `overridable` (bool), `annotations`. A `bool` setting carries
  `annotations: {"bool_setting_kind": "normal" | "one_shot"}` — this is how
  the UI's Normal/One Shot dropdown is stored.
- **computed_metric**: `{name, description, type, unit, validations,
  expression_text}`. An `enum` metric lists its values in
  `validations.enum` and its expression yields string literals.
- **condition**: `{name, description, expression_text}` (boolean-valued).
- **virtual_output**: `{name, description, type, unit, validations,
  expressions: {<state>: "<expr>", …}}` — note `expressions` (a map), not
  `expression_text`.
- **action**: `{name, description, expression_texts[], expressions{…}}` —
  state-machine transition triggers.
- **alarm**: `{name, alarm_name, description, control_point, group_name,
  severity, message_template, activation_condition, deactivation_condition,
  tags{…}}`.
- **validations** (all member kinds): `{min_value, max_value, min_length,
  max_length, enum[], pattern, sequence_items[], expected_output_mapping}` —
  null/absent when unused.

## Mappings

- **input_mappings[]**: `{input_name, kind, source_name, …}` where `kind` is
  one of `control_point_alias` (device I/O; also set
  `control_point_alias`, `source_name: "OAS"`), or `condition_name` /
  `computed_metric_name` / `setting_name` / `output_name` (consume another
  instance's construct; set the matching `*_name` field and `source_name` to
  the source instance's alias). Discover candidates with
  `internal-list-site-narrative-instance-mapping-options` — number members
  map to analog points, bool members to digital points.
- **output_mappings[]**: `{control_point_alias, kind, narrative_construct,
  state_based_expression}` with `kind: "narrative_construct"` (drive a point
  from a construct: `narrative_construct.kind` one of `condition_name` /
  `computed_metric_name` / `output_name` with the matching
  `output_mapping_*` field) or `kind: "state_based_expression"`
  (`{state, expression_text}`).
- **overrides[]**: `{kind: "<member>_override", <member>_override: {name, …}}`
  — per-member override of a TEMPLATE-defined member, allowed only where the
  template declares a matching entry in its `Overridables`. Non-null fields
  override; null fields inherit the template.

## Round-trip checklist

1. GET the draft (`--view extended`), extract the instance, convert to the
   body (script above).
2. Confirm every OLD value in the change-list against this body — mismatch
   ⇒ stop (SKILL.md rail 7).
3. Apply ONLY the change-list edits.
4. Upsert; then GET again and diff: NEW values present, DO NOT TOUCH
   unchanged, per-collection member counts did not shrink.
5. For a NEW instance: build the body from scratch (template id from
   `internal-list-narrative-templates`), upsert, then confirm the instance
   is attached to the draft (list it); `internal-append-narrative-instances`
   with the returned instance id if not.
6. `internal-validate-draft-site-narrative` — upsert does not type-check
   expressions; only validate does.
