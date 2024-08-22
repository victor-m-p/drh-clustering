import pandas as pd


def find_entries(entry_tags, entrytag_id):
    matched_entries = (
        entry_tags[
            (entry_tags["entrytag_id"].isin(entrytag_id))
            | (entry_tags["parent_entrytag_id"].isin(entrytag_id))
        ]["entry_id"]
        .unique()
        .tolist()
    )

    return matched_entries


# loads
entry_tags = pd.read_csv("../data/raw/entity_tags.csv")
entry_metadata = pd.read_csv("../data/raw/entry_data.csv")

# christian tags
christian_tags = [
    18,  # Christian Traditions
    774,  # Early Christianity
    775,  # Early Christianity
    915,  # Evangelicalism
    971,  # Methodism
    984,  # Medieval Christianity
    996,  # Roman Catholic
    999,  # Catholic
    1006,  # Christian Restorationism
    1014,  # Christianity of the Global south
    1015,  # Born Again Christianity
    1030,  # American Christianity
    1031,  # Pentecostal
    1032,  # Protestantism
    1169,  # Early Christian Monasticism in Egypt
    1377,  # Christian monasticism
    1424,  # Christian Theology
    1570,  # Christianity
    1573,  # Christian
    1575,  # Christianity
    43608,  # Celtic Christianity
    43643,  # Orthodox Christianity
]

# islamic tags
islamic_tags = [
    24,  # Islamic traditions
    1305,  # Hispano-Islamic
    1390,  # Shi'a Islam
    1513,  # Islamic Theology
    27689,  # Islamic Law
    27702,  # Islamic Ethics
    43600,  # Sunni Islam
]

# chinese
chinese_tags = [
    123,  # Chinese Religion
    1083,  # Early Chinese text
    1102,  # Chinese Buddhist text
    1123,  # Early Chinese Traditions
    1258,  # China
    1291,  # Chinese Buddhism
    1415,  # Chinese Rites Controversy
    1680,  # Chinese Daoist text
    1721,  # Modern classics in Chinese philosophy
]

# buddhist
buddhist_tags = [
    14,  # Buddhist Traditions
    992,  # Tibetan Buddhism
    993,  # Tantric Buddhism
    1087,  # Yogacara Buddhism
    1089,  # Mahayana Buddhism
    1090,  # Yogacara Buddhism
    1102,  # Chinese Buddhist text
    1103,  # Chan Buddhist text
    1291,  # Chinese Buddhism
    1576,  # Zen Buddhism
    1577,  # Chan Buddhism
    1578,  # Japanese Buddhism
    43661,  # Buddhist Sutra
]

# Christian entries
christian_entries = find_entries(entry_tags, christian_tags)
islamic_entries = find_entries(entry_tags, islamic_tags)
chinese_entries = find_entries(entry_tags, chinese_tags)
buddhist_entries = find_entries(entry_tags, buddhist_tags)

# join with entry_metadata
entry_metadata["christian"] = entry_metadata["entry_id"].isin(christian_entries)
entry_metadata["islamic"] = entry_metadata["entry_id"].isin(islamic_entries)
entry_metadata["chinese"] = entry_metadata["entry_id"].isin(chinese_entries)
entry_metadata["buddhist"] = entry_metadata["entry_id"].isin(buddhist_entries)

# only take groups
answers_groups = pd.read_csv("../data/preprocessed/answers_subset_groups.csv")
answers_groups = answers_groups[["entry_id"]].drop_duplicates()
entry_tags = entry_metadata.merge(answers_groups, on="entry_id", how="inner")

# write to csv
entry_metadata.to_csv("entry_tags.csv", index=False)
