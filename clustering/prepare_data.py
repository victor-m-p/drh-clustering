"""
EM input with the parent questions (subset "group_parents" in run_clustering.py).
- Group entries; the 36 child questions as answered (not inferred), plus the two parent questions:
  supernatural monitoring present (2890) and supreme high god present (2919; incl. "No" inferred when
  supernatural beings are "No"). Children stay missing when their parent is "No", so a "No" entry
  contributes through the parent only.
- Sample: group entries that answered both parent questions (replaces the 50% rule of curate_answers.py,
  which in practice kept only entries with both parents "Yes").
- Conflicting answers: one row per combination of answers, weight = product of 1 / number of answers (as before).
- Collapsed version (subset "group_parents_collapsed"): murder out-group (murder other religions, other polities)
  and elite ties (monarch fused, monarch manifestation, kin to elites, other elite loyalty) as one question each,
  as in modeling/13_main.Rmd: "Yes" if any answered question in the set is "Yes", "No" if at least one is answered
  and none is "Yes", missing otherwise. Applied to each expanded row (each combination of conflicting answers).
  The collapsed questions get the ids in `collapsed_ids` (names added in run_clustering.py).
Run from inside clustering/ after preprocessing/curate_answers.py.
Writes ../data/preprocessed/groups_expanded_parents.csv and groups_expanded_parents_collapsed.csv.
"""

import sys
import pandas as pd

sys.path.insert(0, "../preprocessing")
from helper_functions import expand_data, assign_weight

columns = ["entry_id", "question_id", "answer_value"]
children = pd.read_csv("../data/preprocessed/answers_subset_groups.csv")
parents = pd.read_csv("../data/preprocessed/answers_parents_groups.csv")
parents = parents[parents["question_id"].isin([2890, 2919])]

# sample: both parent questions answered
n_parents = parents.groupby("entry_id")["question_id"].nunique()
entries = n_parents[n_parents == 2].index

# child answers for every entry in the sample (missing as NaN, also for entries without any child answer)
child_questions = children["question_id"].unique()
grid = pd.MultiIndex.from_product([entries, child_questions], names=["entry_id", "question_id"]).to_frame(index=False)
children = grid.merge(children[columns], on=["entry_id", "question_id"], how="left")

# long data, weights 1 / number of answers per entry and question (1 for missing)
long = pd.concat([children, parents.loc[parents["entry_id"].isin(entries), columns]], ignore_index=True)
long = assign_weight(long, "entry_id", "question_id")
assert round(long["weight"].sum()) == len(entries) * (len(child_questions) + 2)

expanded = expand_data(long, "question_id", "entry_id")
assert expanded["entry_id"].nunique() == len(entries)
assert abs(expanded.groupby("entry_id")["weight"].sum() - 1).max() < 1e-9

expanded.to_csv("../data/preprocessed/groups_expanded_parents.csv", index=False)

# collapsed version: each set replaced by one column
collapsed_sets = {
    "murder out-group": ["murder other religions", "murder other polities"],
    "elite ties": ["is monarch fused", "is monarch manifestation", "is kin to elites", "other elite loyalty"],
}
collapsed_ids = {"murder out-group": 9001, "elite ties": 9002}
id_of = pd.read_csv("../data/preprocessed/answers_subset_groups.csv").drop_duplicates("question_id")
id_of = dict(zip(id_of["question_short"], id_of["question_id"]))
collapsed = expanded.copy()
for name, members in collapsed_sets.items():
    cols = [f"Q{id_of[m]}" for m in members]
    values = collapsed[cols]
    collapsed[f"Q{collapsed_ids[name]}"] = (values == 1).any(axis=1).astype(float).where(values.notna().any(axis=1))
    collapsed = collapsed.drop(columns=cols)
assert collapsed.shape[1] == expanded.shape[1] - 4
collapsed.to_csv("../data/preprocessed/groups_expanded_parents_collapsed.csv", index=False)

# summary
parent_answers = parents[parents["entry_id"].isin(entries)].groupby(["entry_id", "question_id"])["answer_value"].mean().unstack()
print(f"entries: {len(entries)}, rows: {len(expanded)}")
print("parent answers (0 = No, 1 = Yes, in between = conflicting):")
print(parent_answers.round(2).value_counts().rename_axis(["monitoring (2890)", "shg (2919)"]))
answered = expanded.drop(columns=["entry_id", "weight"]).notna().sum(axis=1)
print(f"answered questions per row: median {answered.median():.0f}, min {answered.min()}, max {answered.max()}")
