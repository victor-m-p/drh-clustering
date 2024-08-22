import numpy as np
import pandas as pd

# find has writing
answerset = pd.read_csv("../data/raw/answerset.csv")

# take written language super-questions
written_language = answerset[
    (answerset["question_name"].str.contains("written language"))
    & (answerset["parent_question_id"].isna())
]

# written language questions and answers
written_language = written_language[
    ["entry_id", "question_name", "answer_value"]
].drop_duplicates()

# now use the literacy recoding table
literacy_recode = pd.read_csv("../data/raw/literacy_recode.csv")
literacy_recode = literacy_recode[["entry_id", "question_name", "answer_value"]]

# take answer from literacy recode where it exists
# Merge the two dataframes on 'entry_id' and 'question_name' using an outer join
df_merged = pd.merge(
    written_language,
    literacy_recode,
    on=["entry_id", "question_name"],
    how="outer",
    suffixes=("", "_small"),
)

# sanity check
assert len(literacy_recode) == len(df_merged[df_merged["answer_value_small"].notna()])

# Use the 'answer_value' from literacy recode where it exists
df_merged["answer_value"] = df_merged["answer_value_small"].combine_first(
    df_merged["answer_value"]
)

# Drop the auxiliary 'answer_value_small' column
df_result = df_merged.drop(columns=["answer_value_small"])

# Now we can compute whether each entry has a "YES" for at least one of the questions
written_language_yes = df_result[df_result["answer_value"] == 1]
written_language_entries = written_language_yes["entry_id"].unique().tolist()

# Also add all relevant Text entries to the list (they all have literacy)
religious_text = answerset[answerset["poll_name"].str.contains("Text")]
religious_text_entries = religious_text["entry_id"].unique().tolist()

# Combine the two lists (sets)
written_language_entries = list(set(written_language_entries + religious_text_entries))

# Write table
all_entries = answerset["entry_id"].unique().tolist()
df_entries = pd.DataFrame(all_entries, columns=["entry_id"])
df_entries["literacy"] = df_entries.isin(written_language_entries).astype(int)
df_entries.to_csv("literacy.csv", index=False)