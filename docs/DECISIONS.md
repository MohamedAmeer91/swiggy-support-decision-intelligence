# Decisions

1. Line endings: `data/records.csv` and `generate_data.py` are marked `-text` in .gitattributes (the earlier eol=lf rule would have rewritten the CRLF csv and broken the MD5). The MD5 was verified with `git cat-file` and in a clean clone.
2. docs/ and tests/ stay tracked: the brief lists required files and says shared helpers are fine; it does not forbid extra text files.
3. Helper `common.py` holds Part 2 machinery; Part 4 recomputes the Part 2 model and best K deterministically through `part2_pipeline()` instead of importing Part 2 outputs.
4. Part 4 voting uses tau 0.3 for logistic and stump as the brief says; the recommended production threshold in the memo is the cost-chosen 0.15 (Task 2.8). The memo states other models' cost at 0.15 was not computed.
5. `elbow_k` fallback (no K in 3..5 satisfies the rule) is 5; not triggered (elbow_k = 3).
6. AdaBoost ensemble: a zero score would count as wrong; not triggered.
7. Ties in best split and best K go to the first (S1 first, smaller K).
8. All checkpoints matched; K-means pass counts 21/15/27 matched the brief.
9. Package pins: numpy==1.26.4 only.
