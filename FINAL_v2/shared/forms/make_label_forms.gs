/**
 * Google Apps Script: build the labelling forms from a sheet that holds one of the labelling CSVs.
 *
 * Setup (once):
 *   1. Drive: New > Google Sheets > File > Import > Upload > data/labels/labeller_sheet.csv (main) or pilot_30.csv (pilot).
 *      Header row = row 1.  Name the tab "rows".
 *   2. Upload the contents of data/labels/forms_images/ (made by shared/scripts/06_render_row_images.py) to a Drive folder named as
 *      IMAGE_FOLDER below: one card per answer (<row_id>.png), scale_table.png and scale_strip.png.
 *   3. Extensions > Apps Script.  Paste this file.  Run buildBackgroundForm() once, then buildForms(), then refreshAllocation().
 *      buildForms() stops itself after about four minutes (Apps Script's limit is six): run it again, or add a time-driven trigger
 *      every 10 minutes, and it continues with the forms not yet marked DONE in the "forms" tab.
 *
 * There are no grader letters and no fixed number of graders.  Every form starts with "Your grader ID": a short ID the grader
 * chooses (for example initials and two digits) and repeats on every form.  Anyone with the links can take part; each grader does
 * whole forms ("blocks"), as many as agreed.
 *
 *   buildBackgroundForm()  "Grader background and assignment": the study in a paragraph, what the grader is asked to do, then
 *                          grader ID, professional background, a familiarity grid and the ground rules.
 *   buildForms()           one form per block of the sheet (the `block` column; BATCH rows when the sheet has none).
 *                          Page 1: grader ID, how to grade in four lines, the scale table.
 *                          Then one page per answer, in this order:
 *                            the answer card (question, reference, the system's final answer, the table or the two records);
 *                            the 1-7 legend strip;  "<row_id> · Rating": a 1-7 scale row, 1 = wrong or no answer ... 7 = correct;
 *                            "<row_id> · Hedged?": No / Yes;  "<row_id> · Note": optional;
 *                            the system's full reply at the bottom, for the rare case the final line needs checking.
 *                          Graders record 1-7; the scripts convert to a 0-1 utility afterwards, (rating - 1) / 6.
 *   refreshAllocation()    tab "allocation": every form with its link, how many graders have submitted it so far and how many more
 *                          it needs to reach TARGET_PER_FORM.  Share this tab as the work list ("take the block with the fewest
 *                          graders"); run it again whenever you want the counts updated, or put it on an hourly trigger.
 *
 * Collecting: each form > Responses > three dots > Download responses (.csv), all into one folder, then
 *   uv run python shared/scripts/05_forms_to_returned.py path/to/csvs/*.csv        (add --pilot for the pilot form)
 */
var BATCH = 50;                        // rows per form when the sheet has no `block` column
var FORM_PREFIX = "Answer grading";    // "Answer grading, pilot" for the pilot sheet
var FOLDER_NAME = "labelling_forms";   // Drive folder that receives the forms (created if absent)
var IMAGE_FOLDER = "labelling_images"; // Drive folder with <row_id>.png cards, scale_table.png, scale_strip.png
var LEGEND_ON_EVERY_PAGE = true;       // the 1-7 legend strip above every rating question (false: only the text hint)
var TEXT_WITH_IMAGES = false;          // true: also print the table and context as text under the card
var MAXLEN = 3500;                     // characters per read-only text item; longer material is split over several items
var TARGET_PER_FORM = 3;               // graders wanted per form (allocation tab)
var HOURS_PER_ROW = 45 / 3600;
var SCALE = [  // rating, name, definition (graders record the rating; utility = (rating - 1) / 6 is computed afterwards)
  [7, "Correct", "Same answer as the reference. Formatting, wording, list order and harmless extra words do not matter."],
  [6, "Correct, cosmetic defect", "Right answer with a blemish that does not change the meaning: rounding within 1 %, a typo, 'about'."],
  [5, "Mostly correct", "Right answer with a small part missing or slightly imprecise; most list items, none wrong."],
  [4, "Half correct", "About half of the required answer; right quantity in the wrong unit or scale; a right answer beside a wrong one."],
  [3, "Mostly wrong, near miss", "Only a small part right, or a near miss: number 1-5 % off or one digit wrong; under half of a list."],
  [2, "Wrong but related", "Right question and form, wrong content: number more than 5 % off or wrong sign, neighbouring cell, confusable entity."],
  [1, "Wrong or no answer", "Different value or name, opposite yes/no, refusal, no final answer."]
];
var SCALE_TEXT = SCALE.map(function (s) { return s[0] + "  " + s[1] + ": " + s[2]; }).join("\n");
var SCALE_LINE = SCALE.slice().reverse().map(function (s) { return s[0] + " " + s[1].toLowerCase(); }).join("  ·  ");
var ID_HELP = "Choose a short ID, for example your initials and two digits (ab12). Use exactly the same ID on every form.";

function graderIdItem(form) {
  var v = FormApp.createTextValidation().setHelpText("2 to 20 letters, digits, - or _ (no spaces)").requireTextMatchesPattern("[A-Za-z0-9_-]{2,20}").build();
  return form.addTextItem().setTitle("Your grader ID").setHelpText(ID_HELP).setValidation(v).setRequired(true);
}

function readableTable(text) {
  // text fallback when no card image: "A | B | C" rows -> one block per row with "column: value" lines
  var lines = String(text).split("\n"); var out = []; var header = null; var n = 0;
  lines.forEach(function (ln) {
    var t = ln.trim();
    if (!t) { out.push(""); return; }
    if (/^[-=+| ]+$/.test(t) && t.indexOf("-") >= 0) return;
    if (t.indexOf("|") < 0) { out.push(t); header = null; return; }
    var cells = t.replace(/^\||\|$/g, "").split("|").map(function (c) { return c.trim(); });
    if (!header) { header = cells; n = 0; out.push("columns: " + header.join(" | ")); return; }
    n += 1;
    var pairs = cells.map(function (c, i) { return (header[i] || ("col" + (i + 1))) + ": " + c; });
    out.push(pairs.length <= 4 ? "[row " + n + "]  " + pairs.join("  |  ") : "[row " + n + "]\n   " + pairs.join("\n   "));
  });
  return out.join("\n");
}

function addChunked(form, title, text) {
  var parts = []; var cur = "";
  String(text).split("\n").forEach(function (ln) {
    if ((cur + ln).length > MAXLEN - 1 && cur) { parts.push(cur); cur = ""; }
    cur += (cur ? "\n" : "") + ln.substring(0, MAXLEN - 1);
  });
  if (cur) parts.push(cur);
  parts.forEach(function (p, i) { form.addSectionHeaderItem().setTitle(title + (parts.length > 1 ? " (" + (i + 1) + "/" + parts.length + ")" : "")).setHelpText(p); });
}

var IMAGES = null;
function imageFor(name) {
  if (IMAGES === null) {
    IMAGES = {}; var fs = DriveApp.getFoldersByName(IMAGE_FOLDER);
    if (fs.hasNext()) { var it = fs.next().getFiles(); while (it.hasNext()) { var f = it.next(); IMAGES[f.getName().replace(/\.png$/i, "")] = f; } }
  }
  return IMAGES[name] || null;
}

function targetFolder() {
  var folders = DriveApp.getFoldersByName(FOLDER_NAME); return folders.hasNext() ? folders.next() : DriveApp.createFolder(FOLDER_NAME);
}

function moveToFolder(form, folder) {
  var f = DriveApp.getFileById(form.getId()); folder.addFile(f); DriveApp.getRootFolder().removeFile(f);
}

function rowsData() {
  var sh = SpreadsheetApp.getActiveSpreadsheet().getSheetByName("rows");
  var data = sh.getDataRange().getValues(); var head = data[0]; var col = {};
  head.forEach(function (h, i) { col[h] = i; });
  var rows = data.slice(1).filter(function (r) { return String(r[col.row_id]).trim() !== ""; });  // drop blank trailing rows
  var groups = [];  // blocks in sheet order
  if (col.block !== undefined) {
    var seen = {};
    rows.forEach(function (r) { var b = String(r[col.block]); if (!(b in seen)) { seen[b] = groups.length; groups.push([]); } groups[seen[b]].push(r); });
  } else { for (var i = 0; i < rows.length; i += BATCH) groups.push(rows.slice(i, i + BATCH)); }
  return { rows: rows, col: col, blocks: groups };
}

function buildForms() {
  var ss = SpreadsheetApp.getActiveSpreadsheet(); var d = rowsData(); var col = d.col; var folder = targetFolder();
  // resume support: a form is listed in the "forms" tab as BUILDING when started and DONE when finished; a BUILDING leftover from a
  // run that was cut off is trashed and rebuilt
  var tab = ss.getSheetByName("forms") || ss.insertSheet("forms"); var done = {};
  if (tab.getLastRow() < 1) tab.appendRow(["block", "form", "answers", "edit url", "respondent url", "status", "form id"]);
  var listed = tab.getDataRange().getValues();
  for (var i = listed.length - 1; i >= 1; i--) {
    if (listed[i][5] === "DONE") done[listed[i][1]] = true;
    else { try { DriveApp.getFileById(listed[i][6]).setTrashed(true); } catch (e) {} tab.deleteRow(i + 1); }
  }
  var t0 = Date.now(); var LIMIT_MS = 3.5 * 60 * 1000; var stopped = false;
  var scaleImg = imageFor("scale_table"); var strip = LEGEND_ON_EVERY_PAGE ? imageFor("scale_strip") : null; var stripBlob = strip ? strip.getBlob() : null;
  var nb = d.blocks.length;
  for (var b = 0; b < nb && !stopped; b++) {
    var rows = d.blocks[b];
    var title = FORM_PREFIX + (nb > 1 ? ", block " + (b + 1) + " of " + nb : "");
    if (done[title]) continue;
    if (Date.now() - t0 > LIMIT_MS) { stopped = true; break; }
    var form = FormApp.create(title);
    tab.appendRow([b + 1, title, rows.length, "", "", "BUILDING", form.getId()]); var tabRow = tab.getLastRow(); SpreadsheetApp.flush();
    form.setDescription(rows.length + " answers, about " + Math.round(rows.length * HOURS_PER_ROW * 60) + " minutes. One answer per page: read the card, give a rating from 1 to 7, say whether the answer hedges, press Next.");
    form.setProgressBar(true); form.setAllowResponseEdits(true); form.setLimitOneResponsePerUser(false); form.setShowLinkToRespondAgain(false);
    form.setConfirmationMessage("Thank you: " + title + " is recorded. You can edit your response with the link on this page. Pick your next block from the allocation sheet.");
    graderIdItem(form);
    form.addSectionHeaderItem().setTitle("How to grade").setHelpText(
      "1. Grade the system's FINAL answer (yellow on the card) against the reference answer (green). Not the reasoning, not the writing.\n" +
      "2. Rating: 7 = I would accept it as the reference answer, 4 = half of it is right, 1 = nothing is right. Between two neighbouring ratings, choose the lower. Yes/no answers are only 7 or 1.\n" +
      "3. Hedged = Yes when the final answer offers more than one candidate, a range where one value was asked, or will not commit.\n" +
      "4. Do not look anything up. If you doubt the reference, grade against it anyway and leave a note.");
    if (scaleImg) form.addImageItem().setTitle("The scale").setImage(scaleImg.getBlob());
    else form.addSectionHeaderItem().setTitle("The scale").setHelpText(SCALE_TEXT);
    rows.forEach(function (r, k) {
      var rid = r[col.row_id]; var img = imageFor(rid);
      var fields = "Task: " + r[col.task_family] + "\nSource: " + r[col.dataset_description] + "\nAnswer type: " + r[col.answer_type] +
        (r[col.choices] ? "\nChoices: " + r[col.choices] : "") +
        "\n\nQUESTION:\n" + r[col.question] +
        "\n\nREFERENCE ANSWER:\n" + r[col.gold_answer] +
        (r[col.accepted_alternatives] ? "\nAlso accepted: " + r[col.accepted_alternatives] : "") +
        (r[col.gold_is_a_list] ? "\nThe reference is a list: every item required." : "") +
        "\n\nSYSTEM'S FINAL ANSWER (grade this):\n" + (r[col.model_final_answer] || "(no final answer)");
      var page = form.addPageBreakItem().setTitle("Answer " + (k + 1) + " of " + rows.length);
      if (img) { form.addImageItem().setTitle(rid).setImage(img.getBlob()); }
      else { page.setHelpText(fields.substring(0, MAXLEN)); }
      if (!img || TEXT_WITH_IMAGES) {
        if (r[col.table]) addChunked(form, "Table", readableTable(r[col.table]));
        if (r[col.context]) addChunked(form, "Context", r[col.context]);
      }
      if (stripBlob) form.addImageItem().setTitle("Rating guide").setImage(stripBlob);
      form.addScaleItem().setTitle(rid + " · Rating").setHelpText(stripBlob ? "How correct is the final answer?" : "How correct is the final answer?\n" + SCALE_LINE)
        .setBounds(1, 7).setLabels("Wrong or no answer", "Correct").setRequired(true);
      form.addMultipleChoiceItem().setTitle(rid + " · Hedged?").setHelpText("More than one candidate, a range where one value was asked, or no commitment.")
        .setChoiceValues(["No", "Yes"]).setRequired(true);
      form.addTextItem().setTitle(rid + " · Note").setHelpText("Optional. A few words when unsure or when the rules did not fit.").setRequired(false);
      addChunked(form, "Only if needed: the system's full reply", r[col.model_full_reply]);
    });
    moveToFolder(form, folder);
    tab.getRange(tabRow, 4, 1, 3).setValues([[form.getEditUrl(), form.getPublishedUrl(), "DONE"]]); SpreadsheetApp.flush(); done[title] = true;
  }
  if (stopped) Logger.log("time limit near after " + Object.keys(done).length + " forms: run buildForms again to continue");
  else Logger.log("all forms built: " + Object.keys(done).length);
}

function buildBackgroundForm() {
  // Background + assignment: what the study is, what the grader is asked to do, who the grader is.  One response per grader.
  var n = 0, nForms = 0; try { var d = rowsData(); n = d.rows.length; nForms = d.blocks.length; } catch (e) {}
  var perForm = nForms ? Math.round(n / nForms) : BATCH;
  var form = FormApp.create("Grader background and assignment");
  form.setDescription(
    "BACKGROUND\nWe are testing an automatic scoring program that marks answers given by AI systems to questions about tables, " +
    "documents and data records (matching records, matching columns, answering questions from tables and financial filings). " +
    "To know whether the program can be trusted, we compare its marks with the judgement of people who work with such data. " +
    "Each answer is graded independently by several graders.\n\n" +
    "YOUR ASSIGNMENT\n" +
    "1. Read the labelling guide (about 15 minutes) and fill this form (5 minutes).\n" +
    "2. Pilot: grade 30 practice answers in the pilot form (about 25 minutes), then join a short review call.\n" +
    "3. Main round: grade whole blocks from the allocation sheet, as many as you agreed" +
    (n ? " (" + nForms + " blocks of about " + perForm + " answers, about " + Math.round(perForm * HOURS_PER_ROW * 60) + " minutes each)" : "") +
    ". Take the blocks that have the fewest graders so far.\n" +
    "For each answer you give a rating from 1 (wrong or no answer) to 7 (correct) and say whether it hedges; every rating is defined on the form.\n\n" +
    "You never see which AI system wrote an answer. Your ratings are stored under your grader ID only; you are not named in any publication.");
  form.setLimitOneResponsePerUser(false); form.setAllowResponseEdits(true);
  form.setConfirmationMessage("Thank you. Next: the pilot form.");
  graderIdItem(form);
  form.addTextItem().setTitle("Current role or profession").setHelpText("For example: financial analyst, data engineer, accountant, data annotator, graduate student in statistics.").setRequired(true);
  form.addMultipleChoiceItem().setTitle("Years of professional work with data tables, databases or financial documents")
    .setChoiceValues(["less than 1", "1 to 3", "4 to 7", "8 to 15", "more than 15"]).setRequired(true);
  form.addTextItem().setTitle("Highest degree and field").setRequired(false);
  form.addGridItem().setTitle("How familiar are you with each kind of task?").setHelpText("One answer per line.")
    .setRows(["Deciding whether two records are the same product, person or publication (entity matching)",
              "Mapping a column of one table to a column of another (schema matching)",
              "Answering questions by reading a table",
              "Reading financial statements and filings"])
    .setColumns(["Never done it", "Occasionally", "Regularly", "It is my job"]).setRequired(true);
  form.addMultipleChoiceItem().setTitle("English reading level").setChoiceValues(["Native", "Fluent", "Working knowledge"]).setRequired(true);
  form.addMultipleChoiceItem().setTitle("Have you graded or annotated data before?").setChoiceValues(["No", "Yes, once or twice", "Yes, regularly"]).setRequired(true);
  form.addCheckboxGridItem().setTitle("Ground rules: tick each line to confirm").setHelpText("All four are needed before you start.")
    .setRows(["I have read the labelling guide",
              "I will grade on my own and not discuss answers with other graders before the pilot review",
              "I will not look anything up: I grade only against the reference and the material shown",
              "I will grade the final answer, not the reasoning or the writing"])
    .setColumns(["Yes"]).setRequired(true);
  form.addTextItem().setTitle("How many blocks do you plan to grade, and by when?").setRequired(false);
  form.addParagraphTextItem().setTitle("Anything we should know (optional)").setRequired(false);
  moveToFolder(form, targetFolder());
  var ss = SpreadsheetApp.getActiveSpreadsheet(); var tab = ss.getSheetByName("background_form") || ss.insertSheet("background_form");
  tab.clear(); tab.getRange(1, 1, 2, 3).setValues([["edit url", "respondent url", "form id"], [form.getEditUrl(), form.getPublishedUrl(), form.getId()]]);
  Logger.log("background form: " + form.getPublishedUrl());
}

function gradersOf(formId) {
  // distinct grader IDs (lower case) that have submitted this form
  var ids = {};
  try {
    FormApp.openById(formId).getResponses().forEach(function (resp) {
      var its = resp.getItemResponses();
      for (var i = 0; i < its.length; i++) { if (its[i].getItem().getTitle() === "Your grader ID") { ids[String(its[i].getResponse()).trim().toLowerCase()] = true; break; } }
    });
  } catch (e) {}
  return Object.keys(ids).sort();
}

function refreshAllocation() {
  // Run after buildForms, and again whenever the counts should be updated.  Writes the tab "allocation": the work list to share with
  // graders (respondent links only): every form, who has done it, and how many more graders it needs.
  var ss = SpreadsheetApp.getActiveSpreadsheet(); var forms = ss.getSheetByName("forms");
  if (!forms) { Logger.log("run buildForms first"); return; }
  var listed = forms.getDataRange().getValues().slice(1).filter(function (r) { return r[5] === "DONE"; });
  var tab = ss.getSheetByName("allocation") || ss.insertSheet("allocation"); tab.clear();
  var bg = ss.getSheetByName("background_form"); var out = [["block", "form", "answers", "about (min)", "link", "graders so far", "still needed", "done by"]];
  if (bg && bg.getLastRow() >= 2) { var g0 = gradersOf(bg.getRange(2, 3).getValue()); out.push(["", "Grader background and assignment (everyone, first)", "", 5, bg.getRange(2, 2).getValue(), g0.length, "", g0.join(", ")]); }
  var all = {}; var total = 0;
  listed.forEach(function (r) {
    var g = gradersOf(r[6]); g.forEach(function (x) { all[x] = true; }); total += Number(r[2]);
    out.push([r[0], r[1], r[2], Math.round(r[2] * HOURS_PER_ROW * 60), r[4], g.length, Math.max(0, TARGET_PER_FORM - g.length), g.join(", ")]);
  });
  tab.getRange(1, 1, out.length, out[0].length).setValues(out);
  tab.getRange(1, 1, 1, out[0].length).setFontWeight("bold"); tab.setFrozenRows(1); tab.setColumnWidth(2, 330); tab.setColumnWidth(5, 380); tab.setColumnWidth(8, 260);
  tab.getRange(out.length + 2, 2).setValue("Take the block with the highest 'still needed' (fewest graders so far) and do the whole block. " + listed.length + " blocks, " + total +
    " answers; target " + TARGET_PER_FORM + " graders per block. Graders so far: " + Object.keys(all).length + ". Updated " + new Date().toLocaleString() + ".");
  Logger.log("allocation tab written: " + listed.length + " forms, " + Object.keys(all).length + " graders");
}
