# Contributing

`main` contains integrated work. Use one short-lived branch and one pull request
for each feature, fix, or maintenance task. Split unrelated changes into separate
pull requests; keep the implementation, tests, and documentation for the same
change together.

## Branch names

| Prefix | Purpose | Example |
|---|---|---|
| `feature/` | A new capability | `feature/pdf-ocr` |
| `fix/` | A focused bug fix | `fix/date-validation` |
| `docs/` | Documentation only | `docs/local-model-setup` |
| `chore/` | Build, CI, or repository maintenance | `chore/branch-workflow` |

Use lowercase words separated by hyphens. Create a branch when starting work;
do not keep empty branches for future features.

## Workflow

1. Update local `main` with `git pull --ff-only`.
2. Create a branch from `main` with a name describing the single change.
3. Make focused commits and run checks appropriate to the change.
4. Open a pull request targeting `main`. Describe the behavior changed, validation,
   and any remaining limitations.
5. Review the diff and wait for both Python CI jobs to pass before merging.
6. Merge the pull request. GitHub automatically deletes its completed branch.
7. Return to `main`, pull the merged changes, then remove the local branch with
   `git branch -d <branch>` and refresh remote references with `git fetch --prune`.

CI runs for pull requests targeting `main` and again after changes land on
`main`. This avoids running the same checks twice for each feature-branch push.
These are contribution conventions, not enforced branch protection rules.

Keep published history intact. Use a new pull request for follow-up changes,
and release tags for versioned snapshots. Never commit real CVs, credentials,
private registration details, or generated private reports.
