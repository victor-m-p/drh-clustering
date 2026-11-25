"""
vmp 2026-10-23

Covariates for exploring how beliefs relate to society (more experimental than curate_answers.py).
Only entries in the sample of curate_answers.py (run that first): entries with a yes/no answer
(answered or inferred) to a supreme high god or monitoring question, or to one of their parent questions.

Writes:
- entry_covariates.csv: one row per entry
  - social_complexity: society type (band, tribe, chiefdom, state, empire), with the editorial recode
  - literacy: written language (with the literacy recode); all text entries are literate; missing when unanswered
  - adherents, adherents_pct: number of adherents (texts: audience) in the sample region
- answers_covariates.csv: one row per yes/no answer, weighted 1/n (constants.covariate_coding)
  - religion and politics: official political support (2300); head of polity is head of religion (2339)
    and political officials are religious officials (2319), with "No" inferred when 2300 is "No"
  - supernatural punishment (3420) and reward (3437) present; for each, when (this life, afterlife) and
    who / why (e.g. only by the high god, impersonal, to enforce group norms), with "No" inferred when
    3420 (3437) is "No"
  - own written language

Run from inside preprocessing/.
"""

import numpy as np
import pandas as pd
from helper_functions import assign_weight
from constants import (
    polls,
    covariate_coding,
    covariate_infer_no,
    social_complexity_levels,
    social_complexity_labels,
    social_complexity_mistranslated,
)

answerset = pd.read_csv("../data/sccsrv3/answerset.csv", low_memory=False)
question_relation = pd.read_csv("../data/sccsrv3/questionrelation.csv")
answers = answerset[answerset["poll_name"].isin(polls)]
answers = answers[["poll_name", "entry_id", "question_id", "question_name", "answer", "answer_value"]].drop_duplicates()
answers = answers.merge(question_relation, on=["question_id", "poll_name"], how="inner")

# entries in the sample (1187 of the 1240 entries in the polls; each entry is in one poll)
sample = pd.concat([
    pd.read_csv("../data/preprocessed/answers_subset_all_unconditional.csv", usecols=["entry_id", "poll_name"]),
    pd.read_csv("../data/preprocessed/answers_parents_all.csv", usecols=["entry_id", "poll_name"]),
]).drop_duplicates()
answers = answers[answers["entry_id"].isin(sample["entry_id"])]
entries = answers[["entry_id", "poll_name"]].drop_duplicates()
assert not entries["entry_id"].duplicated().any()
assert len(entries) == len(sample)

"""
Social complexity (related id 3492).

The editorial recode (social_complexity_recode.csv, one answer per entry) replaces the raw answers.
Most recoded entries answer "Other" in the raw data (not in the DRH answerset as of SCCSR.v3).
Answers in other languages are coded from the answer text: groups have the level in answer_value,
but nearly all text answers have answer_value = -1 (report to DRH editors).
Levels: band (1) < tribe (2) < chiefdom (3) < state (4) < empire (5); social_complexity_large: state or empire.
Entries with conflicting levels get the highest level.

social_complexity_status (sample of 1187: v5 / v6 / text):
- coded: one level in the raw answers (126 / 478 / 173)
- recoded: in the recode table (63 / 113 / 88); it overrides two coded raw answers (1595: state -> chiefdom, 1767: state -> empire)
- conflict: several levels, highest level taken (3 / 12 / 3); 12 are state and empire
- not codable: "Other" (most with notes: the group is a denomination, network, etc., not a society),
  "Un groupe" (mistranslated, see constants), don't know (4 / 55 / 48)
- unanswered: no answer to 3492 (8 / 12 / 1)
"""

society = answers[answers["related_question_id"] == 3492][["entry_id", "answer", "answer_value"]]
answered = set(society["entry_id"])

# the codes in answer_value (groups) agree with the answer text
coded = society[society["answer_value"] > 0]
coded = coded[~coded["answer"].isin(social_complexity_mistranslated)]
assert (coded["answer"].map(social_complexity_levels) == coded["answer_value"]).all()

recode = pd.read_csv("../data/sccsrv3/social_complexity_recode.csv")
assert not recode["entry_id"].duplicated().any()
society = pd.concat([
    society[~society["entry_id"].isin(recode["entry_id"])].assign(recoded=False),
    recode[recode["entry_id"].isin(entries["entry_id"])][["entry_id", "answer"]].assign(recoded=True),
], ignore_index=True)
society["level"] = society["answer"].map(social_complexity_levels)
society = society.dropna(subset=["level"])

social_complexity = society.groupby("entry_id").agg(
    min_level=("level", "min"), max_level=("level", "max"), social_complexity_recoded=("recoded", "first")
).reset_index()
conflict = social_complexity["min_level"] != social_complexity["max_level"]
social_complexity["social_complexity_level"] = social_complexity["max_level"]
social_complexity["social_complexity"] = social_complexity["social_complexity_level"].map(social_complexity_labels)
social_complexity["social_complexity_large"] = (social_complexity["social_complexity_level"] >= 4).astype(int)
social_complexity["social_complexity_status"] = np.select(
    [social_complexity["social_complexity_recoded"], conflict], ["recoded", "conflict"], "coded"
)
social_complexity = social_complexity.drop(columns=["min_level", "max_level", "social_complexity_recoded"])
social_complexity = entries.merge(social_complexity, on="entry_id", how="left")
social_complexity["social_complexity_status"] = social_complexity["social_complexity_status"].fillna(
    social_complexity["entry_id"].isin(answered).map({True: "not codable", False: "unanswered"})
)
print(pd.crosstab(social_complexity["poll_name"], social_complexity["social_complexity_status"], margins=True))
social_complexity = social_complexity.drop(columns="poll_name")


"""
Literacy (moved from modeling/2_code_literacy.py; changed 2026-10-23: unanswered is missing, not 0).

1 if any of the written language questions (top-level, group polls) is "Yes", with the literacy recode;
all text entries are literate; 0 if at least one is answered "No" (and none "Yes"); else missing.
"""

written_language = answerset[
    answerset["question_name"].str.contains("written language") & answerset["parent_question_id"].isna()
][["entry_id", "question_name", "answer_value"]].drop_duplicates()

literacy_recode = pd.read_csv("../data/sccsrv3/literacy_recode.csv")[["entry_id", "question_name", "answer_value"]]
written_language = written_language.merge(
    literacy_recode, on=["entry_id", "question_name"], how="outer", suffixes=("", "_recode")
)
assert len(literacy_recode) == written_language["answer_value_recode"].notna().sum()
written_language["answer_value"] = written_language["answer_value_recode"].combine_first(written_language["answer_value"])

literate = set(written_language.loc[written_language["answer_value"] == 1, "entry_id"])
literate |= set(answerset.loc[answerset["poll_name"].str.contains("Text"), "entry_id"])
not_literate = set(written_language.loc[written_language["answer_value"] == 0, "entry_id"]) - literate
literacy = entries[["entry_id"]].assign(
    literacy=np.select([entries["entry_id"].isin(literate), entries["entry_id"].isin(not_literate)], [1, 0], np.nan)
)
print("literacy:", literacy["literacy"].value_counts(dropna=False).to_dict())

"""
Number of adherents (related ids 2281: estimated population, 2301: % of sample region population).

The number is only in the answer text ("Estimated population, numeric: 1000000", "Number: 300"),
answer_value is just 1 / -1. Percentages above 100 are dropped (likely population numbers).
Median when an entry gives several values.
"""

def parse_number(related_question_id, name):
    x = answers[answers["related_question_id"] == related_question_id]
    x = x.assign(value=pd.to_numeric(x["answer"].str.extract(r":\s*(\d+(?:\.\d+)?)\s*$")[0]))
    x = x.dropna(subset=["value"])
    return x.groupby("entry_id")["value"].median().rename(name).reset_index()

adherents = parse_number(2281, "adherents")
adherents_pct = parse_number(2301, "adherents_pct")
print(f"adherents_pct above 100 dropped: {(adherents_pct['adherents_pct'] > 100).sum()}")
adherents_pct = adherents_pct[adherents_pct["adherents_pct"] <= 100]

entry_covariates = (
    entries.merge(social_complexity, on="entry_id", how="left")
    .merge(literacy, on="entry_id", how="left")
    .merge(adherents, on="entry_id", how="left")
    .merge(adherents_pct, on="entry_id", how="left")
)
assert len(entry_covariates) == len(entries)
entry_covariates.to_csv("../data/preprocessed/entry_covariates.csv", index=False)

"""
Yes/no covariate questions (constants.covariate_coding).
question_name is kept per poll, since group and text wording differ for several questions.
- Inferred (constants.covariate_infer_no; inferred = True): "No" when the parent is "No" (not when the parent
  is answered both "Yes" and "No", or not at all).
  - 2339 and 2319 are only asked when 2300 is "Yes".
  - Punishment: this life / afterlife are only asked when 3420 is "Yes"; who / why only when, in addition,
    the cause or agent (3480) / the reason (3485) is known. "No" is inferred from 3420 only: a "No" to the
    gateway ("reason not known") leaves who / why missing. Reward (3437) is the same, with one gateway (3469).
  - Open: the top questions ask whether supernatural beings punish (reward), so groups with only impersonal
    (karma-type) punishment may answer "No" there; inferring "No" for "punishment impersonal" is then wrong.
All other answers as answered (inferred = False).
Conflicting answers (an entry answers a question both "Yes" and "No") have weight < 1.
"""

covariate_names = pd.DataFrame(list(covariate_coding.items()), columns=["related_question_id", "question_short"])
covariate_names["related_question_id"] = covariate_names["related_question_id"].astype(int)
answers_covariates = answers.merge(covariate_names, on="related_question_id", how="inner")
answers_covariates = answers_covariates[answers_covariates["answer_value"].isin([0, 1])]
answers_covariates = (
    answers_covariates.drop(columns=["question_id", "answer"])
    .rename(columns={"related_question_id": "question_id"})
    [["entry_id", "poll_name", "question_id", "question_short", "question_name", "answer_value"]]
    .drop_duplicates(["entry_id", "question_id", "answer_value"])
)
answers_covariates = assign_weight(answers_covariates, "entry_id", "question_id").assign(inferred=False)

# infer "No" for the children of 2300 when 2300 is "No"
inferred = []
for child, parent in covariate_infer_no.items():
    parent_answer = answers_covariates[answers_covariates["question_id"] == int(parent)].groupby(
        ["entry_id", "poll_name"])["answer_value"].mean().reset_index()
    parent_no = parent_answer[parent_answer["answer_value"] == 0]
    child_answered = answers_covariates.loc[answers_covariates["question_id"] == int(child), "entry_id"]
    assert not parent_no["entry_id"].isin(child_answered).any()
    inferred.append(parent_no[["entry_id", "poll_name"]].assign(
        question_id=int(child), question_short=covariate_coding[child], answer_value=0.0, weight=1.0, inferred=True
    ))
answers_covariates = pd.concat([answers_covariates] + inferred, ignore_index=True)
assert np.isclose(answers_covariates["weight"].sum(), len(answers_covariates[["entry_id", "question_id"]].drop_duplicates()))
answers_covariates.to_csv("../data/preprocessed/answers_covariates.csv", index=False)

print(answers_covariates.assign(poll=answers_covariates["poll_name"].str.contains("Group").map({True: "group", False: "text"}))
      .groupby(["question_short", "poll", "inferred"])["entry_id"].nunique().unstack(["poll", "inferred"], fill_value=0))
