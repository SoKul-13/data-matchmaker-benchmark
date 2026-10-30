# Step-by-step walkthrough for labellers

This is the practical "what do I click" companion to the labelling guide (`01_LABELLING_GUIDE`). The guide holds the rules; this page holds the procedure. Total time: about 15 minutes to read the guide, 25 minutes for the pilot, about 39 hours (about 8 working days) for the main sheet, in as many sittings as you like.

## Step 1. Open your folder

You received a zip named `labeller_X.zip`. Unzip it. Your letter is in every file name; keep it. The folder contains:

| File | Use |
|---|---|
| `00_START_HERE_WALKTHROUGH` | this page |
| `01_LABELLING_GUIDE.html` | the rules; open in any browser, print if you like |
| `02_pilot_X.xlsx` (or `.csv`) | 30 practice rows, done first |
| `03_main_X.xlsx` (or `.csv`) | 401 rows, the real work |

Pick one format per sheet and stay with it: the `.xlsx` in Excel, Numbers or Google Sheets (File > Import > Upload), or the `.csv` in any editor. The `.xlsx` is easier: the columns you fill are yellow and have drop-downs.

## Step 2. Read the guide once, fully

Fifteen minutes. Pay most attention to section 2 (the five levels), section 4 (rules for every row) and section 5 (worked examples). Keep it open in a second window while you grade.

## Step 3. Set up the sheet

* `03_main` holds every row and you grade all of them. The `assigned_to` column lists all graders and needs no filtering.
* Freeze the header row if your program did not keep it frozen (View > Freeze > 1 row).
* Widen or wrap these columns so you can read them: `question`, `gold_answer`, `accepted_alternatives`, `model_final_answer`. In the `.xlsx` this is already done.
* Leave `context`, `table` and `model_full_reply` narrow; you only open them when needed.
* Do not sort, filter-and-delete, rename, hide-and-forget, or add columns. Hiding columns temporarily is fine; unhide before you return the file.

## Step 4. Grade one row (the loop you repeat for every row)

1. Read `question`. Note `answer_type` (numeric, boolean, text, freeform) so you know which rule block in section 3 of the guide applies.
2. Read `gold_answer` and `accepted_alternatives`. If `gold_is_a_list` says "yes", every item is required.
3. Read `model_final_answer`. This is the only thing you grade.
4. Decide `utility`: is it the same answer (1), the same with a trivial defect (0.75), half of it or the right quantity in the wrong form (0.5), close but wrong (0.25), or wrong / empty / refused (0)?
5. Decide `hedged`: did the final answer offer two candidates, a range where one value was asked, or decline to commit? Then 1, otherwise 0.
6. Only if the final answer is blank or looks cut off, open `model_full_reply` and look at its last lines. If an unambiguous final answer is there, grade it and write `note = extracted from reply`. If there is no answer anywhere, `utility = 0`.
7. Only if you cannot judge from the question and the gold alone (rare: usually sentence answers where the gold is long), glance at `table` or `context`.
8. If you hesitated between two levels, take the lower one and write a two-to-five-word note.

Typical pace: 45 seconds a row. Some rows take 5 seconds, a few take 3 minutes. Do not look anything up on the web; grade against the reference even if you suspect the reference is wrong (write `note = reference doubtful`).

## Step 5. The pilot (30 rows)

Grade all 30 rows of `02_pilot` exactly as in step 4 (there is no `assigned_to` filter on the pilot: everyone grades all of it). Return it (step 7). You will then get a short call where the rows the labellers graded differently are discussed, and the guide may gain a clarification. Do not talk to the other labellers before that call. The pilot rows are not reused.

## Step 6. The main sheet (3100 rows)

Work in sittings of at most 100 rows; fatigue shows up as drifting standards. Every row is graded by 5 people in all, so there is no need to agonise, just be consistent. Before closing a sitting, save, and note which `row_id` you reached. The order of rows is random on purpose; do not reorder.

## Step 7. Check before you submit

Run down this list on the finished sheet:

* `utility` is filled on every one of your rows and only with 1, 0.75, 0.5, 0.25 or 0. In the `.xlsx` the drop-down enforces this; in a `.csv`, filter the column for anything else.
* `hedged` is filled on every one of your rows with 0 or 1.
* Row count is unchanged: 31 lines including the header for the pilot, 3101 for the main sheet.
* Column names are unchanged and in the same order.
* No values anywhere except in `utility`, `hedged`, `note`.
* The file is renamed with your letter: `03_main_X.xlsx` where X is your letter (same for the pilot: `02_pilot_X.xlsx`).

## Step 8. Submit

Send the file back by the channel you received it (email, shared drive, upload link): `02_pilot_X.xlsx` first, later `03_main_X.xlsx` (or the `.csv` versions), with X replaced by your letter. If you worked in Google Sheets, download as Microsoft Excel (`.xlsx`) or as CSV of the one sheet. You will get a confirmation that the file passed the automatic checks; if it did not, the message says which rows to fix.

## What happens to your labels

Every row is graded by several labellers and the sheets are compared row by row. Rows whose labels differ by more than one level go to an adjudicator who sees all the labels and notes and decides. The agreed labels are then used to test an automatic scorer. You are never named; results are reported by letter plus the group's professional background in one line.
