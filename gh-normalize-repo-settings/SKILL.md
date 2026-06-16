---
name: gh-normalize-repo-settings
description: Use when normalizing, auditing, or re-applying a GitHub repository's general settings (features, merge/PR policy, web commit signoff) to the CrossnoKaye org-uniform standard using the gh CLI. Triggers on "normalize repo settings", "fix repo settings", "match gaia settings", "audit github settings".
---

# Normalize GitHub Repo General Settings

Brings a repo's **general settings** (Settings → General page, the writable
`repos/{owner}/{repo}` object) into line with the org-uniform policy seeded
from `crossnokaye/gaia`. Dry-run by default; mutates only on `--apply`.

## Scope — what this touches and what it does NOT

**In scope** (the policy keys in `desired-repo-settings.json`, applied in a
single PATCH to the repo object):
- Features: `has_issues`, `has_projects`, `has_wiki`, `has_downloads`,
  `has_discussions`, `allow_forking`
- Merge / PR policy: `allow_squash_merge`, `allow_merge_commit`,
  `allow_rebase_merge`, `allow_auto_merge`, `delete_branch_on_merge`,
  `allow_update_branch`, `use_squash_pr_title_as_default`,
  `squash_merge_commit_title`, `squash_merge_commit_message`
- `web_commit_signoff_required`

**Deliberately out of scope** (never written by this skill):
- Per-repo identity: `name`, `description`, `homepage`, `topics`,
  `visibility`, `default_branch`, `is_template`, `archived`
- Anything on a separate endpoint: **branch protection / rulesets**,
  **security & analysis** (Dependabot, secret scanning, code scanning),
  **Actions permissions**, **autolinks**

Rationale: those are either repo-specific or live behind different APIs with
their own blast radius. Keeping this skill to the single-PATCH repo object
makes every run idempotent and low-risk. To extend scope, see the bottom.

## Prerequisites

- `gh` authenticated with `repo` scope and **admin** on the target repo
  (`gh auth status` to confirm). PATCHing settings needs admin.
- `jq` on PATH.

## Usage

```bash
# Dry run — print drift only (default, safe)
~/.claude/skills/gh-normalize-repo-settings/normalize.sh OWNER/REPO

# Apply — PATCH the drifted keys to match policy
~/.claude/skills/gh-normalize-repo-settings/normalize.sh OWNER/REPO --apply
```

Always run the dry run first, show the user the drift, and get confirmation
before re-running with `--apply`. The apply path PATCHes only the keys that
actually drifted (minimal, auditable call).

## The golden template

`desired-repo-settings.json` is the single source of truth. The script reads
its keys dynamically, so editing that file is how you change policy — never
hardcode keys in the script. Current values reflect gaia's squash-only,
auto-merge, delete-branch-on-merge posture with issues on and
wiki/projects/discussions/forking off.

To re-seed the template from a model repo:
```bash
gh api repos/crossnokaye/gaia --jq '{
  has_issues, has_projects, has_wiki, has_downloads, has_discussions,
  allow_forking, allow_squash_merge, allow_merge_commit, allow_rebase_merge,
  allow_auto_merge, delete_branch_on_merge, allow_update_branch,
  use_squash_pr_title_as_default, squash_merge_commit_title,
  squash_merge_commit_message, web_commit_signoff_required
}' > ~/.claude/skills/gh-normalize-repo-settings/desired-repo-settings.json
```

## Verifying a result

Re-run the dry run; a normalized repo prints
`✓ OWNER/REPO already matches policy`.

## Extending scope later

These adjacent domains are intentionally excluded but documented so you can add
them as separate, opt-in steps if asked:

| Domain | Endpoint | Note |
|---|---|---|
| Branch protection | `PUT repos/{r}/branches/{b}/protection` | Required-check names differ per repo; not org-uniform |
| Rulesets | `GET/POST repos/{r}/rulesets` | gaia uses classic protection, no rulesets |
| Security & analysis | in repo PATCH under `security_and_analysis`; alerts via `PUT/DELETE /vulnerability-alerts` | GHAS features need entitlement on private/internal repos |
| Actions | `PUT repos/{r}/actions/permissions` | gaia: enabled, allowed_actions=all |
| Autolinks | `POST repos/{r}/autolinks` (one per entry) | Org Jira prefixes; no bulk endpoint |
