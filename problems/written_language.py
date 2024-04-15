import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.ticker as ticker

# setup
superquestion = "shg"
x_min = -2000
bin_width = 500
step_size = 100

# find has writing
raw_data = pd.read_csv("../data/raw/raw_data.csv")

# take written language super-questions
written_language = raw_data[
    (raw_data["question_name"].str.contains("written language"))
    & (raw_data["parent_question_id"].isna())
]

# n = 682 unique entries here.
written_language["entry_id"].nunique()

# find all entries that have "YES" for at least one of these questions
# n = 469 unique entries here.
written_language_yes = written_language[written_language["value"] == 1]
written_language_yes_entries = written_language_yes["entry_id"].unique().tolist()

# find the ones that have only "NO":
written_language_no = written_language[
    ~written_language["entry_id"].isin(written_language_yes_entries)
]
written_language_no = written_language_no[
    ["entry_id", "entry_name", "year_from", "year_to"]
].drop_duplicates()
written_language_no = written_language_no.sort_values("year_from")
written_language_no.to_csv("written_language_no.csv", index=False)
