import numpy as np
import pandas as pd

raw_data = pd.read_csv("../data/dump/raw_data.csv")

raw_data = raw_data[
    [
        "poll",
        "question_id",
        "question_name",
        "entry_id",
        "entry_name",
        "answer",
        "value",
    ]
].drop_duplicates()

""" reason we did this is obvious: 
Many things are coded as 1: 
e.g., sources, year ranges, etc. 
But this is probably not an issue for us because we will never use these questions.
What would actually be nice would be to have a list of all of the questions that we 
would ever care about in a quantitative analysis (probably). 

"""
zero_answers = (
    raw_data[raw_data["value"] == 0].groupby("answer").size().reset_index(name="count")
).sort_values("count", ascending=False)
one_answers = (
    raw_data[raw_data["value"] == 1].groupby("answer").size().reset_index(name="count")
).sort_values("count", ascending=False)
negative_answers = (
    raw_data[raw_data["value"] == -1].groupby("answer").size().reset_index(name="count")
).sort_values("count", ascending=False)

zero_answers  # mostly no and a few other things
one_answers  # mostly yes (and 8000 other things)
negative_answers  # mostly Field/I don't know (and 11K other things).

### what about the other things? ###
test = raw_data[raw_data["value"] == 1]
test.groupby("answer").size().reset_index(name="count").sort_values(
    "count", ascending=False
)  # how do we find that sign?
test[~test["answer"].str.contains("Yes")].sample(n=20)

# ah, so is my answer here just bullshit?
# what about the ones that are "sources" for instance??
# I think I saw some on the website as well though.
# so we do need to do the 0/1 thing instead which is a pain in the ass.
