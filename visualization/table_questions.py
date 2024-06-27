# write the tables of questions
import pandas as pd

# setup
superquestion = "monitoring"  # shg
df_theta = pd.read_csv(f"../data/EM/{superquestion}_theta_all.csv")

# write questions to file:
df_questions = df_theta[["question_id", "question_short"]].drop_duplicates()
df_questions.to_csv(f"../tables/{superquestion}_questions.csv", index=False)
