question_coding = {
    # monitoring
    "2861": "murder other religions",
    "2883": "murder coreligionists",
    "2887": "honouring oaths",
    "2898": "ritual observance",
    "2899": "other elite loyalty",
    "2902": "non-lethal fighting",
    "2910": "is kin to elites",
    "2911": "lying",
    "2917": "laziness",
    "2921": "property crimes",
    "2923": "shirking risk",
    "2928": "prosocial norm adherence",
    "2930": "performance of rituals",
    "2939": "personal hygiene",
    "2941": "is anthropomorphic",
    "2942": "gossiping",
    # shg
    "2944": "is chthonic",
    "2948": "is sky deity",
    "2958": "is monarch fused",
    "2962": "sorcery",
    "2970": "taboos",
    "2972": "murder other polities",
    "2974": "disrespecting elders",
    "2978": "sex",
    "2982": "conversion non-religionists",
    "2984": "is unquestionably good",
    "2985": "economic fairness",
    "3192": "positive emotion",
    "3218": "permissible to worship other god?",
    "3229": "negative emotion",
    "3233": "knowledge this world",
    "3247": "causal efficacy the world",
    "3283": "possesses hunger",
    "3288": "indirect causal efficacy the world",
    "3296": "communicates with living",
    "3328": "is monarch manifestation",
    #
}

# Polls included
polls = ["Religious Group (v6)", "Religious Group (v5)", "Religious Text (v1.0)"]

# Manually going through inconsistent answers (2024-04-09)
correct_answers = [
    # entry_id, question_id, answer
    [211, 3218, 0],
    [211, 3218, 1],
    [439, 2883, 1],
    [439, 2883, 0],
    [439, 2902, 0],  # also has don't know
    [439, 2911, 0],  # also has don't know
    [439, 2917, 1],
    [439, 2917, 0],
    [439, 2970, 1],
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
    [1268, 4978, 1],  # also don't know
    [1508, 8150, 1],  # also don't know
    [1508, 8151, 1],  # also don't know
    [1508, 8152, 1],  # also don't know
    [1508, 8165, -1],
    [1508, 8167, 1],  # also don't know
    [1508, 8171, 1],  # also don't know
    [1535, 4835, 0],
    [1535, 4855, 0],
    [1785, 8150, 1],
    [1785, 8173, 1],
    [1875, 7993, 1],  # also don't know
    [1985, 4853, -1],
    [1985, 4854, -1],
    [2052, 4830, 0],
    [2052, 4830, 1],
    [2052, 4854, 0],
    [2052, 4854, 1],
    [2054, 4833, 0],
    [2054, 4833, 1],
    [2054, 4849, 0],
    [2054, 4849, 1],
    [2059, 8017, 1],
    [2059, 8018, 1],
    [2059, 8023, 1],
    [2074, 4827, 1],
    [2079, 8018, 1],
    [2272, 7998, 1],
    [2272, 7998, 0],
]
