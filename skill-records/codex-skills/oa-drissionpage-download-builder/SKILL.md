---
name: oa-drissionpage-download-builder
description: Generate or modify company-style OA browser download Python scripts using DrissionPage, Excel-based user configuration, OCR captcha retry, report navigation, export polling, file download, and xlwings workbook merging. Use when the user provides an OA download script, OA report navigation steps, browser automation requirements, captcha/login behavior, downloaded Excel naming rules, or asks to update OA/Weaver-style web report download automation while preserving the company Jupyter/Spyder-testable script style.
---

# OA DrissionPage Download Builder

## Core Principle

Generate OA browser automation scripts by preserving the company's existing executable-script style. Prefer practical, step-by-step scripts that the user can run and test in Jupyter, Spyder, or an IDE cell by cell. Do not redesign the workflow into a CLI, package, class hierarchy, or `main()` entrypoint unless the user explicitly asks.

## Default Script Style

Use this delivery style for complete `.py` files:

- Top-level execution follows the business order: imports, parameters/config, browser initialization, login, each download step, post-processing, cleanup.
- Use ordinary comment headings for sections. Do not require `# In[ ]:` markers.
- Wrap only reusable actions in functions, such as browser initialization, captcha OCR, login, report download, export polling, and workbook merge helpers.
- Keep user-editable parameters near the top or read them from the existing configuration workbook.
- Preserve company naming, directory, print-message, and retry patterns from the supplied script.
- Avoid `main()` and `if __name__ == "__main__"` by default; use them only when the user explicitly requests command-line execution or importable modules.

## Required Preflight

Before generating or modifying an OA download script, identify or ask for:

- OA system type and URL pattern, but do not store real internal URLs in reusable skill records.
- Browser path and whether the browser should run visibly or headless.
- Configuration source, usually `用户配置.xlsx` with Web configuration fields.
- Login fields, captcha behavior, retry count, and password-error behavior.
- Report navigation path, report names, search conditions, department/tree selections, and export buttons.
- Download directory, final shared-drive output directory, file naming rules, and whether existing files should be cleared first.
- Post-processing rules, such as merging downloaded workbooks into one output workbook with specific sheet names.

## Reusable OA Patterns

When matching the current company OA style, prefer these patterns:

- Read browser path, user, password, retry count, and show/hide browser flag from the existing config workbook via `xlwings`.
- Clear the local raw-download folder before a fresh run only when the supplied script already does this or the user confirms it.
- Initialize `DrissionPage.ChromiumPage` with `ChromiumOptions().set_browser_path(browser_path)` and optional headless mode.
- Set `Settings.raise_when_ele_not_found = False` and a clear `NoneElement` value when the source script uses that pattern.
- Use `ddddocr` for captcha recognition when the OA login page requires image captcha.
- Retry captcha failures up to the configured retry count; exit immediately on password error.
- Delete temporary captcha images in a `finally` block.
- Wait for search/export UI elements before clicking instead of relying only on fixed sleeps.
- Treat `file-cancel` as the export-in-progress signal; poll until it disappears before clicking `file-download`.
- Use longer polling windows for slow reports.
- Use `click.to_download(origin_dir)` and `mission.wait(show=False)` when following DrissionPage download style.
- Merge downloaded Excel files with `xlwings` when the business expects a final workbook with multiple sheets.
- Use `xlwings` for every direct read, creation, modification, merge, or save of company Excel workbooks. Use pandas only for in-memory DataFrame processing; unless the user explicitly approves an exception, do not use `pandas.read_excel()`, `DataFrame.to_excel()`, `ExcelWriter`, `openpyxl`, or `xlsxwriter` for business-workbook I/O.
- Use filename prefixes to assign output sheet names only after confirming the prefixes.
- Add timestamps to final output files when the source pattern does so.

## Safety Rules

Do not persist secrets or private infrastructure details in skills, GitHub comments, or bug libraries:

- Do not record real OA URLs, internal IP addresses, usernames, passwords, shared-drive paths, or department structures unless the user explicitly confirms they are safe to store.
- In reusable examples, replace them with placeholders such as `OA_URL`, `CONFIG_PATH`, `RAW_DOWNLOAD_DIR`, and `FINAL_OUTPUT_DIR`.
- Keep credentials in the user's existing config workbook or local-only config files, not hardcoded into generated reusable examples.
- If a script must contain internal paths for the user's local run, mention that they should not be uploaded to public GitHub.

## Validation

For generated or modified scripts:

- Run `python -m py_compile <output.py>` when possible.
- Do not claim real OA login, captcha, export, or download was verified unless it was actually run in the user's OA environment.
- If runtime verification is not possible, report that only syntax/static checks were completed.
- For workbook merging, verify that expected sheet-name rules and filename-prefix rules are reflected in code.

## Coordination

Use `finance-excel-logic-python-builder` for downstream financial data cleaning, matching, validation, and report generation after OA files are downloaded.

Use `python-bug-library` after observed DrissionPage, captcha, download, path, permission, or Excel merge failures if the bug has a reusable prevention rule.
