#!/usr/bin/env python3
"""Convert an instance from `internal-get-site-narrative --view extended`
JSON (PascalCase, on stdin) into an `internal-upsert-narrative-instance`
--body (snake_case, on stdout).

Usage: ck-ecp internal-get-site-narrative ... --view extended \
         | python3 to_upsert_body.py <alias>
"""
import json
import re
import sys

STRIP = {"OrgID", "AgentID", "Version", "CreatedAt", "CreatedBy",
         "UpdatedAt", "UpdatedBy"}
RENAME = {"ID": "narrative_instance_id"}


def snake(name):
    if name in RENAME:
        return RENAME[name]
    # NarrativeTemplateID -> narrative_template_id, ExpressionText -> expression_text
    s = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", "_", name)
    s = re.sub(r"(?<=[A-Z])(?=[A-Z][a-z])", "_", s)
    return s.lower()


def convert(obj, depth=0):
    if isinstance(obj, dict):
        out = {}
        for k, v in obj.items():
            if depth == 0 and k in STRIP:
                continue
            out[snake(k)] = convert(v, depth + 1)
        return out
    if isinstance(obj, list):
        return [convert(v, depth + 1) for v in obj]
    return obj


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    alias = sys.argv[1]
    narrative = json.load(sys.stdin)
    matches = [i for i in narrative.get("NarrativeInstances") or []
               if i.get("Alias") == alias]
    if not matches:
        aliases = sorted(i.get("Alias", "?")
                         for i in narrative.get("NarrativeInstances") or [])
        sys.exit(f"alias {alias!r} not found; narrative has: {aliases}")
    body = convert(matches[0])
    # Alias travels in the --alias flag, not the body.
    body.pop("alias", None)
    # The endpoint rejects bodies without a view field.
    body["view"] = "default"
    # Omitted collections are CLEARED server-side: materialize every member
    # collection explicitly so a null from GET round-trips as [].
    for coll in ("inputs", "settings", "computed_metrics", "conditions",
                 "actions", "virtual_outputs", "alarms", "input_mappings",
                 "output_mappings", "overrides"):
        if body.get(coll) is None:
            body[coll] = []
        for member in body[coll]:
            desc = member.get("description") if isinstance(member, dict) else None
            if desc and len(desc) > 250:
                print(f"WARNING: {coll} member {member.get('name')!r} "
                      f"description is {len(desc)} chars (max 250)",
                      file=sys.stderr)
    desc = body.get("description")
    if desc and len(desc) > 250:
        print(f"WARNING: instance description is {len(desc)} chars (max 250)",
              file=sys.stderr)
    json.dump(body, sys.stdout, indent=1, ensure_ascii=False)
    print()


if __name__ == "__main__":
    main()
