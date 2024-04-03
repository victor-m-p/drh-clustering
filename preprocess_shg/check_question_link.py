import pandas as pd
import numpy as np

# load cleaned shg answers
shg_answers = pd.read_csv("../data/preprocessed/shg_answers.csv")
answers_related = pd.read_csv("../data/preprocessed/answers_related.csv")

# looks like we still do not quite have what we need
shg_sub = shg_answers[
    ["entry_id", "question_id", "parent_question_id", "related_question_id", "poll"]
].drop_duplicates()
shg_groups = shg_sub.groupby(["entry_id", "poll"]).size().reset_index(name="count")

### check polls ###
shg_polls = shg_sub["poll"].unique().tolist()

### check the amount in each category ###
len(shg_groups[shg_groups["poll"] == shg_polls[0]])  # 226
len(shg_groups[shg_groups["poll"] == shg_polls[1]])  # 544
len(shg_groups[shg_groups["poll"] == shg_polls[2]])  # 2
len(shg_groups[shg_groups["poll"] == shg_polls[3]])  # 8
len(shg_groups[shg_groups["poll"] == shg_polls[4]])  # 262
len(shg_groups[shg_groups["poll"] == shg_polls[5]])  # 1
len(shg_groups[shg_groups["poll"] == shg_polls[6]])  # 245

# focus on the major polls
## Religious Group (v5)
## Religious Group (v6)
## Religious Place (v1.2)
## Religious Text (v1.0)
shg_groups[shg_groups["poll"] == shg_polls[0]]["count"].unique()  # all 39
shg_groups[shg_groups["poll"] == shg_polls[1]]["count"].unique()  # all 39
shg_groups[shg_groups["poll"] == shg_polls[4]]["count"].unique()  # 16
shg_groups[shg_groups["poll"] == shg_polls[6]]["count"].unique()  # all 39

# what are the missing questions/answers for place?
"""
supernatural monitoring (many or all) lacking for place (v1.2)
check whether this is true. 
"""
all_related_questions = shg_answers["related_question_id"].unique()
shg_place = shg_answers[shg_answers["poll"] == "Religious Place (v1.2)"]
shg_related_questions = shg_place["related_question_id"].unique()
missing_questions = set(all_related_questions) - set(shg_related_questions)
missing_questions = shg_answers[
    shg_answers["related_question_id"].isin(missing_questions)
]
missing_questions = missing_questions[
    ["related_question_id", "question_name", "parent_question"]
].drop_duplicates()
missing_questions_monitoring = missing_questions[
    missing_questions["parent_question"] == "Is supernatural monitoring present:"
]
missing_questions_monitoring  # looks like we are just missing a lot of the answers here.
missing_questions_shg = missing_questions[
    missing_questions["parent_question"] == "A supreme high god is present:"
]
missing_questions_shg  # looks like we actually are just missing a lot of answers here.

# what are we missing for text?
"""
knowledge of this world is missing from text.
check whether this is true. 
"""
shg_text = shg_answers[shg_answers["poll"] == "Religious Text (v1.0)"]
shg_text[shg_text["question_id"] == 8002]
shg_text_related_questions = shg_text["related_question_id"].unique()
missing_questions = set(all_related_questions) - set(shg_text_related_questions)
missing_questions = shg_answers[
    shg_answers["related_question_id"].isin(missing_questions)
]
missing_questions = missing_questions[
    ["question_id", "question_name", "parent_question"]
].drop_duplicates()


# NO; this should be there, so this is a problem with related questions....
# Go back and fix this problem.
raw_data = pd.read_csv("../data/dump/raw_data.csv")
raw_data[
    (raw_data["entry_id"] == 2103)
    & (raw_data["question_name"] == "The supreme high god has knowledge of this world")
]

answers = pd.read_csv("../data/preprocessed/answers.csv")
answers[answers["question_id"] == 8002]


shg_answers = pd.read_csv("../data/preprocessed/shg_answers.csv")
shg_answers[shg_answers["question_id"] == 8002]


# Explain the problem for Willis;
answers = pd.read_csv("../data/preprocessed/answers.csv")
answers = answers[
    ["entry_id", "question_id", "related_question_id", "question_name", "poll"]
].drop_duplicates()
question_relation = pd.read_csv("../data/dump/question_relation.csv")
question_relation[question_relation["question_id"] == 8002]
question_relation[question_relation["related_question_id"] == 8002]

question_relation[question_relation["question_id"] == 8012]
question_relation[question_relation["related_question_id"] == 8012]

answers[answers["question_id"] == 8002]["poll"].unique()
answers[answers["question_id"] == 4848]
answers[answers["related_question_id"] == 4838]


""" mail to willis: 
1. Have not heard back from her.
2. I think there is an error in the question relation for "
3. Is it correctly understood that the Place poll does not have all of the questions for supernatural monitoring and supernatural high gods that the text and the group poll has?

"""
