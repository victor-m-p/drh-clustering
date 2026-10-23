"""
Model data: one row per answer (entry x question), group and text entries.
- family "monitoring" / "shg": the 36 child questions
  - conditional: rows with inferred = False (child questions as answered)
  - unconditional: all rows (inferred when the parent question is "No": "No", except "Yes" for 3218,
    permissible to worship other gods)
- family "parent": the parent questions (supernatural monitoring, supreme high god and supernatural beings present);
  "supreme high god present" includes "No" inferred when supernatural beings are "No" (inferred = True)
Conflicting answers are kept, weighted 1/n (weight column).
Entry-level variables: poll (group / text), year_from, year_to, duration, world region, traditions, literacy, expert.
literacy is missing when no written language question is answered (drop those entries in analyses using it).
All entries are kept; filters (e.g. long entries) are applied in the .Rmd files.
Supersedes 3_curate_models.py.
Run from inside modeling/ after preprocessing/curate_answers.py, preprocessing/curate_covariates.py and 1_code_entrytags.py.
Writes data/model_data.csv.
"""

import sys
import pandas as pd

sys.path.insert(0, "../preprocessing")
from constants import monitoring_questions

### answers: child questions and parent questions ###
children = pd.read_csv("../data/preprocessed/answers_subset_all_unconditional.csv")
children = children.dropna(subset=["answer_value"])
children["family"] = children["question_id"].isin(monitoring_questions).map({True: "monitoring", False: "shg"})
parents = pd.read_csv("../data/preprocessed/answers_parents_all.csv")
parents["family"] = "parent"
answers = pd.concat([children, parents], ignore_index=True)
answers["answer_value"] = answers["answer_value"].astype(int)
answers["poll"] = answers["poll_name"].str.contains("Group").map({True: "group", False: "text"})
answers = answers[["entry_id", "poll", "poll_name", "question_id", "question_short", "family", "answer_value", "weight", "inferred"]]

### entry-level variables ###
entry_tags = pd.read_csv("data/entry_tags.csv")
traditions = ["islamic", "buddhist", "christian", "jewish", "hindu", "chinese"]
entries = entry_tags[["entry_id", "entry_name", "year_from", "year_to", "region_id"] + traditions].copy()
entries["duration"] = entries["year_to"] - entries["year_from"]

# one tradition per entry, in this priority (as in temporal/plot_traditions_time.py)
entries["tradition"] = "other"
for tradition in reversed(traditions):  # highest priority assigned last
    entries.loc[entries[tradition].astype(bool), "tradition"] = tradition
entries[traditions] = entries[traditions].astype(int)

# all traditions per entry, for multiple membership in brms (mm(trad1, trad2, trad3)):
# up to three per entry; unused columns repeat the first tradition with weight 0, used ones get weight 1/k
memberships = entries[traditions].apply(lambda r: [t for t in traditions if r[t]] or ["other"], axis=1)
assert memberships.str.len().max() <= 3
for i in range(3):
    entries[f"trad{i + 1}"] = memberships.apply(lambda m: m[i] if i < len(m) else m[0])
    entries[f"w{i + 1}"] = memberships.apply(lambda m: 1 / len(m) if i < len(m) else 0)

# world region
region_data = pd.read_csv("../data/sccsrv3/region_data.csv")
region_data = region_data[["region_id", "world_region"]].drop_duplicates()
entries = entries.merge(region_data, on="region_id", how="left").drop(columns="region_id")

# literacy (see preprocessing/curate_covariates.py)
literacy = pd.read_csv("../data/preprocessed/entry_covariates.csv")[["entry_id", "literacy"]]
entries = entries.merge(literacy, on="entry_id", how="left")

# expert (lower-case name; see preprocessing/curate_answers.py)
experts = pd.read_csv("../data/preprocessed/entry_experts.csv")[["entry_id", "expert"]]
entries = entries.merge(experts, on="entry_id", how="left")

### combine ###
model_data = answers.merge(entries, on="entry_id", how="left")

# sanity checks: every answer has its entry-level variables, and no rows were duplicated
assert len(model_data) == len(answers)
assert model_data[["year_from", "world_region", "expert"]].notna().all().all()
model_data["literacy"] = model_data["literacy"].astype("Int64")  # missing when unanswered

model_data.to_csv("data/model_data.csv", index=False)
print(f"answers: {len(model_data)} ({model_data['inferred'].sum()} inferred), entries: {model_data['entry_id'].nunique()}")
