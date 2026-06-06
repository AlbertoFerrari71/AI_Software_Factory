# 72 - ASF Git Line Endings Warning Cleanup

## 1. Scope

STEP 548 documents and mitigates Git LF/CRLF conversion warnings in the AI Software Factory repository.

The known warning was:

```text
warning: in the working copy of 'templates/test_plans/test_plan_template.md', LF will be replaced by CRLF the next time Git touches it
```

This cleanup is local-first and conservative. It does not change global Git configuration, does not normalize the whole repository, and does not commit, push, open PRs, merge or deploy.

---

## 2. Initial Diagnosis

Observed during STEP 548:

```text
core.autocrlf: file:C:/Users/alberto.ferrari/.gitconfig false
core.eol: unset
.gitattributes: tracked and present
initial .gitattributes rule: * text=auto
```

The target file reported:

```text
i/lf    w/lf    attr/text=auto         templates/test_plans/test_plan_template.md
templates/test_plans/test_plan_template.md: text: auto
```

The repository also had a mixed working-tree snapshot:

```text
197 files: i/lf, w/crlf, attr/text=auto
65 files:  i/lf, w/lf,   attr/text=auto
```

That means repository content was already normalized to LF in the index, but many working-tree files were still checked out with CRLF because the previous `.gitattributes` rule did not force a working-tree EOL for source and documentation files.

---

## 3. Why The Warning Appeared

Git line-ending warnings appear when the file in the working tree and the normalized content Git would store or later check out do not match the active line-ending policy.

With only:

```gitattributes
* text=auto
```

Git auto-detects text and normalizes content in the index, but the working-tree EOL can still depend on the checkout history and local configuration. On Windows this can leave a mix of LF and CRLF working-tree files.

The warning was not a test failure by itself. It was a signal that Git expected a future touch of the file to change line endings.

---

## 4. Correction Applied

STEP 548 keeps the repository-level policy in `.gitattributes` and does not change user-global Git settings.

The policy now:

- keeps generic text auto-detection;
- forces Markdown, Python, YAML, JSON, TOML, TXT and similar project text files to LF;
- explicitly pins `templates/test_plans/test_plan_template.md` to LF;
- keeps Windows command scripts `.bat`, `.cmd` and `.ps1` as CRLF in the working tree.

This is intentionally narrower than a blind repository-wide renormalization. It gives future edits deterministic EOL rules without rewriting all tracked files in this step.

---

## 5. Normalization Scope

No broad normalization was executed.

The target file `templates/test_plans/test_plan_template.md` already reported `i/lf w/lf` during the initial diagnosis. A filtered hash check after the `.gitattributes` update matched the object in `HEAD`, so no content normalization was needed for that file.

The broad diagnostic command:

```powershell
git add --renormalize --dry-run .
```

reported 262 candidate files. That exceeds the 10-file manual-review threshold, so broad renormalization was intentionally not executed.

If a future check suggests renormalization, measure first:

```powershell
git add --renormalize --dry-run -- templates/test_plans/test_plan_template.md
git add --renormalize --dry-run .
```

Only the first command is acceptable as a normal STEP 548-style correction. The second command is diagnostic only. If it reports more than 10 files, stop and ask for manual review before changing anything.

Do not run this blindly:

```powershell
git add --renormalize .
```

---

## 6. Why Earlier LF/CRLF Warnings Were Non-Blocking

In ASF workflow reports, LF/CRLF warnings are controlled warnings, not automatic failures, when all of these pass:

- `git --no-pager diff --check`;
- `python -m pytest`;
- `python scripts/check_workflow_health.py`;
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\verify.ps1`.

The reason is practical: a line-ending warning can be emitted while Git still returns exit code 0 and no whitespace error exists. The warning must be reported, but it should not be confused with a failed test or failed verification gate.

---

## 7. Future Regression Guardrails

When a future step touches source, docs or templates:

1. Use repository `.gitattributes`, not global `core.autocrlf`, for project policy.
2. Check the target file with:

```powershell
git --no-pager ls-files --eol -- templates/test_plans/test_plan_template.md
git --no-pager check-attr -a -- templates/test_plans/test_plan_template.md
```

3. Prefer targeted dry-run checks before any normalization.
4. Keep broad renormalization out of implementation steps unless Alberto explicitly approves it after the impact is measured.
5. Report residual warnings separately from real test or gate failures.

---

## 8. Verification Commands

Recommended local checks after any future line-ending policy change:

```powershell
git --no-pager diff --check
git --no-pager diff --stat
git --no-pager ls-files --eol -- templates/test_plans/test_plan_template.md
git --no-pager check-attr -a -- templates/test_plans/test_plan_template.md
git add --dry-run -- templates/test_plans/test_plan_template.md
python -m pytest
python scripts/check_workflow_health.py
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\verify.ps1
```
