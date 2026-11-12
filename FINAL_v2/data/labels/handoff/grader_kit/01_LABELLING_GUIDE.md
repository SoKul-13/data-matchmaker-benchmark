# Labelling guide: grading model answers against a reference answer

You are grading short answers that AI systems gave to questions about tables, documents and data records. For each row you decide how correct the system's answer is compared with a reference answer that we supply. You are not judging writing quality, length, politeness or reasoning. Only whether the final answer is right.

Your labels are the ground truth we use to test an automatic scoring program, so consistency matters more than speed. Several people label every row independently; where their labels differ widely, an adjudicator decides. Please do not discuss rows with the other labellers until the pilot review.

## 1. What you see for each row

One row (one page in the form, one line in the spreadsheet) = one answer to grade.

| Field | What it is |
|---|---|
| `row_id` | an anonymous id; leave it as is |
| `block` | the block (work unit of 50 answers) the answer belongs to |
| `task_family` | the kind of task (entity matching, schema matching, table question answering, financial document reading) |
| `dataset_description` | one line on where the question comes from |
| `answer_type` | `numeric`, `boolean` (yes/no), `text` (a short phrase, name or label), or `freeform` (a sentence) |
| `question` | the question the system was asked |
| `context`, `table` | the material the system was shown (may be long; a few rows have neither, where the system answered from its own knowledge) |
| `choices` | for multiple-choice rows, the options offered |
| `gold_answer` | the reference answer |
| `accepted_alternatives` | other spellings or forms that count as fully correct (for example `match`, `yes`, `1`; several valid column names) |
| `gold_is_a_list` | when filled, the reference is a list and every item is required |
| `model_final_answer` | the line the system marked as its final answer (**this is what you grade**) |
| `model_full_reply` | the system's entire reply, for context only |
| `rating` | **you fill this**: a whole number from 1 to 7 on the scale below |
| `hedged` | **you fill this**: `1` if the answer offers more than one final candidate or refuses to commit, else `0` |
| `note` | optional: one short phrase when you were unsure or the rules did not fit |

You never see which system produced the answer, and you should not try to guess.

## 2. The scale: a rating from 1 to 7

A 7-point agreement scale, as in a survey: "how far do I agree that this answer is correct?" from 1 (not at all) to 7 (fully). You record the whole number. Afterwards we convert it to a value between 0 and 1 for the analysis (last column); you never type that value.

| Rating | Name | When to use it | Typical cases | Converted later to |
|---|---|---|---|---|
| **7** | Correct | A reader with the reference in hand would accept it as the same answer. | identical; an accepted alternative; same number written differently (`1,577.00` and `1577`; `14.5%` and `0.145`; `$3.2M` and `3,200,000`); harmless words around the right answer; same list in another order | 1.00 |
| **6** | Correct, cosmetic defect | Right answer with a blemish that does not change the meaning. | rounding within 1 % (`721,000` for `721,453`); a typo or one-character slip in a name; a trailing `approximately`; a redundant qualifier | 0.83 |
| **5** | Mostly correct | Right answer, but a small part is missing or slightly imprecise. | a sentence that states the fact but drops a minor detail; a list with at least two thirds of the required items and no wrong ones; a slightly under- or over-specified name (`Paris` for `Paris, France`) | 0.67 |
| **4** | Half correct | About half of what was required, or the right quantity in the wrong form. | right digits with the wrong scale word or unit (`3.2` for `3.2 million`); about half of a list, none wrong; half of the reference fact; a more general category (`revenue` for `net revenue`); a right answer beside a wrong one (also `hedged = 1`) | 0.50 |
| **3** | Mostly wrong, near miss | Only a small part is right, or it just misses. | a number 1 to 5 % off or with one digit wrong; under half of a list, or as many wrong items as right ones; a sentence whose main fact is wrong but a relevant detail is right | 0.33 |
| **2** | Wrong but related | It answers the right question in the right form, but the content is wrong. | a number more than 5 % off but within ten times, or with the wrong sign; the neighbouring row or column of the table; an entity that shares most attributes with the right one; a list of mostly wrong items | 0.17 |
| **1** | Wrong or no answer | Nothing usable. | a different value, name or label; the opposite yes/no; a refusal; "cannot be determined" when the reference exists; an answer to a different question; no final answer at all | 0.00 |

Three anchors keep the scale steady: **7** means "I would accept this", **4** means "half of it is right", **1** means "nothing is right". The ratings in between lean towards the nearer anchor. If you hesitate between two neighbouring ratings, choose the lower one and write a note.

## 3. Rules by answer type

**Numbers (`numeric`).**

| Situation | rating |
|---|---|
| equal to the reference, in any notation (percent or fraction, thousands separators, currency symbol, scale word that gives the same value) | 7 |
| within 1 % of the reference but visibly rounded or truncated | 6 |
| right value, unit or scale word missing where the question makes it obvious (`3.2` when the question says "in millions") | 5 |
| same digits, wrong unit or scale that changes the value (`3.2` for `3.2 million` with no such cue; `14.5` for `14.5%` where a fraction was asked) | 4 |
| 1 to 5 % off, or exactly one digit wrong or two digits swapped | 3 |
| more than 5 % off but within ten times; or the right magnitude with the wrong sign | 2 |
| anything further off | 1 |
| a range or two candidate numbers, one of them right | 4 and `hedged = 1` |

**Yes/no (`boolean`).** Only **7** or **1**; the ratings in between are not used.

| Situation | rating | hedged |
|---|---|---|
| the same answer (`yes`, `match`, `entailed`, `true` are one answer; `no`, `no match`, `refuted`, `false` are the other) | 7 | 0 |
| `probably yes`, `likely a match`: grade as `yes` | 7 or 1 | 1 |
| `yes and no`, `cannot say`, `either` | 1 | 1 |
| the opposite answer | 1 | 0 |

**Short text (`text`).** Names, labels, column names, option letters, categories.

| Situation | rating |
|---|---|
| exact or an accepted alternative, ignoring case, punctuation and articles; or embedded in a longer phrase that adds nothing wrong (`the column is customer_id`) | 7 |
| a typo or one-character slip of the right answer | 6 |
| the right thing, slightly under- or over-specified, still unambiguous (`Paris` for `Paris, France`; `net revenues from operations` for `net revenue`) | 5 |
| a more general or more specific version that could mean something else (`revenue` for `net revenue`; `France` for `Paris, France`) | 4 |
| shares only a part with the right answer (right family name, wrong person; right product line, wrong model) | 3 |
| a related but different entity or column (`ship_date` for `order_date`; a neighbouring option) | 2 |
| unrelated, or a different multiple-choice option | 1 |

Multiple choice: the option letter and the option text are both correct answers; two options with one right is 4 and `hedged = 1`. Column matching: when several target columns are listed as accepted alternatives, any one of them is 7.

**Lists (`gold_is_a_list` is filled).** Count the required items found and the wrong items added. Order and duplicates never matter.

| Required items present | Wrong items added | rating |
|---|---|---|
| all | none | 7 |
| at least two thirds | none | 5 |
| about half | none | 4 |
| all or nearly all | one or two | 4 |
| under half | none | 3 |
| some | as many wrong as right, or more | 2 |
| none | any | 1 |

**Sentences (`freeform`).** Judge the fact, not the wording, and judge it against what the question asks.

| Situation | rating |
|---|---|
| states the reference fact correctly, however phrased; or gives exactly what the question asked even if the reference sentence says more | 7 |
| states it with a small inaccuracy that does not change the fact (a rounded figure, a slightly different name form) | 6 |
| states the main fact but leaves out a secondary detail the question asked for | 5 |
| states about half of it, or states it with a wrong detail alongside | 4 |
| main fact wrong, but a relevant detail from the reference is right | 3 |
| right subject, wrong fact | 2 |
| contradicts the reference or does not address the question | 1 |

## 4. Rules that apply to every row

* **Grade the final answer**, shown in `model_final_answer`. Use `model_full_reply` only to check that the final line was extracted correctly. If the final line is missing or clearly cut off mid-sentence and the full reply contains an unambiguous final answer, grade that answer and write `note = extracted from reply`. If the reply ends without any answer, grade `1`.
* **Do not grade the reasoning.** A right answer reached by wrong reasoning is `7`; a wrong answer with excellent reasoning is `1`.
* **Do not look anything up.** Grade only against the reference and the material shown. If you believe the reference itself is wrong, grade against the reference anyway and write `note = reference doubtful`.
* **Hedging.** Set `hedged = 1` whenever the final answer offers more than one candidate (`A or B`, `either 12 or 15`, a list where one was asked for), gives a range where a value was asked for, or declines to commit (`probably`, `cannot be sure`). Hedging does not by itself change `rating`; grade the best candidate as if it were alone, but never above `4` when a wrong candidate is offered beside it.
* **Refusals and empty answers** (`I cannot answer`, `insufficient information`, blank) are `1` with `hedged = 0`, unless the reference itself says the question is unanswerable, in which case they are `7`.
* **Extra material** after a correct answer (explanations, caveats, citations) does not lower the grade. A correct answer followed by "but it could also be X" is hedged.
* **Formatting never matters**: capitalisation, punctuation, thousands separators, currency symbols, quotation marks, leading articles.

## 5. Worked examples

| Reference | Final answer | rating | hedged | Why |
|---|---|---|---|---|
| `721453` | `721,453` | 7 | 0 | same number |
| `721453` | `721,000` | 6 | 0 | rounded, within 1 % |
| `721453` | `721` (question said "in thousands") | 5 | 0 | right value, scale left implicit |
| `721453` | `721` (no such cue) | 4 | 0 | right digits, wrong scale |
| `721453` | `712453` | 3 | 0 | two digits swapped, about 1 % off: near miss |
| `721453` | `650,000` | 2 | 0 | 10 % off: wrong but related |
| `721453` | `1,200,000,000` | 1 | 0 | wrong |
| `14.5%` | `0.145` | 7 | 0 | same value |
| `yes` (accepted: `match`, `1`) | `These are the same product.` | 7 | 0 | a clear yes |
| `yes` | `Probably the same product.` | 7 | 1 | yes, hedged |
| `no` | `Yes` | 1 | 0 | opposite |
| `customer_id` (accepted: `cust_id`) | `cust_id` | 7 | 0 | accepted alternative |
| `customer_id` | `custmer_id` | 6 | 0 | typo |
| `Paris, France` | `Paris` | 5 | 0 | under-specified, still unambiguous |
| `net revenue` | `revenue` | 4 | 0 | more general |
| `order_date` | `ship_date` | 2 | 0 | related column, wrong one |
| `Paris` | `Paris or Lyon` | 4 | 1 | right answer beside a wrong one |
| list `apple; pear; fig` | `apple, fig, pear` | 7 | 0 | complete, any order |
| list `apple; pear; fig` | `apple, pear` | 5 | 0 | two of three, none wrong |
| list `apple; pear; fig; plum` | `apple, pear` | 4 | 0 | half, none wrong |
| list `apple; pear; fig` | `apple, pear, fig, kiwi` | 4 | 0 | all present, one wrong extra |
| list `apple; pear; fig` | `apple, kiwi, lime` | 2 | 0 | more wrong than right |
| sentence: "Revenue rose 12 % to 4.1 billion in 2021." | `Revenue grew about 12 percent in 2021, reaching $4.1bn.` | 7 | 0 | same fact |
| same | `Revenue rose 12 % to roughly 4 billion in 2021.` | 6 | 0 | a rounded figure |
| same (question asked for growth and level) | `Revenue rose 12 % in 2021.` | 5 | 0 | main fact, one asked detail missing |
| same | `Revenue was 4.1 billion in 2021 after falling 12 %.` | 4 | 0 | half right, half wrong |
| same | `Revenue fell to 4.1 billion in 2021.` | 3 | 0 | main fact wrong, a detail right |
| same | `Revenue fell in 2021.` | 1 | 0 | contradicts |
| any | `I cannot determine this from the table.` | 1 | 0 | refusal |

## 6. How the work runs

1. **Background and assignment.** Read the one-page brief and fill the short background form. You are identified by your email address: use the same address on every form and in the names of files you send back.
2. **Pilot (30 rows, about 25 minutes).** Every labeller grades the same pilot rows independently. We then compare, discuss the rows where labels differed most, and clarify the guide if a rule was unclear. Nothing from the pilot is reused.
3. **Main round.** The answers come in blocks of 50 (one online form, or one value of the `block` column). You do whole blocks, as many as you agreed; take the blocks that still need graders. At most two blocks in one sitting. Keep a steady pace; about 45 seconds per row is typical. Fill `rating` and `hedged` on every row; use `note` sparingly.
4. **Adjudication.** Rows where the labels are spread over more than two ratings, or where a label is missing, go to an adjudicator with all ratings and notes. The adjudicated value is final.

## 7. What we report

Agreement between labellers (Krippendorff's α on the rating and on hedged, exact and within-one-rating agreement, each with confidence intervals), the number of adjudicated rows, and then the correlation between the automatic scorer and your labels. Your labels are stored by row id only and are never attributed to you by name in the paper.

Questions about a specific row: write them in `note` and keep going; do not stop to ask.
