# Step-by-step walkthrough for graders

The practical companion to the labelling guide (`01_LABELLING_GUIDE`). The guide holds the rules; this page holds the procedure. Time: about 15 minutes to read the guide, 25 minutes for the pilot, then about 38 minutes per block of 50 answers, for as many blocks as you agreed to do.

## Step 1. Use one email address

You are identified by your email address, nothing else: there are no letters and no IDs to choose. Use the same address everywhere: on the background form, on every online form, and in the names of the files you send back. It is the only thing that links your background form to your ratings. The address is used to link your work and to reach you; before any analysis it is replaced by a code, and neither your name nor your address appears in any publication or shared file.

## Step 2. Open the kit

| File | Use |
|---|---|
| `00_BACKGROUND_AND_ASSIGNMENT.html` | one page: what the study is, what you are asked to do, the scale |
| `00_BACKGROUND_FORM.xlsx` | a short form about your professional background; fill and return it (or use the online form if you were sent a link) |
| `00_START_HERE_WALKTHROUGH` | this page |
| `01_LABELLING_GUIDE.html` | the rules; open in any browser, print if you like |
| `SCALE_TABLE.png`, `SCALE_STRIP.png` | the 1 to 7 scale as pictures, to keep beside you |
| `02_pilot.xlsx` (or `.csv`) | 30 practice answers, done first, by everyone |
| `03_main.xlsx` (or `.csv`) | all 1,550 answers in 31 blocks of 50 (the `block` column) |
| `04_FORM_PREVIEW.html` | what a page of the online form looks like |

You work either in the online forms (one form per block; you were sent links) or in the spreadsheets. Pick one route and stay with it. In a spreadsheet, use the `.xlsx` in Excel, Numbers or Google Sheets (File > Import > Upload); the columns you fill are yellow and have drop-downs.

## Step 3. Read the brief and the guide once, fully

Start with `00_BACKGROUND_AND_ASSIGNMENT`, then the guide. Pay most attention to section 2 (the 1 to 7 scale), section 4 (rules for every answer) and section 5 (worked examples). Keep the guide open in a second window while you grade. Fill the background form.

## Step 4. Grade one answer (the loop you repeat)

1. Read the question and note the answer type (numeric, yes/no, short text, sentence): it tells you which rule table in section 3 of the guide applies.
2. Read the reference answer and anything listed as also accepted. If the reference is a list, every item is required.
3. Read the system's final answer. This is the only thing you grade.
4. Decide the **rating**, a whole number from 1 to 7. Start from the three anchors: would I accept this as the reference answer (7), is half of it right (4), is nothing right (1)? Then move one step if it fits better: correct with a cosmetic defect (6), mostly correct (5), mostly wrong or a near miss (3), wrong but related (2). Yes/no answers are only 7 or 1. The scale with every definition is in front of you on each form page and on the `scale` tab of the sheet. We convert ratings to a value between 0 and 1 afterwards; you never type that.
5. Decide **hedged**: did the final answer offer two candidates, a range where one value was asked, or decline to commit? Then yes (1), otherwise no (0).
6. Only if the final answer is blank or looks cut off, look at the end of the system's full reply. If an unambiguous final answer is there, grade it and write the note `extracted from reply`. If there is no answer anywhere, the rating is 1.
7. Only if you cannot judge from the question and the reference alone, look at the table or the context.
8. If you hesitated between two neighbouring ratings, take the lower one and write a two-to-five-word note.

Typical pace: 45 seconds an answer. Some take 5 seconds, a few take 3 minutes. Do not look anything up on the web; grade against the reference even if you suspect it is wrong (note `reference doubtful`).

## Step 5. The pilot (30 answers)

Grade all 30 pilot answers exactly as in step 4 and submit or return them (step 8). A short call follows where the answers that graders rated differently are discussed, and the guide may gain a clarification. Do not talk to other graders before that call. The pilot answers are not reused.

## Step 6. The main round, block by block

* The work comes in 31 blocks of 50 answers. A block is one online form, or the rows with one value in the `block` column of the sheet (filter that column).
* You do **whole blocks**, as many as you agreed. Nobody is assigned particular blocks: the allocation sheet you were sent lists every block with the number of graders it has so far. Take the block that still needs the most graders. If you were not sent an allocation sheet, ask which blocks to take.
* Finish a block before starting the next; a half-finished block is the one thing that cannot be used well.
* One block is a natural sitting. Stop after two blocks in a row; fatigue shows up as drifting standards.
* Every answer is graded by several people, so there is no need to agonise. Be consistent.

## Step 7. Check before you send (spreadsheet route)

* In every block you did, `rating` is filled on every row with a whole number from 1 to 7 (the drop-down shows each with its name, for example `6 Correct, cosmetic defect`; in a `.csv` type the number), and `hedged` with 0 or 1.
* No row has a rating without hedged, or the reverse.
* Any filter is cleared, so the file still holds all 1,550 rows (1551 lines with the header; 31 lines for the pilot). Rows you did not grade stay blank; do not delete them.
* Column names are unchanged and no values were typed anywhere except in `rating`, `hedged`, `note`.
* The file is named with your email address: `03_main_<your address>.xlsx`, for example `03_main_ana.lee@example.org.xlsx` (the pilot: `02_pilot_<your address>.xlsx`; the background form: `00_BACKGROUND_FORM_<your address>.xlsx`).

In the online forms none of this is needed: required questions cannot be skipped and nothing else can be edited.

## Step 8. Send

* Online forms: press Submit at the end of each form. The confirmation page has a link to edit your response if you need to change something.
* Spreadsheets: send the file back by the channel you received it (email, shared drive, upload link), pilot first, the main sheet whenever you have finished more blocks. You can send the main sheet several times; the latest file replaces the earlier one. If you worked in Google Sheets, download as Microsoft Excel (`.xlsx`) or CSV first.

You will get a confirmation that the file passed the automatic checks; if it did not, the message says which rows to fix.

## What happens to your ratings

For every answer the ratings of all graders are compared and combined into one value. Answers whose ratings are far apart go to an adjudicator who sees all ratings and notes and decides. The combined values are then used to test an automatic scorer. You are never named; results are reported under grader IDs, plus one sentence on the group's professional background.
