# Running the labelling through Google Forms

The spreadsheet route (`data/labels/handoff/grader_kit.zip`) and the Forms route collect the same ratings and feed the same scripts. Forms suits graders who would rather click than edit cells: nothing but the answer fields can be changed, required questions cannot be skipped, each answer sits on its own page, and any number of people can take part with nothing more than the links.

## What the generator builds

`shared/forms/make_label_forms.gs` has three entry points.

**`buildBackgroundForm()`: "Grader background and assignment".** The description gives the background of the study and the assignment (pilot, blocks, time). Then: the grader's email address (recorded by the form), role or profession, years of experience, degree, a grid on familiarity with the four task families, English level, annotation experience, the four ground rules to tick, how many blocks the grader plans to do.

**`buildForms()`: one form per block.** 31 forms of 50 answers for the main sheet (about 38 minutes each), one form for the pilot.

| Page | Content, top to bottom |
|---|---|
| 1 | title and time; the grader's **email address**, recorded by the form (it links that person's forms); "How to grade" in four lines; the scale table |
| 2 to 51, one per answer | "Answer 12 of 50"; the **answer card** (a two-column table with task, question, reference answer in green and the system's final answer in yellow; under it the data table as a real grid or, for entity matching, the two records side by side); the **1 to 7 legend strip** (seven coloured cells, each with its name and one-line definition); **Rating**, a 1 to 7 scale row from "Wrong or no answer" to "Correct" (required); **Hedged?** No / Yes (required); **Note** (optional); at the bottom, "Only if needed: the system's full reply" |
| end | a confirmation naming the block, with the link to edit the response |

Graders record 1 to 7. The conversion to a 0 to 1 utility, (rating − 1) / 6, happens later in the agreement script.

**`refreshAllocation()`: the work list.** Writes a tab `allocation`: every form with its respondent link, minutes, how many graders have submitted it so far, how many more it needs to reach `TARGET_PER_FORM` (3), and their IDs. Share this tab with the graders: they take the block that still needs the most graders. Run it again whenever you want fresh counts, or put it on an hourly trigger.

The card, the scale table and the legend strip are pictures, made by `uv run python shared/scripts/06_render_row_images.py` into `data/labels/forms_images/` (one PNG per answer plus `scale_table.png` and `scale_strip.png`; not kept in git). Forms cannot draw tables in text, so the pictures are what makes a page readable. Without them the generator falls back to plain text.

`data/labels/handoff/grader_kit/04_FORM_PREVIEW.html` shows the first page and three real answer pages in exactly this layout.

## Step by step (coordinator)

1. `uv run python shared/scripts/06_render_row_images.py`, then in Google Drive create a folder named exactly `labelling_images` and upload everything from `data/labels/forms_images/` into it.
2. Drive > New > Google Sheets. File > Import > Upload > `data/labels/labeller_sheet.csv`, replace the current sheet. Rename the tab `rows`.
3. Extensions > Apps Script. Paste `shared/forms/make_label_forms.gs`, save.
4. Run `buildBackgroundForm` once; authorise Forms and Drive when asked (first run only).
5. Run `buildForms`. A run builds forms for about four minutes and stops; the tab `forms` lists each form as DONE. Run it again until the log says all 31 are built, or add a trigger (Triggers > Add trigger > `buildForms` > time-driven > every 10 minutes) and delete it when the tab shows 31 DONE rows. A form cut off mid-build is trashed and rebuilt on the next run.
6. Run `refreshAllocation`.
7. Pilot: a second spreadsheet from `data/labels/pilot_30.csv` (tab `rows`), the same script with `FORM_PREFIX = "Answer grading, pilot"`, run `buildForms` once. One form.
8. Open one respondent link and page through two answers to confirm the layout.
9. Send every grader: `01_LABELLING_GUIDE.html`, `00_BACKGROUND_AND_ASSIGNMENT.html`, the background-form link and the pilot link, and ask them to use the same email address on every form. The forms record the address; the converter replaces it by a code, so the paper and the repository stay anonymous. `EMAIL_MODE = "VERIFIED"` in the script asks for Google's verified mode (the grader is signed in and the address is filled in); if that is not available the form falls back to "responder input" (the grader types it). The mode each form got is in column H of the `forms` tab; run `checkEmailMode` to re-read it, or look at Settings > Responses > Collect email addresses in any form. If some graders have no Google account, set `EMAIL_MODE = "RESPONDER_INPUT"` before building.
10. After the pilot: Responses > ⋮ > Download responses (.csv), then
    `uv run python shared/scripts/05_forms_to_returned.py --pilot ~/Downloads/pilot.csv`,
    `uv run python shared/scripts/03_label_agreement.py --pilot --check all`,
    `uv run python shared/scripts/03_label_agreement.py --pilot`, and hold the review call over the queue file.
11. Share the `allocation` tab. Collect as often as you like: run `exportResponses` in the script (it writes one CSV per form plus `background.csv` into the Drive folder `labelling_responses`; download that folder), or download each form's responses by hand (Responses > ⋮ > Download responses), and run
    `uv run python shared/scripts/05_forms_to_returned.py folder/*.csv`. It gives each email address a code (`g01`, `g02`, ...; the table is `data/labels/grader_registry.csv`, git-ignored, never share it), writes one returned file per code, lists each grader's answers and forms, and warns when two addresses look like the same person (`--alias "second@address=first@address"` merges them).
12. Link backgrounds to ratings: download the background form's responses and run
    `uv run python shared/scripts/05_forms_to_returned.py --background ~/Downloads/background.csv`. The email address links the two, and the same codes are used. The script writes `data/labels/graders.csv` (git-ignored, no addresses) and lists anyone who rated answers without a background form.
13. `uv run python shared/scripts/03_label_agreement.py --check all`, then the comparison; send graders to the blocks `coverage.csv` lists; adjudicate; rebuild the paper. See `notes/WALKTHROUGH_COORDINATOR.md`.

## Step by step (grader)

1. Read the background and assignment page and the guide, and fill the background form. Use the same email address on every form.
2. Open the pilot form. The first page has the scale table.
3. Each following page is one answer: read the card (question, reference in green, final answer in yellow, the table or the two records), choose a rating from 1 to 7 with the legend strip right above it, choose No or Yes for hedged, add a note only if unsure, press Next.
4. Press Submit at the end of the form. "Edit your response" on the confirmation page lets you change an answer later.
5. After the pilot call, open the allocation sheet, take the block that still needs the most graders, and do the whole block. Repeat for as many blocks as you agreed. Do not discuss answers with other graders before the pilot call.

## Trade-offs

* For: no file handling by the grader, no possible edits to read-only data, required fields, the legend beside every rating, records side by side, live counts of who has done what, works on a tablet.
* Against: about 1,600 pictures to upload to Drive once; a form cannot be saved half-done unless Google's draft autosave is available for the account, which is why a block is 50 answers; collecting means downloading 31 files instead of receiving one per grader.
* Either way the output is the same `03_main_<code>` file per grader, and the agreement script does not know which route was used.
