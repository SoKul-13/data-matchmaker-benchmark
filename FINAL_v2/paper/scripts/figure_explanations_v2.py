"""Reading guide for every figure in the v2 summary report (paper/v2/main.tex, appendix A).

Each entry: what the axes encode, how to read the figure, what it shows.  Tokens in «double angle brackets» are filled with numbers
computed from the output files by make_overleaf_package.py, so the text stays correct after a re-run.  Plain LaTeX is allowed.
"""

EXPLANATIONS = {
    # ------------------------------------------------------------------ the grid
    "fig_j_histogram": r"""\textbf{What it encodes.} The horizontal axis is the agreement objective $J$ (mean Kendall $\tau$ between each dataset's model ranking and the Borda-pooled ranking); the bars count how many of the 1,771 step-0.05 weightings fall in each bin. The vertical lines mark the deployed weights (v1) and the best weighting; the shaded band is the plateau of weightings statistically indistinguishable from the best.
\textbf{How to read it.} If the weights mattered, the histogram would be wide and v1 would sit in a low tail far from the best. Instead the whole distribution spans «Jmin»--«Jmax», v1 sits at «v1J» and the best at «bestJ», and the plateau covers «plateau» of 1,771 points.
\textbf{What it shows.} The objective is flat: moving weight between F1, decay, precision and recall changes $J$ by less than the bootstrap noise of a single point, so no weighting is distinguishable from v1 on this suite.""",

    "fig_landscape": r"""\textbf{What it encodes.} Every weighting sorted from best (left) to worst (right) by $J$; the curve is $J$ itself, and the marked points are v1 and the four single-ingredient corners (F1 only, decay only, precision only, recall only).
\textbf{How to read it.} The height of the curve at any rank is the $J$ of that weighting; the vertical drop from left to right is the whole range the search could ever exploit. A rank far to the right looks bad until the vertical scale is read: v1 is at rank «v1rank» of 1,771, but the curve drops only «Jrange» from first to last.
\textbf{What it shows.} The curve is nearly horizontal until the last few dozen weightings, which are the extreme corners. Rank inside such a curve carries no information, which is why the report quotes the plateau and the out-of-bag difference instead of v1's rank.""",

    "fig_marginals": r"""\textbf{What it encodes.} Four panels, one per ingredient; each point is one weighting placed by the weight it gives that ingredient (horizontal) and its $J$ (vertical); the line is the mean $J$ at each weight level.
\textbf{How to read it.} A sloping mean line would say that more (or less) of that ingredient helps; a flat line says the ingredient's weight is irrelevant. The vertical scatter at each level is the effect of the other three weights.
\textbf{What it shows.} The mean lines drift by at most «marg_max» of $J$ across the whole range (precision is the steepest, falling as its weight approaches 1); no ingredient has a slope worth acting on, and the scatter around each line is larger than any slope.""",

    "fig_weight_pairs": r"""\textbf{What it encodes.} Six heatmaps, one per pair of ingredients; each cell is the best $J$ attainable with those two weights fixed at the cell's values and the other two weights free. The red star is v1.
\textbf{How to read it.} A ridge or a hot spot would point to a region of good weightings; a uniform colour means the pair does not constrain $J$. Only the lower-left triangle is feasible because the two weights cannot sum to more than one.
\textbf{What it shows.} The feasible triangle is uniformly coloured except for a slightly cooler edge where precision dominates. There is no ridge to follow: the best $J$ is reachable from almost any pair of values.""",

    "fig_j_pooling_rules": r"""\textbf{What it encodes.} The objective recomputed under four ways of pooling the 31 per-dataset rankings into one (Borda, Kemeny, Copeland, Bradley--Terry), each curve sorted separately from best to worst.
\textbf{How to read it.} The curves answer whether the flatness is an artefact of Borda pooling. If another rule produced a steeper curve or a clear winner, the choice of pooling rule would matter for the audit.
\textbf{What it shows.} All four curves are flat and sit within a few hundredths of each other; which weighting is ``best'' changes with the rule (v1's rank moves from «v1rank_bt» under Bradley--Terry to «v1rank_kemeny» under Kemeny), confirming that rank inside the lattice is noise.""",

    "fig_tau_native_vs_j": r"""\textbf{What it encodes.} Each weighting placed by its agreement with the datasets' own native metrics (horizontal: Kendall $\tau$ between the composite's model ranking and the native-metric ranking) and its $J$ (vertical).
\textbf{How to read it.} Points to the right rank the models the way the datasets' own metrics would; points to the top make the datasets agree with each other. A strong diagonal would mean the two criteria coincide.
\textbf{What it shows.} The correlation is weak («rho_tau_native»); v1 is among the most native-faithful weightings («v1_tau_native») while the best-$J$ weighting is slightly less so. Agreement among datasets is a different criterion from fidelity to each dataset's own metric.""",

    "fig_per_dataset_tau_rules": r"""\textbf{What it encodes.} Rows are the 31 datasets; columns are named weightings (v1, the best, the four corners, the uniform mix); each cell is that dataset's Kendall $\tau$ to the pooled ranking under that weighting (blue positive, red negative). $J$ is the column mean.
\textbf{How to read it.} A row that is red in every column is a dataset whose model ranking runs against the consensus whatever the weights; a column that is uniformly bluer than the others would be a weighting that genuinely improves agreement.
\textbf{What it shows.} Rows differ far more than columns: the same «n_neg» datasets are negative under every weighting and the same high-agreement datasets are blue everywhere. The weights redistribute a little $\tau$ between datasets; they do not change which datasets agree.""",

    # ------------------------------------------------------------------ scores and components
    "fig_model_dataset_heatmap": r"""\textbf{What it encodes.} Rows are the ten models in Bradley--Terry order under v1; columns are the 31 datasets; each cell is the model's mean v1 composite on that dataset (dark = high).
\textbf{How to read it.} Columns show how hard a dataset is for everyone (BIRD and the two OfficeQA sets are dark for all models); rows show a model's profile. A leaderboard is a summary of this matrix, so any disagreement between datasets is visible here as a row that is high in one column and low in another.
\textbf{What it shows.} Most columns are near ceiling with tiny spreads (the matching sets); the spread that separates models comes from a dozen table and document sets. No row dominates every column.""",

    "fig_model_dataset_ranks": r"""\textbf{What it encodes.} The same matrix as the score heatmap, but each column is replaced by the within-dataset rank (1 = best, ties averaged).
\textbf{How to read it.} A perfectly consistent suite would show each row as a single colour. Colour changes along a row are datasets that rank that model differently from the rest.
\textbf{What it shows.} Only the bottom rows are nearly uniform; the top three rows trade first place from column to column (no model is first on more than «max_first» datasets), which is the picture behind Kendall's $W$ of «W» among datasets.""",

    "fig_family_scores": r"""\textbf{What it encodes.} For each model, four bars: its mean v1 composite within entity matching, schema matching, table QA and finance.
\textbf{How to read it.} Compare bars of the same colour across models to see the family-specific ranking; compare the four bars of one model to see which family drives its overall mean.
\textbf{What it shows.} Entity matching is near ceiling for every model, finance is near floor for every model, and the differences between models live in table QA and schema matching. A model's overall position is therefore decided by a minority of the suite.""",

    "fig_native_vs_composite": r"""\textbf{What it encodes.} One panel per family; each answer placed by its dataset's native metric (horizontal) and its v1 composite (vertical), with cell colour showing how many answers fall there (log scale).
\textbf{How to read it.} Mass on the diagonal means the composite agrees with the native metric; mass off the diagonal is where the four ingredients give partial credit (above) or penalise (below) relative to the dataset's own rule.
\textbf{What it shows.} Entity and schema matching sit almost entirely on the diagonal corners (0,0) and (1,1): the composite is exact match there. Table QA and finance show the off-diagonal cloud of partial credit, which is the only place the weights can act.""",

    "fig_component_distributions": r"""\textbf{What it encodes.} Five panels (exact match, F1, decay, precision, recall); within each, one density curve per answer type (numeric, boolean, text, free-form).
\textbf{How to read it.} A curve concentrated at 0 and 1 means the ingredient behaves like a binary score on that answer type; mass in between is graded credit.
\textbf{What it shows.} On boolean and text golds every ingredient is binary and identical to exact match. Decay is graded only on numeric golds; F1, precision and recall are graded only on free-form and some text golds. This is the mechanical reason the weights barely matter: the ingredients differ on a minority of answers.""",

    # ------------------------------------------------------------------ selection
    "fig_nested": r"""\textbf{What it encodes.} From 1,000 item bootstraps: the in-bag $J$ of the weighting selected as best on the in-bag items, the same weighting's out-of-bag $J$, and v1's out-of-bag $J$.
\textbf{How to read it.} The gap between the first two is the optimism of selection (the winner's curse); the comparison between the second and the third is the honest test of whether searching found anything.
\textbf{What it shows.} The selected weighting looks «gap» better in-bag than out of bag, and out of bag it is «oob_diff» from v1 with a 95\,\% interval of [«oob_lo», «oob_hi»]. Searching the weights buys nothing that survives held-out items.""",

    "fig_optimism_distributions": r"""\textbf{What it encodes.} The three bootstrap distributions behind the optimism gap, as histograms over the 1,000 resamples.
\textbf{How to read it.} The in-bag distribution of the selected weighting (shifted right) is what an un-validated search would report; the two out-of-bag distributions overlap almost completely.
\textbf{What it shows.} The shift is the selection effect itself, about «gap» of $J$; the overlap of the out-of-bag distributions is why no weighting can be declared better than v1.""",

    "fig_oob_difference": r"""\textbf{What it encodes.} For each of the 1,000 resamples, the out-of-bag $J$ of the selected weighting minus the out-of-bag $J$ of v1; the vertical line is zero.
\textbf{How to read it.} Mass to the right of zero means the search beat v1 on held-out items in that resample. The mean and the 2.5--97.5 percentile interval are the paired test.
\textbf{What it shows.} The distribution is centred at «oob_diff» with the interval straddling zero; the selected weighting is ahead in only «share_ahead» of resamples.""",

    "fig_selected_weights": r"""\textbf{What it encodes.} Four histograms: the weight on each ingredient of the weighting selected as in-bag best, over the 1,000 resamples; the dotted line is v1's value.
\textbf{How to read it.} If the data pointed to a specific weighting, each histogram would be a narrow spike. Spread across the whole range means the ``best'' weighting depends on which items happen to be drawn.
\textbf{What it shows.} «ndistinct» different weightings win across the resamples, and every weight spreads over most of its range (standard deviations «sd_weights»). The selection is close to uniform over the simplex.""",

    "fig_plateau": r"""\textbf{What it encodes.} Weightings sorted by full-data $J$ (horizontal) with the 95\,\% bootstrap band of each (shaded) and the plateau boundary: the set of weightings not significantly below the best in a paired bootstrap test.
\textbf{How to read it.} A weighting is in the plateau when its band overlaps the best's in the paired sense; the boundary is where $p$ drops below .05.
\textbf{What it shows.} «plateau» of 1,771 weightings are in the plateau and v1 is inside it ($p$ = «v1p»); only the extreme precision-free, decay-dominated corner falls out. The practical plateau (within 0.02 of the best) holds «practical» weightings.""",

    "fig_plateau_oob": r"""\textbf{What it encodes.} Three curves over the sorted weightings: full-data $J$, the bootstrap mean with its band, and the mean out-of-bag $J$ when each weighting is evaluated on items it was not selected on.
\textbf{How to read it.} The vertical distance between the full-data curve and the out-of-bag curve is the optimism for every weighting, not only the winner. If the out-of-bag curve were steep, some weightings would be reliably better on new items.
\textbf{What it shows.} The out-of-bag curve is flat and noisy across the entire lattice: the ordering of weightings on the full data does not reproduce on held-out items.""",

    "fig_times_selected": r"""\textbf{What it encodes.} The twenty weightings most often chosen as in-bag best across the 1,000 resamples (labels give F1 / decay / precision / recall).
\textbf{How to read it.} A dominant weighting would be selected hundreds of times. A flat bar chart with small counts means no weighting is consistently preferred.
\textbf{What it shows.} The most-selected weighting wins only «top_sel» of 1,000 resamples, and the winners include decay-dominated, F1-dominated and recall-dominated points alike.""",

    "fig_sensitivity": r"""\textbf{What it encodes.} For v1 and for the best weighting: the $J$ at the point and the range of $J$ over all neighbours one lattice step (0.05) away.
\textbf{How to read it.} A long bar would mean a knife-edge optimum; a short bar means the neighbourhood is flat.
\textbf{What it shows.} One step moves $J$ by at most «sens_v1» around v1 and «sens_best» around the best: both sit on flat ground, and the best is not a peak but a point on a plateau.""",

    # ------------------------------------------------------------------ transfer
    "fig_lodo_tau": r"""\textbf{What it encodes.} For each dataset held out in turn: the Kendall $\tau$ between its model ranking and the pooled ranking of the other 30, under weights re-fitted without it, the full-data best, and v1.
\textbf{How to read it.} If weight search generalised, the re-fitted bars would beat v1's on most datasets. Negative bars are datasets whose ranking opposes the consensus however the weights are set.
\textbf{What it shows.} Means are «lodo_refit» (re-fitted), «lodo_best» (full best) and «lodo_v1» (v1); re-fitting helps on «lodo_wins» datasets and hurts on «lodo_losses». The same handful of sets (Alaska Camera, HiTab, Alaska schema) are negative under every rule.""",

    "fig_family_weights": r"""\textbf{What it encodes.} The four weights of v1, of the global optimum, and of the optimum fitted inside each task family.
\textbf{How to read it.} Compare the family profiles with each other and with the global point. Agreement would show the same shape in every row.
\textbf{What it shows.} The families disagree: decay dominates for schema matching, recall for table QA, precision for finance. The suite-level flatness is partly these pulls cancelling, which also explains why leave-one-family-out re-fits land far from the global best.""",

    "fig_family_j": r"""\textbf{What it encodes.} Within-family agreement $J$ (computed over that family's datasets only) under the family's own optimum, the global best and v1.
\textbf{How to read it.} The gap between the first bar and the other two is what family-specific weights would gain for that family.
\textbf{What it shows.} Within a family the datasets agree far more than across the suite (finance highest, entity matching lowest), and the family optimum beats the global best by a visible margin only for table QA and finance.""",

    # ------------------------------------------------------------------ designs
    "fig_designs": r"""\textbf{What it encodes.} For three sampling designs of 100 weightings (uniform lattice, Dirichlet-snapped, Latin hypercube) and 20 seeds each, the best $J$ found, against the exhaustive optimum.
\textbf{How to read it.} Regret is the vertical distance to the exhaustive best; the spread across seeds is the risk of an unlucky sample.
\textbf{What it shows.} Every design and every seed lands within «design_regret» of the optimum; the worst seed of any design still finds a top-«design_worst_rank» weighting. With four weights the exhaustive grid is free, so the designs serve only to show that sampling would have sufficed.""",

    "fig_design_metrics": r"""\textbf{What it encodes.} Box plots over 20 seeds of regret, centred $L_2$ discrepancy (coverage of the simplex, lower is more even) and the rank of the found best within the exhaustive grid, per design.
\textbf{How to read it.} Lower discrepancy means the sample is spread more evenly; lower regret and rank mean the sample found a better point.
\textbf{What it shows.} The three designs are interchangeable at this budget; the uniform lattice has marginally better coverage and the Latin hypercube marginally lower regret, and all three differ by less than the bootstrap noise of $J$.""",

    # ------------------------------------------------------------------ anchors
    "fig_pareto": r"""\textbf{What it encodes.} Every weighting placed by its agreement objective $J$ (horizontal) and its Spearman $\rho$ against the known utility of 31,380 synthetic answers (vertical); the Pareto front and the named points (v1, best $J$, best $\rho$, knee) are marked.
\textbf{How to read it.} If agreement and correctness pulled together, the cloud would rise to the upper right. A front that bends away means the two criteria trade off.
\textbf{What it shows.} The best-$J$ weighting is among the worst by $\rho$ («rho_bestJ») while v1 («rho_v1») sits near the $\rho$ optimum («rho_best»); across the lattice $J$ and $\rho$ correlate «J_rho_corr». Agreement is not correctness, and v1 is close to the correct end.""",

    "fig_anchor_operators": r"""\textbf{What it encodes.} Each anchor operator (a typed perturbation applied to gold answers) with its assigned utility, the mean v1 score it receives, and its exact-match rate.
\textbf{How to read it.} A perfect judge would put the blue point on the grey one for every operator. Blue above grey is over-generosity, blue below is over-severity.
\textbf{What it shows.} The ends are right (identity, verbose and tagged score 1; flips and non-answers score 0). The judge is generous to shuffled lists, supersets and list dumps (token overlap rewards extra correct tokens) and severe on typos, digit typos and medium near misses. These operators are where a human label would disagree with any lexical rule.""",

    "fig_rho_per_dataset": r"""\textbf{What it encodes.} Spearman $\rho$ between score and known utility computed within each dataset's anchors, under v1, the best-$J$ and the best-$\rho$ weightings.
\textbf{How to read it.} Datasets where the three bars differ are where the weighting changes how well the judge grades answers; equal bars mean the weighting is irrelevant there.
\textbf{What it shows.} v1 and best-$\rho$ are close everywhere; best-$J$ falls behind on the numeric and list-answer datasets, which is where decay-only weighting loses the partial credit that token overlap provides.""",

    "fig_anchor_metrics_vs_j": r"""\textbf{What it encodes.} Three anchor diagnostics against $J$ for every weighting: AUC for separating correct from wrong anchors, the mean score given to wrong anchors, and the hedge gap (score of a committed answer minus the same answer hedged).
\textbf{How to read it.} Flat clouds mean the diagnostic does not depend on the weighting; a slope means agreement trades against it.
\textbf{What it shows.} AUC is «auc_min»--«auc_max» for every weighting: all separate right from wrong. Wrong answers score below 0.06 everywhere. The differences between weightings are in partial credit, not in discrimination.""",

    # ------------------------------------------------------------------ leaderboards
    "fig_leaderboard_rules": r"""\textbf{What it encodes.} Bradley--Terry strengths (log-odds of winning an item against the reference model, with standard errors) and bootstrap rank intervals under exact match, v1 and the best-$J$ weighting.
\textbf{How to read it.} Overlapping intervals mean the order is not established; a model whose point moves between panels is one whose position depends on the scoring rule.
\textbf{What it shows.} The ends are fixed under every rule («last» last, gpt-oss-120b ninth); the top three (Gemini 3.8 Flash, Claude Opus 5, GPT-5.5) reorder with the rule. Exact match favours Opus; the graded rules favour Gemini Flash.""",

    "fig_bt_all_rules": r"""\textbf{What it encodes.} Nine small panels, one per reported rule (exact match, v1, the five best by $J$, the best by $\rho$, the Pareto knee), each showing Bradley--Terry strength $\pm$ SE for the ten models in a fixed order; the first-placed model is orange.
\textbf{How to read it.} Scan a row across panels to see whether a model's strength is stable; scan the orange markers to see who is first under which rule.
\textbf{What it shows.} Rows 4--10 barely move; first place is Opus under exact match and Gemini Flash under every graded rule. Kendall $\tau$ between the rules' rankings is «rule_tau_min»--1.00.""",

    "fig_rank_bootstrap_v1": r"""\textbf{What it encodes.} For each model, the distribution of its Bradley--Terry rank (left) and Borda rank (right) over 1,000 item bootstraps under v1.
\textbf{How to read it.} A narrow box is a rank the data pin down; a wide box is a rank that depends on which items are drawn. Overlapping boxes are models whose order is not established.
\textbf{What it shows.} Bradley--Terry pins Gemini Flash to first (P = «p_first_bt») and the last two to their places; the middle four overlap. Borda spreads first place over three models, because it counts dataset-level ranks rather than item-level wins.""",

    "fig_p_first": r"""\textbf{What it encodes.} The bootstrap probability of first place for every model under every rule, by Bradley--Terry (left) and Borda (right) pooling.
\textbf{How to read it.} Each column sums to one. A dark cell is a confident first place; a column with several mid-tone cells is a contested one.
\textbf{What it shows.} Bradley--Terry is nearly certain about Gemini Flash under the graded rules and about Opus under exact match; Borda divides first place between Opus and GPT-5.5 under most rules. The pooling method, not only the scoring rule, decides the headline winner.""",

    "fig_rule_agreement": r"""\textbf{What it encodes.} Kendall $\tau$ between the Bradley--Terry rankings produced by each pair of rules.
\textbf{How to read it.} 1.00 means identical rankings; values near 0.8 mean a few adjacent swaps.
\textbf{What it shows.} The graded rules agree with each other at «rule_tau_min» or above; exact match is the outlier because it ranks the reasoning-heavy models differently. Changing the weights inside the plateau does not change the leaderboard beyond adjacent swaps.""",

    "fig_cd_diagram_v1": r"""\textbf{What it encodes.} The Friedman test's mean rank of each model across the 31 datasets on a single axis, with the Nemenyi critical difference («cd») drawn as a bar; models closer than the critical difference are not separated at $\alpha$ = .05.
\textbf{How to read it.} Two models are significantly different only if their positions differ by more than the bar's length.
\textbf{What it shows.} The top group is separated from the bottom two; nothing inside the top group, and nothing in the middle, is separated. With 31 datasets and eleven models this is the resolution the cross-dataset test can offer.""",

    "fig_pairwise_significance_v1": r"""\textbf{What it encodes.} For each pair of models, the number of datasets (of 31) in which a Holm-corrected per-item paired test separates them under v1.
\textbf{How to read it.} A high count is a pair separated on many datasets; zero is a pair never separated at the item level even where the cross-dataset test suggests a difference.
\textbf{What it shows.} The pairs involving the bottom two models are separated on many datasets; pairs inside the top group are separated on few. Item-level evidence agrees with the Friedman picture.""",

    "fig_significant_pairs_per_dataset": r"""\textbf{What it encodes.} For each dataset, how many of the 45 model pairs the per-item paired test separates, coloured by family.
\textbf{How to read it.} A dataset with zero separates no pair: either every model scores the same or the items are too few for the differences present. High bars are the datasets carrying the leaderboard's statistical power.
\textbf{What it shows.} «n_zero» datasets separate no pair, all of them entity-matching or ceiling sets; «n_20» datasets separate 20 or more, led by FeTaQA and the two OfficeQA sets. Power lives in a dozen table and document sets.""",

    "fig_majority_baselines": r"""\textbf{What it encodes.} For the boolean datasets, every model's exact-match accuracy against the majority-class baseline of the pool (the accuracy of always answering the more common label).
\textbf{How to read it.} A model below the baseline line is doing worse than a constant answer on that dataset.
\textbf{What it shows.} Every model clears the baseline on every boolean set, usually by a wide margin; the balanced pools make the baseline about 0.5 so this is a weak test, which is why the official-ratio F1 is reported beside it.""",

    "fig_official_split": r"""\textbf{What it encodes.} Per dataset, the suite score (mean over the balanced, stratified pool) against the same answers re-weighted to the official split's stratum or class proportions; for the matching sets, positive-class F1 on the pool against F1 at the official match ratio.
\textbf{How to read it.} Points on the diagonal are datasets whose pool already matches the official split; points below it are where the balanced pool overstates performance.
\textbf{What it shows.} Accuracy moves by at most «off_shift»; F1 on the matching sets drops by up to «off_f1drop» where matches are rare, through precision: at a 2\,\% match rate a 1\,\% false-positive rate halves precision.""",

    "fig_official_scatter": r"""\textbf{What it encodes.} Every (dataset, model) pair placed by its suite score and its post-stratified official estimate under v1.
\textbf{How to read it.} Distance from the diagonal is the effect of re-weighting for that cell; the cloud's tightness is how comparable the suite numbers are to published ones.
\textbf{What it shows.} Almost every cell is within a few hundredths of the diagonal; the exceptions are the sparse matching sets and OpenSanctions, where the official class ratio differs most from 50/50.""",

    "fig_official_f1_models": r"""\textbf{What it encodes.} For each matching dataset and model, positive-class F1 on the balanced pool (grey ticks) and at the official match ratio (coloured dots).
\textbf{How to read it.} The vertical gap between tick and dot for a model is how much its balanced-pool F1 overstates its official-ratio F1; the spread of dots is the between-model difference that survives re-weighting.
\textbf{What it shows.} The gap is large and similar for all models on Amazon--Google, Machamp and Papadakis--Christen, and negligible on the dense sets. Model order is mostly preserved; the absolute numbers are not.""",

    # ------------------------------------------------------------------ diagnostics
    "fig_dataset_tau": r"""\textbf{What it encodes.} Kendall $\tau$ between the model rankings of every pair of datasets under v1 (blue agreement, red disagreement).
\textbf{How to read it.} Blocks of blue are groups of datasets that rank the models the same way; red rows are datasets that disagree with most others.
\textbf{What it shows.} Mean pairwise $\tau$ is «mean_pair_tau» and Kendall's $W$ is «W»: datasets agree about the ends of the table and disagree about the middle. Alaska Camera and HiTab are red against most of the suite.""",

    "fig_diagnostics_scatter": r"""\textbf{What it encodes.} Each dataset placed by its mean v1 score across models (horizontal) and the spread between the best and worst model (vertical); the dotted line is the ceiling flag.
\textbf{How to read it.} Datasets at the right with low spread are at ceiling and cannot rank models; datasets with high spread are the discriminating ones.
\textbf{What it shows.} «n_ceiling» datasets are flagged at ceiling (mean $\ge$ 0.95, spread $\le$ 0.04). They remain inside the objective in this run and are listed as a limitation.""",

    "fig_self_stability": r"""\textbf{What it encodes.} For each dataset, the Kendall $\tau$ between the model rankings obtained on two bootstrap halves of its items (self-stability).
\textbf{How to read it.} A value near 1 means the dataset's ranking is reproducible from its own items; a low value means its ranking is driven by a few items.
\textbf{What it shows.} Self-stability ranges from «stab_min» («stab_min_ds») to «stab_max» («stab_max_ds»). Low-stability sets are the ones whose disagreement with the consensus is partly noise.""",

    # ------------------------------------------------------------------ run facts
    "fig_run_facts": r"""\textbf{What it encodes.} Per model: total API cost for the suite, mean output tokens, median latency, and the number of answers still cut off at the final budget.
\textbf{How to read it.} Cost and output length are the price of a model's position; cut-offs are the answers scored as given because the model did not finish.
\textbf{What it shows.} One model accounts for most of the bill, output length varies by more than an order of magnitude, and the residual cut-offs are concentrated in the reasoning model that writes its chain of thought into the output budget.""",

    "fig_truncation": r"""\textbf{What it encodes.} Per model, how many answers were re-asked at each stage of the truncation protocol after being cut off without a final line at the previous budget.
\textbf{How to read it.} The trigger is mechanical (finish reason ``length'' and no final-answer line), never correctness; a tall bar is a verbose or reasoning-heavy model, not a worse one.
\textbf{What it shows.} The reasoning models dominate the re-asks; the short-answer models almost never hit the first budget.""",

    "fig_tokens_heatmap": r"""\textbf{What it encodes.} Mean output tokens per model and dataset.
\textbf{How to read it.} Columns show which tasks make every model write more (documents and SQL); rows show each model's verbosity.
\textbf{What it shows.} The two OfficeQA sets and BIRD draw the longest replies from every model, and the reasoning models write several times more than the rest on the same items. These are the cells where the output budget bites.""",
}
