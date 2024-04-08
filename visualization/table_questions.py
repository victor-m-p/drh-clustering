# write the tables of questions
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

#### setup ####
c = 7  # minimize BIC
superquestion = "monitoring"
df_theta = pd.read_csv(f"../data/EM/{superquestion}_theta_{c}_all.csv")

# write questions to file:
df_questions = df_theta[["question_id", "question_short"]].drop_duplicates()
df_questions.to_csv(f"../tables/{superquestion}_questions.csv", index=False)
