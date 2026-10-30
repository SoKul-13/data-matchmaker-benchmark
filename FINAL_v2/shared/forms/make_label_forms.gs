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
 * Readability: tables arrive as pipe-delimited text ("No. | Event | Time" with a dashed rule), which Forms' proportional font
 * garbles.  readableTable() rewrites each table as record-style text, one line per cell ("Event: 1500 m freestyle"), and long
 * material is split over several read-only items of at most MAXLEN characters, so nothing is cut.  If a Drive folder named
 * IMAGE_FOLDER exists and holds <row_id>.png (made by shared/scripts/06_render_row_images.py, uploaded by you), that image of the
 * original table and context is shown on the row's page as well.
 *
 * Collecting: each form > Responses > three dots > Download responses (.csv).  Put all CSVs in one folder and run
 *   uv run python shared/scripts/05_forms_to_returned.py --labeller A path/to/csvs/*.csv        (add --pilot for the pilot forms)
 * which rebuilds data/labels/returned/03_main_A.csv (or 02_pilot_A.csv) in the format the agreement script reads.
 */
var BATCH = 50;                       // rows per form (401 rows -> 9 forms; 30 pilot rows -> 1 form)
var FORM_PREFIX = "Labelling, main";  // "Labelling, pilot" for the pilot sheet
var FOLDER_NAME = "labelling_forms";  // Drive folder that receives the forms (created if absent)
var MAXLEN = 3500;                    // characters per read-only item; longer material is split over several items
var IMAGE_FOLDER = "labelling_images"; // optional Drive folder with <row_id>.png renderings of table + context
var LEVELS = ["1", "0.75", "0.5", "0.25", "0"];
var LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ".split("");

function readableTable(text) {
  // "Table: title\nA | B | C\n-----\n1 | x | y" -> "Table: title\n[row 1]  A: 1 | B: x | C: y" ... one line per cell when wide
  var lines = String(text).split("\n"); var out = []; var header = null; var n = 0;
  lines.forEach(function (ln) {
    var t = ln.trim();
    if (!t) { out.push(""); return; }
    if (/^[-=+| ]+$/.test(t) && t.indexOf("-") >= 0) return;            // dashed rule under the header
    if (t.indexOf(" | ") < 0 && t.indexOf("|") < 0) { out.push(t); header = null; return; }  // title or prose line
    var cells = t.replace(/^\||\|$/g, "").split("|").map(function (c) { return c.trim(); });
    if (!header) { header = cells; n = 0; out.push("columns: " + header.join(" | ")); return; }
    n += 1;
    var pairs = cells.map(function (c, i) { return (header[i] || ("col" + (i + 1))) + ": " + c; });
    out.push(pairs.length <= 4 ? "[row " + n + "]  " + pairs.join("  |  ") : "[row " + n + "]\n   " + pairs.join("\n   "));
  });
  return out.join("\n");
}

function addChunked(form, title, text) {
  // one read-only item per MAXLEN characters, split on line breaks
  var parts = []; var cur = "";
  String(text).split("\n").forEach(function (ln) {
    if ((cur + ln).length > MAXLEN - 1 && cur) { parts.push(cur); cur = ""; }
    cur += (cur ? "\n" : "") + ln.substring(0, MAXLEN - 1);
  });
  if (cur) parts.push(cur);
  parts.forEach(function (p, i) { form.addSectionHeaderItem().setTitle(title + (parts.length > 1 ? " (" + (i + 1) + "/" + parts.length + ")" : "")).setHelpText(p); });
}

var IMAGES = null;
function imageFor(rid) {
  if (IMAGES === null) {
    IMAGES = {}; var fs = DriveApp.getFoldersByName(IMAGE_FOLDER);
    if (fs.hasNext()) { var it = fs.next().getFiles(); while (it.hasNext()) { var f = it.next(); IMAGES[f.getName().replace(/\.png$/i, "")] = f; } }
  }
  return IMAGES[rid] || null;
}

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
        var img = imageFor(rid);
        if (img) form.addImageItem().setTitle("Table and context as shown to the system").setImage(img.getBlob());
        if (r[col.table]) addChunked(form, "Table" + (img ? " (text version)" : ""), readableTable(r[col.table]));
        if (r[col.context]) addChunked(form, "Context" + (img ? " (text version)" : ""), r[col.context]);
        addChunked(form, "Full reply (for checking the final line only)", r[col.model_full_reply]);
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
