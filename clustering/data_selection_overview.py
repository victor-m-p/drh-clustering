import pandas as pd
import numpy as np

# monitoring:
answers = pd.read_csv("../data/preprocessed/answers.csv")
answers["entry_id"].nunique()  # 1288

# first selection (group)
answers_poll = answers[
    answers["poll"].isin(
        ["Religious Group (v6)", "Religious Group (v5)", "Religious Text (v1.0)"]
    )
]
answers_poll["entry_id"].nunique()  # 1015

# second selection (has to have "YES" to super-question)
# and has to have at leats 1 non-NAN answer to sub-question
shg_data = pd.read_csv("../data/preprocessed/shg_answers.csv")
monitoring = pd.read_csv("../data/ML/monitoring.csv")
shg = pd.read_csv("../data/ML/shg.csv")

shg["entry_id"].nunique()
monitoring["entry_id"].nunique()
# 525 (for monitoring)
# 556 (SHG)

shg_sub = shg_data[
    shg_data["poll"].isin(
        ["Religious Group (v6)", "Religious Group (v5)", "Religious Text (v1.0)"]
    )
]
shg_shg = shg_sub[shg_sub["question_name"] == "A supreme high god is present:"]
shg_shg[shg_shg["answer"] == "No"]
