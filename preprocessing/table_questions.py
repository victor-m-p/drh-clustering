# write the tables of questions
import os
import pandas as pd

answers = pd.read_csv("../data/preprocessed/answers_subset_groups.csv")

# we need to add whether the super-question is monitoring or shg
# (parents checked against parent_question_id in the raw data: 2890 = monitoring, 2919 = shg)
question_coding = {
    # monitoring (n=20)
    2861: "supernatural monitoring",
    2883: "supernatural monitoring",
    2887: "supernatural monitoring",
    2898: "supernatural monitoring",
    2902: "supernatural monitoring",
    2911: "supernatural monitoring",
    2917: "supernatural monitoring",
    2921: "supernatural monitoring",
    2923: "supernatural monitoring",
    2928: "supernatural monitoring",
    2930: "supernatural monitoring",
    2939: "supernatural monitoring",
    2942: "supernatural monitoring",
    2962: "supernatural monitoring",
    2970: "supernatural monitoring",
    2972: "supernatural monitoring",
    2974: "supernatural monitoring",
    2978: "supernatural monitoring",
    2982: "supernatural monitoring",
    2985: "supernatural monitoring",
    # shg (n=16)
    2899: "supreme high god",
    2910: "supreme high god",
    2941: "supreme high god",
    2944: "supreme high god",
    2948: "supreme high god",
    2958: "supreme high god",
    2984: "supreme high god",
    3192: "supreme high god",
    3218: "supreme high god",
    3229: "supreme high god",
    3233: "supreme high god",
    3247: "supreme high god",
    3283: "supreme high god",
    3288: "supreme high god",
    3296: "supreme high god",
    3328: "supreme high god",
}

answers["super_question"] = answers["question_id"].map(question_coding)
answers = answers[["question_id", "question_short", "super_question"]].drop_duplicates()

# rename
answers = answers.rename(
    columns={
        "question_id": "Question ID",
        "question_short": "Question",
        "super_question": "Parent Question",
    }
)

# sort
answers = answers.sort_values(by=["Parent Question", "Question ID"])

# save
os.makedirs("tables", exist_ok=True)
answers.to_csv("tables/questions.csv", index=False)
answers.to_latex("tables/questions.tex", index=False)
