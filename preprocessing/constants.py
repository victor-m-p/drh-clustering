# Give short names to questions
question_coding = {
    # MONITORING
    # NB: "care about other" left out intentionally
    "Is supernatural monitoring present:": "monitoring present",  # level: 0
    "There is supernatural monitoring of prosocial norm adherence in particular:": "prosocial norm adherence",  # level: 1 ...
    "Supernatural beings care about taboos:": "taboos",
    "Supernatural beings care about murder of coreligionists:": "murder coreligionists",
    "Supernatural beings care about murder of members of other religions:": "murder other religions",
    "Supernatural beings care about murder of members of other polities:": "murder other polities",
    "Supernatural beings care about sex:": "sex",
    "Supernatural beings care about lying:": "lying",
    "Supernatural beings care about honouring oaths:": "honouring oaths",
    "Supernatural beings care about laziness:": "laziness",
    "Supernatural beings care about sorcery:": "sorcery",
    "Supernatural beings care about non-lethal fighting:": "non-lethal fighting",
    "Supernatural beings care about shirking risk:": "shirking risk",
    "Supernatural beings care about disrespecting elders:": "disrespecting elders",
    "Supernatural beings care about gossiping:": "gossiping",
    "Supernatural beings care about property crimes:": "property crimes",
    "Supernatural beings care about proper ritual observance:": "ritual observance",
    "Supernatural beings care about performance of rituals:": "performance of rituals",
    "Supernatural beings care about conversion of non-religionists:": "conversion non-religionists",
    "Supernatural beings care about economic fairness:": "economic fairness",
    "Supernatural beings care about personal hygiene:": "personal hygiene",
    # SHG
    # NB: "Other feature(s) of supreme high god" left out intentionally
    # NB: "The supreme high god possesses/exhibis some other feature" left out intentionally
    "Are supernatural beings present:": "supernatural beings present",  # level: 0
    "A supreme high god is present:": "supreme high god present",  # level: 1
    "The supreme high god is anthropomorphic:": "is anthropomorphic",  # level: 2 ...
    "The supreme high god is a sky deity:": "is sky deity",
    "The supreme high god is chthonic (of the underworld):": "is chthonic",
    "The supreme high god is fused with the monarch (king=high god):": "is monarch fused",
    "The monarch is seen as a manifestation or emanation of the high god:": "is monarch manifestation",
    "The supreme high god is a kin relation to elites:": "is kin to elites",
    "The supreme high god has another type of loyalty-connection to elites:": "other elite loyalty",
    "The supreme high god is unquestionably good:": "is unquestionably good",
    "The supreme high god has knowledge of this world:": "knowledge this world",
    "The supreme high god has deliberate causal efficacy in the world:": "causal efficacy the world",
    "The supreme high god has indirect causal efficacy in the  world:": "indirect causal efficacy the world",
    "The supreme high god exhibits positive emotion:": "positive emotion",
    "The supreme high god exhibits negative emotion:": "negative emotion",
    "The supreme high god possesses hunger:": "possesses hunger",
    "Is it permissible to worship supernatural beings other than the high god:": "permissible to worship other god?",
    "The supreme high god communicates with the living:": "communicates with living",
}

# Polls included
polls = ["Religious Group (v6)", "Religious Group (v5)", "Religious Text (v1.0)"]

# Manually going through inconsistent answers
correct_answers = [
    # entry_id, question_id, answer
    [211, 3218, 0],
    [211, 3218, 1],
    [416, 2890, 1],
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
    [590, 2893, 1],
    [613, 4828, 1],
    [613, 4828, 0],
    [645, 4954, 1],
    [645, 4962, 1],
    [645, 4963, 1],
    [645, 4970, 1],
    [645, 4980, 1],
    [657, 4828, 1],
    [671, 4828, 1],
    [671, 4828, 0],
    [684, 4849, 1],
    [684, 4849, 0],
    [727, 4927, 1],
    [739, 4954, 1],
    [900, 4954, -1],
    [929, 4954, 1],
    [929, 4954, 0],
    [1038, 4849, 1],
    [1038, 4858, 1],
    [1062, 7991, 1],
    [1101, 4833, 0],
    [1144, 7992, 1],
    [1234, 4972, 1],
    [1268, 4978, 1],  # also don't know
    [1289, 4827, 1],
    [1306, 4827, 1],
    [1308, 4828, 1],
    [1390, 4828, 1],
    [1390, 4828, 0],
    [1432, 8135, 0],
    [1458, 4828, 1],
    [1458, 4828, 0],
    [1508, 8150, 1],  # also don't know
    [1508, 8151, 1],  # also don't know
    [1508, 8152, 1],  # also don't know
    [1508, 8165, -1],
    [1508, 8167, 1],  # also don't know
    [1508, 8171, 1],  # also don't know
    [1522, 4828, 1],
    [1535, 4835, 0],
    [1535, 4855, 0],
    [1535, 4954, 1],
    [1551, 7991, 1],
    [1784, 8135, 0],
    [1785, 8150, 1],
    [1785, 8173, 1],
    [1805, 4827, 1],  # expert 1
    [1805, 4827, 0],  # expert 2
    [1805, 4954, 1],  # expert 1
    [1805, 4954, 0],  # expert 2
    [1875, 7993, 1],  # also don't know
    [1985, 4853, -1],
    [1985, 4854, -1],
    [2059, 8017, 1],
    [2059, 8018, 1],
    [2059, 8023, 1],
    [2074, 4827, 1],
    [2079, 8018, 1],
]
