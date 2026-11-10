# Returned labels

One file per grader, named with the grader's own ID (lower-case letters, digits, underscore):

    02_pilot_<grader id>.xlsx (or .csv)      03_main_<grader id>.xlsx (or .csv)

Spreadsheet route: graders send these files; rename on receipt if a grader did not. A newer file from the same grader replaces the older one.
Google Forms route: `uv run python shared/scripts/05_forms_to_returned.py [--pilot] responses/*.csv` writes one file per grader ID found in the responses.

Then, from FINAL_v2:

    uv run python shared/scripts/03_label_agreement.py --check all [--pilot]   # validate every returned file
    uv run python shared/scripts/03_label_agreement.py --pilot                 # pilot agreement + pilot_adjudication_queue.csv (for the review call)
    uv run python shared/scripts/03_label_agreement.py                         # agreement, coverage.csv (blocks that need graders), adjudication_queue.csv, human_labels.csv

Aggregation (mean / median / mode / trimmed, minimum ratings per answer, what counts as a wide disagreement, adjudicate or not, graders to
exclude) is set in `config/labelling.toml` or by flags. The adjudicator resolves the queue in `data/labels/adjudicated.csv`
(columns row_id, rating, hedged; rating 1 to 7); re-run the script to merge.

Then `bash paper/scripts/rebuild_all.sh --paper` (adds tables/human_correctness.tex to the v2 Overleaf package); optionally
v6_top30_significance/v5_metric_library/scripts/02_select_metrics.py --labels data/labels/human_labels.csv.
