# References: papers actually used, and papers to compare against

APA 7 style. Links are to the open version (arXiv / ACL Anthology / publisher page). Section A lists what the method, suite or decisions rest
on; section B lists the related systems the paper should position itself against. Verify page numbers and final venues before submission.

## A. Used in the method, the suite or the decisions

### A1. Statistical comparison and selection honesty
- Demšar, J. (2006). Statistical comparisons of classifiers over multiple data sets. *Journal of Machine Learning Research, 7*, 1–30. https://jmlr.org/papers/v7/demsar06a.html — Friedman test across datasets, Nemenyi critical difference. *Used for:* the cross-dataset tests.
- García, S., & Herrera, F. (2008). An extension on "Statistical comparisons of classifiers over multiple data sets" for all pairwise comparisons. *Journal of Machine Learning Research, 9*, 2677–2694. https://jmlr.org/papers/v9/garcia08a.html — Holm-corrected pairwise post-hoc. *Used for:* Holm-Wilcoxon pairs.
- Holm, S. (1979). A simple sequentially rejective multiple test procedure. *Scandinavian Journal of Statistics, 6*(2), 65–70. https://www.jstor.org/stable/4615733
- Iman, R. L., & Davenport, J. M. (1980). Approximations of the critical region of the Friedman statistic. *Communications in Statistics – Theory and Methods, 9*(6), 571–595. https://doi.org/10.1080/03610928008827904
- Cawley, G. C., & Talbot, N. L. C. (2010). On over-fitting in model selection and subsequent selection bias in performance evaluation. *Journal of Machine Learning Research, 11*, 2079–2107. https://jmlr.org/papers/v11/cawley10a.html — *Used for:* the winner's curse argument and the nested bootstrap.
- Varma, S., & Simon, R. (2006). Bias in error estimation when using cross-validation for model selection. *BMC Bioinformatics, 7*, 91. https://doi.org/10.1186/1471-2105-7-91
- Koehn, P. (2004). Statistical significance tests for machine translation evaluation. In *Proceedings of EMNLP 2004* (pp. 388–395). https://aclanthology.org/W04-3250/ — *Used for:* paired bootstrap on per-item scores.
- Dror, R., Baumer, G., Shlomov, S., & Reichart, R. (2018). The hitchhiker's guide to testing statistical significance in natural language processing. In *Proceedings of ACL 2018* (pp. 1383–1392). https://aclanthology.org/P18-1128/
- Efron, B., & Tibshirani, R. J. (1993). *An introduction to the bootstrap*. Chapman & Hall. — item bootstrap throughout.
- Card, D., Henderson, P., Khandelwal, U., Jia, R., Mahowald, K., & Jurafsky, D. (2020). With little power comes great responsibility. In *Proceedings of EMNLP 2020* (pp. 9263–9274). https://aclanthology.org/2020.emnlp-main.745/ — *Used for:* the 100-items-per-dataset decision.
- Bouthillier, X., Delaunay, P., Bronzi, M., Trofimov, A., Nichyporuk, B., Szeto, J., … Vincent, P. (2021). Accounting for variance in machine learning benchmarks. In *Proceedings of MLSys 2021*. https://proceedings.mlsys.org/paper_files/paper/2021/hash/cfecdb276f634854f3ef915e2e980c31-Abstract.html — *Used for:* decoding and sampling variance.

### A2. Rank aggregation and leaderboards
- Bradley, R. A., & Terry, M. E. (1952). Rank analysis of incomplete block designs: I. The method of paired comparisons. *Biometrika, 39*(3/4), 324–345. https://doi.org/10.2307/2334029 — headline pooling.
- Chiang, W.-L., Zheng, L., Sheng, Y., Angelopoulos, A. N., Li, T., Li, D., … Stoica, I. (2024). Chatbot Arena: An open platform for evaluating LLMs by human preference. In *Proceedings of ICML 2024*. https://arxiv.org/abs/2403.04132 — Bradley–Terry with bootstrap CIs. *Used for:* the headline leaderboard; compared against in B.
- Colombo, P., Noiry, N., Irurozki, E., & Clémençon, S. (2022). What are the best systems? New perspectives on NLP benchmarking. In *Advances in NeurIPS 35*. https://arxiv.org/abs/2202.03799 — Kemeny / Borda consensus for benchmarks.
- Kemeny, J. G. (1959). Mathematics without numbers. *Daedalus, 88*(4), 577–591. https://www.jstor.org/stable/20026529
- Liang, P., Bommasani, R., Lee, T., Tsipras, D., Soylu, D., Yasunaga, M., … Koreeda, Y. (2022). Holistic evaluation of language models. *arXiv:2211.09110*. https://arxiv.org/abs/2211.09110 — mean win rate, per-scenario native metrics.
- Boubdir, M., Kim, E., Ermis, B., Hooker, S., & Fadaee, M. (2023). Elo uncovered: Robustness and best practices in language model evaluation. *arXiv:2311.17295*. https://arxiv.org/abs/2311.17295 — transitivity and reliability of pairwise ratings.
- Perlitz, Y., Bandel, E., Gera, A., Arviv, O., Ein-Dor, L., Shnarch, E., … Choshen, L. (2024). Efficient benchmarking of language models. In *Proceedings of NAACL 2024*. https://arxiv.org/abs/2308.11696 — reliability (DIoR) and benchmark agreement. *Used for:* Kendall's W framing.
- Perlitz, Y., Gera, A., Arviv, O., Shnarch, E., Shmueli, Y., & Choshen, L. (2024). Do these LLM benchmarks agree? Fixing benchmark evaluation with BenchBench. *arXiv:2407.13696*. https://arxiv.org/abs/2407.13696
- Polo, F. M., Weber, L., Choshen, L., Sun, Y., Xu, G., & Yurochkin, M. (2024). tinyBenchmarks: Evaluating LLMs with fewer examples. In *Proceedings of ICML 2024*. https://arxiv.org/abs/2402.14992 — IRT / Rasch ability; 100 items suffice. *Used for:* v3's IRT view and the item-count decision.
- Rasch, G. (1960). *Probabilistic models for some intelligence and attainment tests*. Danish Institute for Educational Research. — Rasch model.
- Kendall, M. G. (1938). A new measure of rank correlation. *Biometrika, 30*(1/2), 81–93. https://doi.org/10.2307/2332226; and Kendall, M. G., & Babington Smith, B. (1939). The problem of m rankings. *Annals of Mathematical Statistics, 10*(3), 275–287. — τ-b and Kendall's W.

### A3. Metric validation (the anchors)
- Mathur, N., Baldwin, T., & Cohn, T. (2020). Tangled up in BLEU: Reevaluating the evaluation of automatic machine translation evaluation metrics. In *Proceedings of ACL 2020* (pp. 4984–4997). https://aclanthology.org/2020.acl-main.448/ — metrics validated against external quality; outlier systems. *Used for:* separating agreement from correctness; dataset outliers.
- Kocmi, T., Federmann, C., Grundkiewicz, R., Junczys-Dowmunt, M., Matsushita, H., & Menezes, A. (2021). To ship or not to ship: An extensive evaluation of automatic metrics for machine translation. In *Proceedings of WMT 2021* (pp. 478–494). https://aclanthology.org/2021.wmt-1.57/
- Zheng, L., Chiang, W.-L., Sheng, Y., Zhuang, S., Wu, Z., Zhuang, Y., … Stoica, I. (2023). Judging LLM-as-a-judge with MT-Bench and Chatbot Arena. In *Advances in NeurIPS 36*. https://arxiv.org/abs/2306.05685 — judges need validation. *Used for:* framing.
- Fabbri, A. R., Kryściński, W., McCann, B., Xiong, C., Socher, R., & Radev, D. (2021). SummEval: Re-evaluating summarization evaluation. *Transactions of the ACL, 9*, 391–409. https://aclanthology.org/2021.tacl-1.24/ — human-label meta-evaluation design. *Used for:* the human-labelling protocol.

### A4. Search design and decoding
- McKay, M. D., Beckman, R. J., & Conover, W. J. (1979). A comparison of three methods for selecting values of input variables in the analysis of output from a computer code. *Technometrics, 21*(2), 239–245. https://doi.org/10.2307/1268522 — Latin hypercube sampling.
- Bergstra, J., & Bengio, Y. (2012). Random search for hyper-parameter optimization. *Journal of Machine Learning Research, 13*, 281–305. https://jmlr.org/papers/v13/bergstra12a.html
- Hickernell, F. J. (1998). A generalized discrepancy and quadrature error bound. *Mathematics of Computation, 67*(221), 299–322. https://doi.org/10.1090/S0025-5718-98-00894-1 — centred L2 discrepancy used for design coverage.
- Renze, M., & Guven, E. (2024). The effect of sampling temperature on problem solving in large language models. In *Findings of EMNLP 2024*. https://arxiv.org/abs/2402.05201 — temperature and accuracy.

### A5. Post-stratification
- Horvitz, D. G., & Thompson, D. J. (1952). A generalization of sampling without replacement from a finite universe. *Journal of the American Statistical Association, 47*(260), 663–685. https://doi.org/10.1080/01621459.1952.10483446 — weighted estimation to the official split.
- Papadakis, G., Kirielle, N., Christophides, V., & Christen, P. (2024). A critical re-evaluation of benchmark datasets for (deep) learning-based matching algorithms. In *Proceedings of ICDE 2024*. https://arxiv.org/abs/2307.01231 — class imbalance in matching benchmarks. *Used for:* why balanced pools inflate F1; the Dn1–Dn8 sets.

### A6. Datasets in the suite (cite each once in the data table)
- Mudgal, S., Li, H., Rekatsinas, T., Doan, A., Park, Y., Krishnan, G., Deep, R., Arcaute, E., & Raghavendra, V. (2018). Deep learning for entity matching: A design space exploration. In *Proceedings of SIGMOD 2018* (pp. 19–34). https://doi.org/10.1145/3183713.3196926 — Abt-Buy, Amazon-Google, Walmart-Amazon, DBLP-Scholar, DBLP-ACM.
- Li, Y., Li, J., Suhara, Y., Doan, A., & Tan, W.-C. (2020). Deep entity matching with pre-trained language models. *Proceedings of the VLDB Endowment, 14*(1), 50–60. https://arxiv.org/abs/2004.00584 — Ditto; WDC-LSPC usage.
- Peeters, R., Der, A., & Bizer, C. (2024). WDC Products: A multi-dimensional entity matching benchmark. In *Proceedings of EDBT 2024*. https://arxiv.org/abs/2301.09521
- Wang, J., Li, Y., & Hirota, W. (2021). Machamp: A generalized entity matching benchmark. In *Proceedings of CIKM 2021*. https://doi.org/10.1145/3459637.3482008
- Crescenzi, V., De Angelis, A., Firmani, D., Mazzei, M., Merialdo, P., Piai, F., & Srivastava, D. (2021). Alaska: A flexible benchmark for data integration tasks. *arXiv:2101.11259*. https://arxiv.org/abs/2101.11259
- Koutras, C., Siachamis, G., Ionescu, A., Psarakis, K., Brons, J., Fragkoulis, M., … Katsifodimos, A. (2021). Valentine: Evaluating matching techniques for dataset discovery. In *Proceedings of ICDE 2021*. https://arxiv.org/abs/2010.07386
- Liu, Y., Magalhães, E., Lopez, G., Paiva, B., & Freire, J. (2025). Magneto: Combining small and large language models for schema matching. *Proceedings of the VLDB Endowment, 18*. https://arxiv.org/abs/2412.08194
- Zhang, J., Shin, B., Choi, J. D., & Ho, J. C. (2021). SMAT: An attention-based deep learning solution to the automation of schema matching. In *Advances in Databases and Information Systems (ADBIS 2021)*. https://doi.org/10.1007/978-3-030-82472-3_19
- Wang, Y., Ren, Y., Qian, L., Peng, X., Xie, Q., Han, W., … (2025). FinTagging: An LLM-ready benchmark for extracting and structuring financial information. *arXiv:2505.20650*. https://arxiv.org/abs/2505.20650 [verify author list]
- Transaction Processing Performance Council. (2014). *TPC Benchmark DI, Specification v1.1.0*. https://www.tpc.org/tpcdi/
- Cheng, Z., Dong, H., Wang, Z., Jia, R., Guo, J., Gao, Y., Han, S., Lou, J.-G., & Zhang, D. (2022). HiTab: A hierarchical table dataset for question answering and natural language generation. In *Proceedings of ACL 2022* (pp. 1094–1110). https://aclanthology.org/2022.acl-long.78/
- Pasupat, P., & Liang, P. (2015). Compositional semantic parsing on semi-structured tables. In *Proceedings of ACL-IJCNLP 2015* (pp. 1470–1480). https://aclanthology.org/P15-1142/ — WikiTableQuestions.
- Chen, W., Wang, H., Chen, J., Zhang, Y., Wang, H., Li, S., Zhou, X., & Wang, W. Y. (2020). TabFact: A large-scale dataset for table-based fact verification. In *Proceedings of ICLR 2020*. https://arxiv.org/abs/1909.02164
- Nan, L., Hsieh, C., Mao, Z., Lin, X. V., Verma, N., Zhang, R., … Radev, D. (2022). FeTaQA: Free-form table question answering. *Transactions of the ACL, 10*, 35–49. https://aclanthology.org/2022.tacl-1.3/
- Zhu, F., Lei, W., Huang, Y., Wang, C., Zhang, S., Lv, J., Feng, F., & Chua, T.-S. (2021). TAT-QA: A question answering benchmark on a hybrid of tabular and textual content in finance. In *Proceedings of ACL-IJCNLP 2021* (pp. 3277–3287). https://aclanthology.org/2021.acl-long.254/
- Li, J., Hui, B., Qu, G., Yang, J., Li, B., Li, B., … Li, Y. (2023). Can LLM already serve as a database interface? A big bench for large-scale database grounded text-to-SQLs. In *Advances in NeurIPS 36 (Datasets and Benchmarks)*. https://arxiv.org/abs/2305.03111 — BIRD.
- Wu, X., Yang, J., Chai, L., Zhang, G., Liu, J., Du, X., … Zhang, Z. (2025). TableBench: A comprehensive and complex benchmark for table question answering. In *Proceedings of AAAI 2025*. https://arxiv.org/abs/2408.09174
- Sui, Y., Zhou, M., Zhou, M., Han, S., & Zhang, D. (2024). Table meets LLM: Can large language models understand structured table data? A benchmark and empirical study. In *Proceedings of WSDM 2024*. https://arxiv.org/abs/2305.13062 — SUC.
- MMTU, RealHiTBench, TabIS, TableEval, OfficeQA Pro V2, OpenSanctions pairs: cite the dataset cards / papers listed in `datasets_survey/09_SOURCES.md` (arXiv ids there); verify venues at submission time.

## B. Systems and papers to compare against in the paper

| Compare on | Paper | Why it is the right comparison |
|---|---|---|
| Leaderboard construction with uncertainty | Chiang et al. (2024), Chatbot Arena, https://arxiv.org/abs/2403.04132 | same Bradley–Terry + bootstrap machinery, but human votes and no gold; our judge is a formula that we audit |
| Qualitative model differences | Dunlap, L., Mandal, K., Darrell, T., Steinhardt, J., & Gonzalez, J. E. (2024). VibeCheck: Discover and quantify qualitative differences in large language models. *arXiv:2410.12851*. https://arxiv.org/abs/2410.12851 | explains preferences; does not measure correctness; shows what our lexical judge cannot see |
| Judge validation | Zheng et al. (2023), MT-Bench, https://arxiv.org/abs/2306.05685; Tan, S., Zhuang, S., Montgomery, K., Tang, W. Y., Cuadron, A., Wang, C., Popa, R. A., & Stoica, I. (2024). JudgeBench: A benchmark for evaluating LLM-based judges. *arXiv:2410.12784*. https://arxiv.org/abs/2410.12784 | they validate LLM judges against humans; we validate a formula judge against known-quality answers |
| Benchmark reliability / agreement | Perlitz et al. (2024) BenchBench, https://arxiv.org/abs/2407.13696; Boubdir et al. (2023), https://arxiv.org/abs/2311.17295 | our Kendall's W (≈ 0.27) and rule-dependent top order are the same phenomenon measured on a gold-based suite |
| Few-item evaluation | Polo et al. (2024) tinyBenchmarks, https://arxiv.org/abs/2402.14992 | justifies 100 items per dataset; our item-level bootstraps show the attainable precision |
| Leaderboard integrity | Singh, S., Nan, Y., Wang, A., D'Souza, D., Kapoor, S., Üstün, A., … Hooker, S. (2025). The leaderboard illusion. *arXiv:2504.20879*. https://arxiv.org/abs/2504.20879 | selection effects on leaderboards; our nested selection addresses the analogous effect in weight search |
| Holistic multi-metric evaluation | Liang et al. (2022) HELM, https://arxiv.org/abs/2211.09110 | HELM reports per-scenario native metrics without a composite; we show the composite's weights do not matter here |
| LLM entity matching | Peeters, R., & Bizer, C. (2025). Entity matching using large language models. In *Proceedings of EDBT 2025*. https://arxiv.org/abs/2310.11244; Narayan, A., Chami, I., Orr, L., & Ré, C. (2022). Can foundation models wrangle your data? *Proceedings of the VLDB Endowment, 16*(4). https://arxiv.org/abs/2205.09911 | published F1 on the same Magellan / WDC sets; our official-split F1 estimates are the comparable numbers |
| Table understanding leaderboards | Wu et al. (2025) TableBench; MMTU (Zhang et al., 2025, https://arxiv.org/abs/2506.05587) | they rank models per task with exact match; we show how the pooling rule changes the top order |
| Metric meta-evaluation | Mathur et al. (2020); Kocmi et al. (2021) | the template for "validate the metric against something external to the systems ranked" |

Keep the comparison paragraph short: one sentence per row on what the other paper measures, one on what ours adds (an audited gold-based
judge, honest selection, official-split comparability, reproducibility from cache), and one on what theirs has that ours lacks (scale,
human signal, open-ended coverage).
