/**
 * Google Apps Script: build labelling forms from a sheet that holds one of the labelling CSVs.
 *
 * Setup (once, about 10 minutes):
 *   1. In Google Drive: New > Google Sheets > File > Import > Upload > labeller_sheet.csv (the canonical main sheet) or pilot_30.csv.
 *      Keep the header row as row 1.  Name the tab "rows".
 *   2. Extensions > Apps Script.  Paste this file.  Set BATCH, FORM_PREFIX and the folder below.  Run buildForms().  Authorise when asked.
 *   3. The script writes a tab "forms" with the edit and the respondent links of every form it created.
 *
 * Design: one form per batch of BATCH rows.  Question 1 asks the labeller's letter, so labellers can fill the SAME forms.
 * With many labellers and an "assignments" tab (columns row_id, labeller; import data/labels/assignments.csv), the script instead builds
 * one set of forms PER LABELLER holding only that person's rows, and the letter question is pre-limited to that letter.
 * Each row becomes its own page: a section whose title is the row_id and whose description shows the task, question, gold answer,
 * accepted alternatives, the list flag and the model's final answer, followed by three questions titled "<row_id> | utility",
 * "<row_id> | hedged" (both required multiple choice) and "<row_id> | note" (optional short text).  Context, table and full reply
 * are shown in a separate read-only text item, cut to MAXLEN characters (Forms limits item text); the spreadsheet remains the
 * reference for anything longer.
 *
 * Collecting: each form > Responses > three dots > Download responses (.csv).  Put all CSVs in one folder and run
 *   uv run python shared/scripts/05_forms_to_returned.py --labeller A path/to/csvs/*.csv        (add --pilot for the pilot forms)
 * which rebuilds data/labels/returned/03_main_A.csv (or 02_pilot_A.csv) in the format the agreement script reads.
 */
var BATCH = 50;                       // rows per form (401 rows -> 9 forms; 30 pilot rows -> 1 form)
var FORM_PREFIX = "Labelling, main";  // "Labelling, pilot" for the pilot sheet
var FOLDER_NAME = "labelling_forms";  // Drive folder that receives the forms (created if absent)
var MAXLEN = 3500;                    // characters of context/table/reply shown per row
var LEVELS = ["1", "0.75", "0.5", "0.25", "0"];
var LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ".split("");

function buildForms() {
  var ss = SpreadsheetApp.getActiveSpreadsheet(); var sh = ss.getSheetByName("rows");
  var data = sh.getDataRange().getValues(); var head = data[0]; var col = {};
  head.forEach(function (h, i) { col[h] = i; });
  var folders = DriveApp.getFoldersByName(FOLDER_NAME); var folder = folders.hasNext() ? folders.next() : DriveApp.createFolder(FOLDER_NAME);
  var out = [["labeller", "form", "rows", "edit url", "respondent url"]];
  var asg = ss.getSheetByName("assignments");
  var groups = [];  // [{letter, rows}]
  if (asg) {
    var a = asg.getDataRange().getValues(); var byL = {};
    for (var i = 1; i < a.length; i++) { (byL[a[i][1]] = byL[a[i][1]] || {})[a[i][0]] = true; }
    Object.keys(byL).sort().forEach(function (L) { groups.push({ letter: L, rows: data.slice(1).filter(function (r) { return byL[L][r[col.row_id]]; }) }); });
  } else { groups.push({ letter: null, rows: data.slice(1) }); }
  groups.forEach(function (g) {
    var nb = Math.ceil(g.rows.length / BATCH);
    for (var b = 0; b < nb; b++) {
      var rows = g.rows.slice(b * BATCH, (b + 1) * BATCH);
      var title = FORM_PREFIX + (g.letter ? ", labeller " + g.letter : "") + ", batch " + (b + 1) + " of " + nb + " (" + rows[0][col.row_id] + " to " + rows[rows.length - 1][col.row_id] + ")";
      var form = FormApp.create(title);
      form.setDescription("Grade the system's FINAL answer against the reference, following the labelling guide. utility: 1 correct, 0.75 minor defect, 0.5 partly correct, 0.25 wrong but close, 0 wrong or empty. hedged: 1 if the final answer offers more than one candidate, a range, or declines to commit.");
      form.setProgressBar(true); form.setAllowResponseEdits(true); form.setLimitOneResponsePerUser(false);
      form.addMultipleChoiceItem().setTitle("Your labeller letter").setChoiceValues(g.letter ? [g.letter] : LETTERS).setRequired(true);
      rows.forEach(function (r) {
        var rid = r[col.row_id];
        var desc = "Task: " + r[col.task_family] + "\nSource: " + r[col.dataset_description] + "\nAnswer type: " + r[col.answer_type] +
          (r[col.choices] ? "\nChoices: " + r[col.choices] : "") +
          "\n\nQUESTION:\n" + r[col.question] +
          "\n\nREFERENCE ANSWER:\n" + r[col.gold_answer] +
          (r[col.accepted_alternatives] ? "\nAccepted alternatives: " + r[col.accepted_alternatives] : "") +
          (r[col.gold_is_a_list] ? "\nThe reference is a list: every item required." : "") +
          "\n\nSYSTEM'S FINAL ANSWER (grade this):\n" + r[col.model_final_answer];
        form.addPageBreakItem().setTitle(rid).setHelpText(desc.substring(0, MAXLEN));
        var mat = "";
        if (r[col.context]) mat += "CONTEXT:\n" + r[col.context] + "\n\n";
        if (r[col.table]) mat += "TABLE:\n" + r[col.table] + "\n\n";
        mat += "FULL REPLY (for checking the final line only):\n" + r[col.model_full_reply];
        form.addSectionHeaderItem().setTitle("Material shown to the system (open only if needed)").setHelpText(mat.substring(0, MAXLEN) + (mat.length > MAXLEN ? "\n[... cut; the spreadsheet has the full text ...]" : ""));
        form.addMultipleChoiceItem().setTitle(rid + " | utility").setChoiceValues(LEVELS).setRequired(true);
        form.addMultipleChoiceItem().setTitle(rid + " | hedged").setChoiceValues(["0", "1"]).setRequired(true);
        form.addTextItem().setTitle(rid + " | note").setRequired(false);
      });
      var f = DriveApp.getFileById(form.getId()); folder.addFile(f); DriveApp.getRootFolder().removeFile(f);
      out.push([g.letter || "all", title, rows.length, form.getEditUrl(), form.getPublishedUrl()]);
    }
  });
  var tab = ss.getSheetByName("forms") || ss.insertSheet("forms"); tab.clear(); tab.getRange(1, 1, out.length, 5).setValues(out);
}
