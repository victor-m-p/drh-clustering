"""
Code each entry for religious traditions (yes/no per tradition) from the DRH tagging tree.
An entry belongs to a tradition if any of the tradition's tags appears anywhere on the
path of any of its tags (so sub-tags count). Tag lists were reviewed against the full
tag vocabulary of the group entries in SCCSR.v3 (2026-10-12), including the Arabic- and
French-language tags. A few entries are included or excluded by hand (see below).
Writes data/entry_tags.csv (all entries, one row per entry).
"""

import re
import pandas as pd


def tag_paths(entry_tags):
    """tag id -> ids on its path in the tagging tree (from rows that have a path)"""
    rows = entry_tags.dropna(subset=["entrytag_path"]).drop_duplicates("entrytag_id")
    return {
        int(r["entrytag_id"]): [int(i) for i in re.findall(r"\[(\d+)\]", r["entrytag_path"])]
        for _, r in rows.iterrows()
    }


def tag_ids(row, paths):
    """
    All tag ids on a row's path in the tagging tree (the tag itself and all its ancestors).
    Rows without a path (a few, in SCCSR.v3): the tag itself plus the full path of its parent.
    """
    if isinstance(row["entrytag_path"], str):
        return paths[int(row["entrytag_id"])]
    ids = [int(row["entrytag_id"])]
    if pd.notna(row["parent_entrytag_id"]):
        parent = int(row["parent_entrytag_id"])
        ids += paths.get(parent, [parent])
    return ids


def find_entries(entry_tags, entrytag_id, exclude=(), include=()):
    # an entry matches if any of the tags is anywhere on the path of any of its tags
    entrytag_id = set(entrytag_id)
    matched = entry_tags[entry_tags["tag_ids"].apply(lambda ids: bool(entrytag_id.intersection(ids)))]
    matched_entries = [e for e in matched["entry_id"].unique().tolist() if e not in exclude]
    matched_entries += [e for e in include if e not in matched_entries]

    return matched_entries


# loads
entry_tags = pd.read_csv("../data/sccsrv3/entity_tags.csv")
entry_metadata = pd.read_csv("../data/sccsrv3/entry_data.csv")
paths = tag_paths(entry_tags)
entry_tags["tag_ids"] = entry_tags.apply(tag_ids, axis=1, paths=paths)

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
    # new tags (2026-10-12)
    917,  # Protestantism
    1343,  # Baptists
    237,  # Chinese Christian Traditions (under Chinese Religion)
    39,  # Nestorianism
    797,  # Pentacostal (under African Religions)
    1017,  # Aladura
    1021,  # Orthodoxy (generic tag; see christian_exclude)
    1618,  # Christian (under Abrahamic)
    381,  # Orthodox/Eastern Christian (under Armenian Religion)
    1605,  # Coptic
    1571,  # Arianism
    1574,  # Arianism
    972,  # Montanism
    973,  # New Prophecy (Montanism)
    27694,  # Albigenses
    1330,  # Augustine
    977,  # Tertullian
    1416,  # Jesuits; Society of Jesus
    1471,  # Mendicant Orders
    1590,  # Spanish Catholicism
    1333,  # Liberation Theology
    1398,  # Christian Mysticism
    27686,  # United Missionary Church of Africa (UMCA)
    43680,  # Evangelical Church Winning All
    43709,  # Caribbean Christianity
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
    # new tags (2026-10-12)
    1678,  # Islam (under Abrahamic); also brings in "Mauritius" (2518), a multi-religious island society
    997,  # Sufi (also brings in Baul Fakirs of Bengal, a Sufi-Vaishnava tradition)
    1470,  # Sufi Order
    1534,  # Islam (under African Religion)
    239,  # Chinese Islamic Traditions (under Chinese Religion)
    661,  # Islamic Traditions (under Indic Religious Traditions; see islamic_exclude)
    43635,  # الإسلام (Islam)
    43636,  # الديانة الإسلامية (Islamic religion)
    1507,  # شيعة (Shi'a)
    1509,  # إِمَامِيَّة (Imami Shi'a)
    1508,  # ٱثْنَا عَشَرِيَّة (Twelver Shi'a)
    43631,  # المذهب الحنفي (Hanafi school)
    43633,  # الدولة المرادية (Muradid state)
    27700,  # مجموعة سنية (Sunni group; French-language branch)
    43535,  # سنية مالكية (Maliki Sunni; French-language branch)
    43632,  # مجموعة حنفية (Hanafi group; French-language branch)
    1663,  # إباضية جزيرة جربة (Ibadis of Djerba; French-language branch)
]

# jewish tags (new 2026-10-12)
jewish_tags = [
    27,  # Jewish Traditions (see jewish_exclude)
    43519,  # Judaism (under Abrahamic)
    1308,  # Judeans and Israelites
    # not used: 43518 Judaism and 731 Diaspora Judaism in Rome (only add multi-religious
    # regional entries), 1293 Israelite Religion (also brings in Phoenicia)
]

# hindu tags (new 2026-10-12)
hindu_tags = [
    566,  # Hinduism (under Indic Religious Traditions)
    1244,  # Hinduism
    1059,  # Shaivism
    896,  # Vaishnavism
    1385,  # Neo-Vedanta
    1243,  # Southeast Asian Hinduism
    853,  # Balinese Hinduism
    799,  # Vedic Traditions
    512,  # Bhakti traditions (under Indic Religious Traditions)
    1610,  # Bhakti
    1036,  # Tamil Religious Groups
    # not used: 1458 Yoga (also brings in Contemporary Shingon), 510 Indic Religious
    # Traditions and 1037 South Asian Religion (too broad)
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
    # 1721,  # Modern classics in Chinese philosophy (not in SCCSR.v3)
    # new tags (2026-10-12)
    65,  # Chinese Buddhist Traditions (under Buddhist Traditions)
    1085,  # Confucianism (see chinese_exclude)
    243,  # Chinese Nestorian Traditions
    1264,  # Religious Confucianism (under Syncretic Religions)
    240,  # Chinese Islamic Traditions (under Islamic Traditions)
    1189,  # Redemptive Societies
    # not used: 1108 Daoism (only adds Shugendō, Japanese), 1251/1311/1312 region tags
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
    # 1577,  # Chan Buddhism (not in SCCSR.v3)
    1578,  # Japanese Buddhism
    # 43661,  # Buddhist Sutra (not in SCCSR.v3)
    # new tags (2026-10-12)
    383,  # Chinese Buddhist Traditions (under Chinese Religion)
    43719,  # Modern Buddhism
    # not used: 513 Indic Buddhist Traditions (only adds Śaiva Magic), 13 Bön
]

# entries matched by the tags above that we exclude by hand (entry_id: reason)
christian_exclude = {
    2220: "Ansar-ud-deen Society of Nigeria: Islamic; only matched via the generic 'Orthodoxy' tag (1021)",
    1293: "The Zapotec (-2000 to 2022): has a Roman Catholic tag, but the entry starts long before Christianity",
    810: "British Isles IV: Pre-Theodosian Roman Britain (-43 to 380): starts before Christianity",
    1903: "The 'Abbāsids: Islamic caliphate; Christian tags presumably refer to subject populations",
}
islamic_exclude = {
    441: "Worshipers of Śītalā: Hindu goddess cult; matched via Islamic Traditions under Indic (661)",
}
jewish_exclude = {
    1191: "Religion in Greco-Roman Alexandria: multi-religious city, Jews one group among several",
}
hindu_exclude = {}
chinese_exclude = {
    1041: "Korean Catholicism: Korean, only matched via Confucianism (1085)",
}
buddhist_exclude = {
    441: "Worshipers of Śītalā: Hindu goddess cult; also tagged Buddhist Traditions",
    1903: "The 'Abbāsids: Islamic caliphate; Buddhist tags presumably refer to subject populations",
}

# entries without a matching tag that we include by hand (entry_id: reason)
christian_include = {
    1958: "The Apostolic Faith Mission in Zimbabwe: Pentecostal church; only tagged 'African Religion'",
    2484: "Simon Kimbangu: the Kimbanguist church (African independent Christian); only tagged 'African Religions'",
    860: "Kimpa Vita: the Antonian movement (Kongolese Catholic); only tagged 'Bantu Religions'",
}
islamic_include = {
    2322: "The Umayyad State in the East (661-750): only tagged 'ruling group' (مجموعة حاكمة)",
    1776: "The Qadiriyya Order in Tunisia: Sufi order; only tagged 'Mysticism' and 'Religious Group (fr)'",
}
hindu_include = {
    374: "Non-dual Śaiva Tantra (Kashmir Śaivism): only tagged 'Indic Religious Traditions'",
    580: "Nāth Sampradāya: Śaiva yogic order; only tagged 'Indic Religious Traditions'",
}
buddhist_include = {
    2329: "Hòa Hảo: Vietnamese Buddhist reform movement (one tag is 'Phật Giáo Hòa Hảo', Hòa Hảo Buddhism)",
    185: "Shinnyo-en: Japanese Buddhist movement (Shingon lineage); tagged as a Shintō new religion",
}

# entries per tradition
christian_entries = find_entries(entry_tags, christian_tags, christian_exclude, christian_include)
islamic_entries = find_entries(entry_tags, islamic_tags, islamic_exclude, islamic_include)
jewish_entries = find_entries(entry_tags, jewish_tags, jewish_exclude)
hindu_entries = find_entries(entry_tags, hindu_tags, hindu_exclude, hindu_include)
chinese_entries = find_entries(entry_tags, chinese_tags, chinese_exclude)
buddhist_entries = find_entries(entry_tags, buddhist_tags, buddhist_exclude, buddhist_include)

# join with entry_metadata
entry_metadata["christian"] = entry_metadata["entry_id"].isin(christian_entries)
entry_metadata["islamic"] = entry_metadata["entry_id"].isin(islamic_entries)
entry_metadata["jewish"] = entry_metadata["entry_id"].isin(jewish_entries)
entry_metadata["hindu"] = entry_metadata["entry_id"].isin(hindu_entries)
entry_metadata["chinese"] = entry_metadata["entry_id"].isin(chinese_entries)
entry_metadata["buddhist"] = entry_metadata["entry_id"].isin(buddhist_entries)

# write to csv
entry_metadata.to_csv("data/entry_tags.csv", index=False)
