# Running the labelling through Google Forms

The spreadsheet route (`data/labels/handoff/`) is the default and the simplest. Google Forms is the alternative when labellers would rather click than edit cells, or when you want to prevent any edit outside the three answer fields. The data, the rules and the downstream scripts are identical; only the collection step changes.

## How it is laid out

Google Forms cannot import a table of rows, so an Apps Script builds the forms from the sheet. With the default layout (20 graders, 3 per row) it builds one or two forms per grader holding only that grader's 60 or so rows, plus one pilot form everyone fills; the first question asks for the grader's letter. Each row is one page:

* page title: the `row_id`
* page text: task family, source, answer type, choices if any, the question, the reference answer, accepted alternatives, the list flag, and the system's final answer
* a collapsed-looking header holding the context, table and full reply (cut at 3,500 characters; the spreadsheet remains the reference for longer material)
* `R001 | utility` (required, one of 1 / 0.75 / 0.5 / 0.25 / 0), `R001 | hedged` (required, 0 / 1), `R001 | note` (optional)

Required questions and fixed choices mean the file that comes back cannot contain blanks or off-scale values, which removes most of the `--check` failures of the spreadsheet route.

## Step by step (coordinator)

1. Google Drive > New > Google Sheets. File > Import > Upload > `data/labels/labeller_sheet.csv`. Rename the tab to `rows`. Then File > Import > Upload > `data/labels/assignments.csv` as a new tab named `assignments` (this makes the script build per-grader forms; without it, it builds shared forms with a letter question listing all letters).
2. Extensions > Apps Script. Paste `shared/forms/make_label_forms.gs`. Leave `BATCH = 50`, `FORM_PREFIX = "Labelling, main"`. Run `buildForms`, authorise the script for Forms and Drive when asked (first run only). It takes a few minutes; forms land in a Drive folder `labelling_forms`, and a new tab `forms` lists every form's edit and respondent link.
3. Repeat with `data/labels/pilot_30.csv` and `FORM_PREFIX = "Labelling, pilot"` (one form).
4. Send each grader: the guide (`01_LABELLING_GUIDE.html`), the walkthrough, the pilot respondent link first, later their own main-form links from the `forms` tab, and tell them their letter. Settings worth keeping: "Allow response editing" on (set by the script), "Limit to 1 response" off (two people share each form), "Collect email addresses" off (anonymity in the paper).
5. After the pilot, in the pilot form: Responses > ⋮ > Download responses (.csv). Convert and check:
   `uv run python shared/scripts/05_forms_to_returned.py --labeller A --pilot ~/Downloads/pilot.csv` (then B), then `uv run python shared/scripts/03_label_agreement.py --pilot --check A`, then the comparison, exactly as in the coordinator walkthrough.
6. After the main round, download every main form's response CSV into one folder and run
   `uv run python shared/scripts/05_forms_to_returned.py --labeller A folder/*.csv` (then B). The script keeps each labeller's latest submission per form, fills the canonical sheet and writes `data/labels/returned/03_main_A.csv`. From there everything is the standard flow: `--check`, comparison, adjudication, merge, paper rebuild.

## Step by step (labeller)

1. Read the guide, then open the pilot link. Choose your letter on the first page.
2. Each page is one answer to grade: read the question, the reference, the final answer; pick `utility` and `hedged`; add a note only if unsure. Press Next. The progress bar shows how far you are in the batch.
3. Press Submit at the end of each form. You can stop between forms at any time; inside a form, use "Edit your response" from the confirmation page if you need to change something.
4. Do your main forms in order after the pilot call. Do not discuss rows with the other labeller before that call.

## Trade-offs

* For: no file handling by the labeller, no possible edits to read-only data, required fields, works on a phone or tablet.
* Against: tables and long contexts render as plain text without columns (the spreadsheet shows them in a cell); a form cannot be saved half-done unless Google's draft autosave is available for the account; building and downloading is nine files instead of one.
* Either way the output is the same `03_main_X.csv`, and the agreement script does not know which route was used.
