# Returned labels

Every grader returns the same two files; name them with the grader's letter (A to T) on receipt if the grader did not:

    02_pilot_<letter>.xlsx (or .csv)      03_main_<letter>.xlsx (or .csv)

Validate each file first: `uv run python shared/scripts/03_label_agreement.py [--pilot] --check <letter>`.
Google Forms responses: convert with `shared/scripts/05_forms_to_returned.py --labeller <letter> [--pilot] responses/*.csv` first.

Then, from FINAL_v2:

    uv run python shared/scripts/03_label_agreement.py --pilot    # pilot agreement + pilot_adjudication_queue.csv (for the review call)
    uv run python shared/scripts/03_label_agreement.py            # main agreement + adjudication_queue.csv
    # resolve the queue into data/labels/adjudicated.csv (columns row_id, utility, hedged), then
    uv run python shared/scripts/03_label_agreement.py            # merges into data/labels/human_labels.csv + human_correctness.{csv,json}

Then `bash paper/scripts/rebuild_all.sh --paper` (adds tables/human_correctness.tex to the v2 Overleaf package); optionally
v6_top30_significance/v5_metric_library/scripts/02_select_metrics.py --labels data/labels/human_labels.csv.
