#!/usr/bin/env bash
#
# Normalize a GitHub repo's general settings to the org-uniform policy
# defined in desired-repo-settings.json (the "golden" template).
#
# Touches ONLY the policy keys present in the desired file (features +
# merge/PR behavior + web_commit_signoff). Per-repo identity fields
# (name, description, homepage, topics, visibility, default_branch) and
# everything on separate endpoints (branch protection, security toggles,
# Actions, autolinks) are deliberately left untouched.
#
# Usage:
#   normalize.sh OWNER/REPO            # dry-run: print drift only (default)
#   normalize.sh OWNER/REPO --apply    # PATCH the repo object to match
#
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DESIRED="$SCRIPT_DIR/desired-repo-settings.json"

REPO="${1:-}"
APPLY=false
for arg in "${@:2}"; do
  [[ "$arg" == "--apply" ]] && APPLY=true
done

if [[ -z "$REPO" || "$REPO" == --* ]]; then
  echo "usage: normalize.sh OWNER/REPO [--apply]" >&2
  exit 2
fi
if [[ ! -f "$DESIRED" ]]; then
  echo "error: desired file not found: $DESIRED" >&2
  exit 1
fi

# Snapshot current repo object once.
current="$(gh api "repos/$REPO")"

# Compute drift: for each desired key, compare against current.
drift="$(jq -n \
  --slurpfile d "$DESIRED" \
  --argjson c "$current" '
    $d[0] | to_entries
    | map({key: .key, desired: .value, current: ($c[.key])})
    | map(select(.desired != .current))
  ')"

count="$(jq 'length' <<<"$drift")"

if [[ "$count" -eq 0 ]]; then
  echo "✓ $REPO already matches policy ($(jq 'keys|length' "$DESIRED") keys checked)."
  exit 0
fi

echo "Drift on $REPO ($count of $(jq 'keys|length' "$DESIRED") keys):"
jq -r '.[] | "  \(.key): \(.current) → \(.desired)"' <<<"$drift"

if [[ "$APPLY" != true ]]; then
  echo
  echo "Dry run. Re-run with --apply to PATCH these keys."
  exit 0
fi

echo
echo "Applying…"
# Patch only the drifted keys so the API call is minimal and auditable.
patch_body="$(jq 'map({(.key): .desired}) | add' <<<"$drift")"
echo "$patch_body" | gh api --method PATCH "repos/$REPO" --input - >/dev/null
echo "✓ Applied $count change(s) to $REPO."
