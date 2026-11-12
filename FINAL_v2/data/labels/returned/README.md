# Returned labels

One file per grader, named with the grader's code (g01, g02, ...), never with a name or an address:

    02_pilot_<code>.xlsx (or .csv)      03_main_<code>.xlsx (or .csv)

Graders are identified by email address. `shared/scripts/05_forms_to_returned.py` turns addresses into codes and writes the files here;
do not copy files in by hand. The address-to-code table is data/labels/grader_registry.csv (git-ignored, private).

Google Forms route:   `uv run python shared/scripts/05_forms_to_returned.py [--pilot] responses/*.csv`
Spreadsheet route:    `uv run python shared/scripts/05_forms_to_returned.py --sheets inbox/03_main_<address>.xlsx ...` (keep the inbox outside the repository)
Background forms:     `uv run python shared/scripts/05_forms_to_returned.py --background background.csv [inbox/00_BACKGROUND_FORM_<address>.xlsx ...]`

Then, from FINAL_v2:

    uv run python shared/scripts/03_label_agreement.py --check all [--pilot]   # validate every returned file
    uv run python shared/scripts/03_label_agreement.py --pilot                 # pilot agreement + pilot_adjudication_queue.csv (for the review call)
    uv run python shared/scripts/03_label_agreement.py                         # agreement, coverage.csv (blocks that need graders), adjudication_queue.csv, human_labels.csv

Aggregation (mean / median / mode / trimmed, minimum ratings per answer, what counts as a wide disagreement, adjudicate or not, graders to
exclude) is set in `config/labelling.toml` or by flags. The adjudicator resolves the queue in `data/labels/adjudicated.csv`
(columns row_id, rating, hedged; rating 1 to 7); re-run the script to merge.

Then `bash paper/scripts/rebuild_all.sh --paper` (adds tables/human_correctness.tex to the v2 Overleaf package); optionally
v6_top30_significance/v5_metric_library/scripts/02_select_metrics.py --labels data/labels/human_labels.csv.
