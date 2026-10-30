# Labelling guide: grading model answers against a reference answer

You are grading short answers that AI systems gave to questions about tables, documents and data records. For each row you decide how correct the system's answer is compared with a reference answer that we supply. You are not judging writing quality, length, politeness or reasoning. Only whether the final answer is right.

Your labels are the ground truth we use to test an automatic scoring program, so consistency matters more than speed. Several people label every row independently; where their labels differ by more than one step, an adjudicator decides. Please do not discuss rows with the other labellers until the pilot review.

## 1. What you receive

A spreadsheet (`03_main.xlsx` or `.csv`; open it in Excel, Numbers or Google Sheets). You grade the rows whose `assigned_to` contains your letter. One row = one answer to grade. Columns:

| Column | What it is |
|---|---|
| `row_id` | an anonymous id; leave it as is |
| `assigned_to` | the letters of the graders who own this row; filter it to your letter |
| `task_family` | the kind of task (entity matching, schema matching, table question answering, financial document reading) |
| `dataset_description` | one line on where the question comes from |
| `answer_type` | `numeric`, `boolean` (yes/no), `text` (a short phrase, name or label), or `freeform` (a sentence) |
| `question` | the question the system was asked |
| `context`, `table` | the material the system was shown (may be long; some rows have neither, where the system answered from its own knowledge) |
| `choices` | for multiple-choice rows, the options offered |
| `gold_answer` | the reference answer |
| `accepted_alternatives` | other spellings or forms that count as fully correct (e.g. `match`/`yes`/`1`; several valid column names) |
| `gold_is_a_list` | when filled, the reference is a list and every item is required |
| `model_final_answer` | the line the system marked as its final answer (what you grade) |
| `model_full_reply` | the system's entire reply, for context only |
| `utility` | **you fill this**: one of `1`, `0.75`, `0.5`, `0.25`, `0` |
| `hedged` | **you fill this**: `1` if the answer offers more than one final candidate or refuses to commit, else `0` |
| `note` | optional: one short phrase when you were unsure or the rules did not fit |

You never see which system produced the answer, and you should not try to guess.

## 2. The scale

| utility | Meaning | Typical cases |
|---|---|---|
| **1** | Correct. A reader with the reference in hand would accept it as the same answer. | identical; an accepted alternative; same number written differently (`1,577.00` vs `1577`; `14.5%` vs `0.145`; `$3.2M` vs `3,200,000`); extra harmless words around the right answer (`The total is 721,453.`); same list in a different order |
| **0.75** | Correct with a minor defect that does not change the meaning. | rounding within 1 % (`721,000` for `721,453`); a unit written differently but unambiguous (`3.2 million` for `3,200,000`); a correct answer with a trailing qualifier that adds nothing (`approximately`, `about`) |
| **0.5** | Partially correct: part of the required answer, or the right quantity in the wrong form. | right number but wrong scale word or unit (`3.2` for `3.2 million`; `14.5` for `14.5%` where the % matters); a list with some required items missing and no wrong ones; a sentence that states only part of the reference fact; a correct answer plus a second, wrong candidate (also set `hedged = 1`) |
| **0.25** | Wrong but related: it answers the question, is in the right form, and is close or confusable. | a number off by more than 1 % but within an order of magnitude; the right value with the wrong sign; a list with wrong extra items; the neighbouring row or column of a table; an entity that shares most attributes with the right one |
| **0** | Wrong, empty, or no answer. | a different value, name or label; the opposite yes/no; a refusal; "cannot be determined" when the reference exists; an answer to a different question; a reply with no final answer at all |

If you hesitate between two levels, choose the lower one and write a note.

## 3. Rules by answer type

**Numbers (`numeric`).**
1. Equal to the reference within 1 % → `1`. Within 1 % but visibly rounded or truncated → `0.75`.
2. Same digits, different unit or scale word that changes the meaning (`3.2` vs `3.2 million`; `14.5` vs `14.5%` when the question asks for a percentage) → `0.5`. If the scale is merely written differently and the value is the same, it is `1`.
3. Wrong sign, or off by more than 1 % but less than 10× → `0.25`. Anything further → `0`.
4. A range or two candidate numbers where one is right → `0.5` and `hedged = 1`.
5. Percent versus fraction: `0.145` and `14.5%` are the same value → `1`.

**Yes/no (`boolean`).**
1. Only `1` or `0`. `yes` / `match` / `entailed` / `true` are the same answer; `no` / `no match` / `refuted` / `false` are the same answer.
2. `probably yes`, `likely a match` → grade as `yes` and set `hedged = 1`.
3. `yes and no`, `cannot say`, `either` → `0` and `hedged = 1`.

**Short text (`text`).** Names, labels, column names, option letters, categories.
1. Exact or an accepted alternative, ignoring case, punctuation and articles → `1`.
2. The right answer embedded in a longer phrase that adds nothing wrong (`the column is customer_id`) → `1`.
3. A typo or a one-character slip of the right answer → `0.75`.
4. A more general or more specific version of the right answer (`revenue` for `net revenue`; `France` for `Paris, France`) → `0.5`.
5. Multiple choice: the option letter and the option text are both correct answers; a different option is `0`; two options → `0.5` and `hedged = 1`.
6. For column-matching rows (`task_family` = schema matching), several target columns may be listed as accepted alternatives; any one of them is `1`.

**Lists (`gold_is_a_list` is filled).**
1. Every required item and no wrong ones, in any order → `1`.
2. All required items plus harmless duplicates or formatting → `1`.
3. Some required items missing, none wrong → `0.5`.
4. Wrong extra items (with or without all the right ones) → `0.25`.
5. Nothing right → `0`.

**Sentences (`freeform`).**
1. States the reference fact correctly, however it is phrased → `1`.
2. States it with a small inaccuracy that does not change the fact (a rounded figure, a slightly different name form) → `0.75`.
3. States part of it, or states it with a wrong detail alongside → `0.5`.
4. Talks about the right subject but gets the fact wrong → `0.25`.
5. Contradicts the reference or does not address it → `0`.

## 4. Rules that apply to every row

* **Grade the final answer**, shown in `model_final_answer`. Use `model_full_reply` only to check that the final line was extracted correctly. If the final line is missing or clearly cut off mid-sentence and the full reply contains an unambiguous final answer, grade that answer and write `note = extracted from reply`. If the reply ends without any answer, grade `0`.
* **Do not grade the reasoning.** A right answer reached by wrong reasoning is `1`; a wrong answer with excellent reasoning is `0`.
* **Do not look anything up.** Grade only against the reference and the material shown. If you believe the reference itself is wrong, grade against the reference anyway and write `note = reference doubtful`.
* **Hedging.** Set `hedged = 1` whenever the final answer offers more than one candidate (`A or B`, `either 12 or 15`, a list where one was asked for), gives a range where a value was asked for, or declines to commit (`probably`, `cannot be sure`). Hedging does not by itself change `utility`; grade the best candidate as if it were alone, but never above `0.5` when a wrong candidate is offered beside it.
* **Refusals and empty answers** (`I cannot answer`, `insufficient information`, blank) are `0` with `hedged = 0`, unless the reference itself says the question is unanswerable, in which case they are `1`.
* **Extra material** after a correct answer (explanations, caveats, citations) does not lower the grade. A correct answer followed by "but it could also be X" is hedged.
* **Formatting never matters**: capitalisation, punctuation, thousands separators, currency symbols, quotation marks, leading articles.

## 5. Worked examples

| Reference | Final answer | utility | hedged | Why |
|---|---|---|---|---|
| `721453` | `721,453` | 1 | 0 | same number |
| `721453` | `721,000` | 0.75 | 0 | rounded, within 1 % |
| `721453` | `721` (table was in thousands) | 0.5 | 0 | right digits, wrong scale |
| `721453` | `712453` | 0.25 | 0 | off by about 1 %, a digit slip: wrong but close |
| `721453` | `1,200,000` | 0 | 0 | wrong |
| `14.5%` | `0.145` | 1 | 0 | same value |
| `yes` (accepted: `match`, `1`) | `These are the same product.` | 1 | 0 | a clear yes |
| `yes` | `Probably the same product.` | 1 | 1 | yes, hedged |
| `no` | `Yes` | 0 | 0 | opposite |
| `customer_id` (accepted: `cust_id`) | `cust_id` | 1 | 0 | accepted alternative |
| `net revenue` | `revenue` | 0.5 | 0 | more general |
| `Paris` | `Paris or Lyon` | 0.5 | 1 | right answer beside a wrong one |
| list `apple; pear; fig` | `apple, fig, pear` | 1 | 0 | complete, any order |
| list `apple; pear; fig` | `apple, pear` | 0.5 | 0 | one required item missing |
| list `apple; pear; fig` | `apple, pear, fig, kiwi` | 0.25 | 0 | a wrong extra item |
| sentence: "Revenue rose 12 % to 4.1 billion in 2021." | `Revenue grew about 12 percent in 2021, reaching $4.1bn.` | 1 | 0 | same fact |
| same | `Revenue was 4.1 billion in 2021.` | 0.5 | 0 | half the fact |
| same | `Revenue fell in 2021.` | 0 | 0 | contradicts |
| any | `I cannot determine this from the table.` | 0 | 0 | refusal |

## 6. How the work runs

1. **Pilot (30 rows, about 25 minutes).** Every labeller grades the same pilot sheet independently. We then compare, discuss the rows where labels differed by more than one step, and clarify the guide if a rule was unclear. Nothing from the pilot is reused.
2. **Main sheet.** Your sheet holds the rows assigned to you (the walkthrough says how many). Work in sittings of at most 100 rows. Keep a steady pace; about 45 seconds per row is typical. Fill `utility` and `hedged` on every row; use `note` sparingly.
3. **Return the file** with the same name and the same rows and columns, values only in the three columns you own. Do not sort, filter-and-delete, or add columns.
4. **Adjudication.** Rows where the labellers differ by more than one step, or where a label is blank, go to an adjudicator with all labels and notes. The adjudicated value is final.

## 7. What we report

Agreement between labellers (Krippendorff's α on utility and on hedged, exact and within-one-step agreement), the number of adjudicated rows, and then the correlation between the automatic scorer and your labels. Your labels are stored by row id only and are never attributed to you by name in the paper.

Questions about a specific row: write them in `note` and keep going; do not stop to ask.
