question_coding = {
    # monitoring (n=20)
    "2861": "murder other religions", 
    "2883": "murder coreligionists", 
    "2887": "honouring oaths", 
    "2898": "ritual observance", 
    "2902": "non-lethal fighting", 
    "2911": "lying", 
    "2917": "laziness", 
    "2921": "property crimes", 
    "2923": "shirking risk", 
    "2928": "prosocial norm adherence", 
    "2930": "performance of rituals", 
    "2939": "personal hygiene", 
    "2942": "gossiping", 
    "2962": "sorcery", 
    "2970": "taboos", 
    "2972": "murder other polities",
    "2974": "disrespecting elders",
    "2978": "sex",
    "2982": "conversion non-religionists",
    "2985": "economic fairness",
    # shg (n=16)
    "2899": "other elite loyalty",
    "2910": "is kin to elites",
    "2941": "is anthropomorphic",
    "2944": "is chthonic",
    "2948": "is sky deity",
    "2958": "is monarch fused",
    "2984": "is unquestionably good",
    "3192": "positive emotion",
    "3218": "permissible to worship other god?",
    "3229": "negative emotion",
    "3233": "knowledge this world",
    "3247": "causal efficacy the world",
    "3283": "possesses hunger",
    "3288": "indirect causal efficacy the world",
    "3296": "communicates with living",
    "3328": "is monarch manifestation",
}

# same tree in all three polls (related ids):
# 2890 -> monitoring questions
# 2893 -> 2919 -> shg questions
parent_coding = {
    "2890": "supernatural monitoring present",
    "2893": "supernatural beings present",
    "2919": "supreme high god present",
}
monitoring_questions = [2861, 2883, 2887, 2898, 2902, 2911, 2917, 2921, 2923, 2928, 2930, 2939, 2942, 2962, 2970, 2972, 2974, 2978, 2982, 2985]
shg_questions = [2899, 2910, 2941, 2944, 2948, 2958, 2984, 3192, 3218, 3229, 3233, 3247, 3283, 3288, 3296, 3328]
parent_question = {q: 2890 for q in monitoring_questions} | {q: 2919 for q in shg_questions} | {2919: 2893}
# inferred "Yes" (not "No") when the parent is "No": no supreme high god -> permissible to worship other gods
infer_yes = [3218]

# Polls included
polls = ["Religious Group (v6)", "Religious Group (v5)", "Religious Text (v1.0)"]

# Covariate yes/no questions (related ids; see curate_covariates.py)
# short names follow the group wording; several text questions ask something else (question_name is kept per poll)
covariate_coding = {
    # religion and politics
    "2300": "official political support",  # text: is the production of the text funded by the polity
    # children of 2300 (only asked when 2300 is "Yes"; "No" inferred when 2300 is "No", see covariate_infer_no)
    "2339": "head of polity is head of religion",  # text: leaders of the polity and the religion the same figure
    "2319": "political officials are religious officials",  # text: involved in the support of textual production
    # supernatural punishment and reward
    "3420": "supernatural punishment",
    "3437": "supernatural reward",
    # children of 3420: when (only asked when 3420 is "Yes")
    "3440": "punishment this life",
    "3444": "punishment afterlife",
    # grandchildren of 3420: who (under 3480, is the cause or agent known) and why (under 3485, is the reason known)
    "3477": "punishment by high god only",
    "3478": "punishment by many beings",
    "3479": "punishment impersonal",
    "3482": "punishment for group norms",
    "3483": "punishment for ritual",
    "3484": "punishment random",
    "3486": "punishment for selfishness",
    # children of 3437: when (only asked when 3437 is "Yes")
    "3434": "reward this life",
    "3450": "reward afterlife",
    # grandchildren of 3437: who and why (both under 3469, is the cause/purpose known)
    "3472": "reward by high god only",
    "3466": "reward by many beings",
    "3470": "reward impersonal",
    "3473": "reward for group norms",
    "3471": "reward for ritual",
    "3467": "reward random",
    "3468": "reward for selfishness",
    # written language
    "3166": "own written language",  # text: written in distinctly religious/sacred language
}
# covariate questions with "No" inferred when their parent is "No" (child: parent)
# punishment and reward: inferred from the top question only, never from a "No" gateway ("reason not known");
# the "Other [specify]" questions and the gateways themselves are not used
punishment_questions = ["3440", "3444", "3477", "3478", "3479", "3482", "3483", "3484", "3486"]
reward_questions = ["3434", "3450", "3472", "3466", "3470", "3473", "3471", "3467", "3468"]
covariate_infer_no = (
    {"2339": "2300", "2319": "2300"}
    | {q: "3420" for q in punishment_questions}
    | {q: "3437" for q in reward_questions}
)

# Society type (related id 3492): answer -> level; answer_value has the same codes (1-5) for groups,
# but is -1 for nearly all text answers, so we code from the answer text
social_complexity_levels = {
    "A band": 1, "A tribe": 2, "Una tribu": 2, "A chiefdom": 3, "Una sociedad de jefatura": 3,
    "A state": 4, "Un estado": 4, "An empire": 5, "Un imperio": 5,
}
social_complexity_labels = {1: "band", 2: "tribe", 3: "chiefdom", 4: "state", 5: "empire"}
# "A band" is translated as "a group" (French, Chinese), and chosen for e.g. Wu Zetian's State Buddhism: not coded
social_complexity_mistranslated = ["Un groupe", "一个团体"]

# Manually going through inconsistent answers (2024-04-09)
correct_answers = [
    # entry_id, question_id, answer
    [211, 3218, 0],
    [211, 3218, 1],
    [439, 2883, 1],
    [439, 2883, 0],
    [439, 2902, 0],
    [439, 2911, 0],
    [439, 2917, 1],
    [439, 2917, 0],
    [439, 2970, 1], # matters: but also seeing 0 on website (2026)
    [441, 2928, 1],
    [441, 2928, 0],
    [580, 2941, 1],
    [580, 2941, 0],
    [645, 4962, 1],
    [645, 4963, 1],
    [645, 4970, 1],
    [645, 4980, 1],
    [684, 4849, 1],
    [684, 4849, 0],
    [1038, 4849, 1],
    [1038, 4858, 1],
    [1101, 4833, 0],
    [1234, 4972, 1],
    [1268, 4978, 1],
    [1508, 8150, 1],
    [1508, 8151, 1],
    [1508, 8152, 1],
    [1508, 8165, -1],
    [1508, 8167, 1],
    [1508, 8171, 1],
    [1535, 4835, 0],
    [1535, 4855, 0],
    [1785, 8150, 1],
    [1785, 8173, 1],
    [1875, 7993, 1],
    [1985, 4853, -1], # matters: not sure whether correct.
    [1985, 4854, -1], # matters: not sure whether correct.
    [2052, 4830, 0],
    [2052, 4830, 1],
    [2052, 4854, 0],
    [2052, 4854, 1],
    [2054, 4833, 0],
    [2054, 4833, 1],
    [2054, 4849, 0],
    [2054, 4849, 1],
    [2059, 8017, 1], # matters (but only text): check again.
    [2059, 8018, 1], # matters (but only text): check again.
    [2059, 8023, 1], # matters (but only text): check again.
    [2074, 4827, 1], # this is superquestion so might not matter.
    [2079, 8018, 1],
    [2272, 7998, 1],
    [2272, 7998, 0],
]
