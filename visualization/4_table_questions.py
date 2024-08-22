# write the tables of questions
import pandas as pd

answers = pd.read_csv("../data/preprocessed/answers_subset_groups.csv")

# we need to add whether the super-question is monitoring or shg
question_coding = {
    # monitoring
    2861: "supernatural monitoring",
    2883: "supernatural monitoring",
    2887: "supernatural monitoring",
    2898: "supernatural monitoring",
    2902: "supernatural monitoring",
    2910: "supernatural monitoring",
    2899: "supernatural monitoring",
    2911: "supernatural monitoring",
    2917: "supernatural monitoring",
    2921: "supernatural monitoring",
    2923: "supernatural monitoring",
    2928: "supernatural monitoring",
    2930: "supernatural monitoring",
    2939: "supernatural monitoring",
    2941: "supernatural monitoring",
    2942: "supernatural monitoring",
    # shg
    2944: "supreme high god",
    2948: "supreme high god",
    2958: "supreme high god",
    2962: "supreme high god",
    2970: "supreme high god",
    2972: "supreme high god",
    2974: "supreme high god",
    2978: "supreme high god",
    2982: "supreme high god",
    2984: "supreme high god",
    2985: "supreme high god",
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
answers.to_csv("../tables/questions.csv", index=False)
answers.to_latex("../tables/questions.tex", index=False)
