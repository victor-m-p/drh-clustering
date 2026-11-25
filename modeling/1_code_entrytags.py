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

# abrahamic: christian, islamic or jewish (as coded above), or tagged "Abrahamic" (anywhere on the path; new 2026-11-17)
abrahamic_tags = [
    905,  # Abrahamic (top level; Christian, Islam, Judaism and a few sub-tags below it)
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
    959: "Iron Age Britain: Romano-Celtic Era (-55 to 286): starts before Christianity (as 810)",
}
islamic_exclude = {
    441: "Worshipers of Śītalā: Hindu goddess cult; matched via Islamic Traditions under Indic (661)",
}
jewish_exclude = {
    1191: "Religion in Greco-Roman Alexandria: multi-religious city, Jews one group among several",
    1306: "Philistine Religion (-1200 to -600): Philistines, not Israelites; matched via Judeans and Israelites (1308)",
    # Judaism is counted from the exile and Second Temple period on; Iron Age Israelite religion (not yet
    # monotheistic) is not (2026-11-17; to be checked by an expert). Entry 300, also "Israelite Religion", is not
    # tagged as Jewish.
    189: "Israelite Religion (-1200 to -515): Iron Age, before the exile",
    2348: "Ancient Israelite Religion (Iron Age) (-1200 to -500): Iron Age, before the exile",
}
abrahamic_exclude = {  # entries the "Abrahamic" tag brings in that we leave out (on top of the exclusions above)
    1258: "Religion in Judah (-1000 to -586): Iron Age, before the exile (as 189, 2348)",
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
    2125: "Islam in Nigeria and Sheikh Usman dan Fodio (text): only tagged 'Abrahamic' and 'African Religion'",
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

# abrahamic: in any of the three traditions, or tagged "Abrahamic" (unless excluded by hand from one of the three)
abrahamic_tagged = find_entries(
    entry_tags, abrahamic_tags, set(christian_exclude) | set(islamic_exclude) | set(jewish_exclude) | set(abrahamic_exclude)
)
abrahamic_entries = sorted(set(christian_entries) | set(islamic_entries) | set(jewish_entries) | set(abrahamic_tagged))

# join with entry_metadata
entry_metadata["christian"] = entry_metadata["entry_id"].isin(christian_entries)
entry_metadata["islamic"] = entry_metadata["entry_id"].isin(islamic_entries)
entry_metadata["jewish"] = entry_metadata["entry_id"].isin(jewish_entries)
entry_metadata["hindu"] = entry_metadata["entry_id"].isin(hindu_entries)
entry_metadata["chinese"] = entry_metadata["entry_id"].isin(chinese_entries)
entry_metadata["buddhist"] = entry_metadata["entry_id"].isin(buddhist_entries)
entry_metadata["abrahamic"] = entry_metadata["entry_id"].isin(abrahamic_entries)

# write to csv
entry_metadata.to_csv("data/entry_tags.csv", index=False)

"""
Coding sheet for the six traditions, tab 1: tags (for review by an expert).

Entries: our sample (groups and texts; entry_covariates.csv). One row per tag on the lists above that matches at least
one of these entries (tags that only match religious places are left out, e.g. China, Zen Buddhism), plus the
n_unclassified tags (religious tree) with the most uncoded entries (in none of the six traditions) that have none of the
listed tags on their path. Columns:
- tradition: our current coding (several if a tag is on more than one list; "none" if on no list)
- comment: the comment next to the tag in the lists above (read from this file), "not used" notes, and the entries
  the tag brings in that we exclude by hand
- expert_tradition: empty, for the expert (copy the current tradition or change it)
- tag_id, tag, path (in the tagging tree, without the root "Religious Group")
- entries: entries in our sample matched through the tag (carrying it or a tag below it); texts: of which texts;
  uncoded: of which in none of the six traditions (what the tag could add)
- examples: up to three of these entries (earliest first), with their years
- entry_ids: all of these entries (entry ids, earliest first)
Writes data/coding_traditions_tags.tsv (tab-separated, since fields contain commas; to import as a sheet).
"""

n_unclassified = 50
traditions = {
    "christian": christian_tags, "islamic": islamic_tags, "jewish": jewish_tags,
    "buddhist": buddhist_tags, "hindu": hindu_tags, "chinese": chinese_tags,
}
excludes = {
    "christian": christian_exclude, "islamic": islamic_exclude, "jewish": jewish_exclude,
    "buddhist": buddhist_exclude, "hindu": hindu_exclude, "chinese": chinese_exclude,
}

# comments next to the tags in the lists above, and the "not used" notes below them (read from this file)
source = open(__file__, encoding="utf-8").read()
comments = {}
tag_names = entry_tags.drop_duplicates("entrytag_id").set_index("entrytag_id")["entrytag_name"]
for tradition in traditions:
    block = re.search(rf"^{tradition}_tags = \[\n(.*?)^\]", source, re.S | re.M)
    if block is None:
        raise ValueError(f"tag list {tradition}_tags not found in {__file__}")
    notes = []
    for line in (line.strip() for line in block.group(1).splitlines()):
        listed = re.match(r"(\d+),\s*#\s*(.*)", line)
        if listed:
            # keep what the comment adds to the tag name (e.g. "under Chinese Religion", or a translation)
            tag, comment = int(listed.group(1)), listed.group(2)
            name = str(tag_names.get(tag, ""))
            if name and comment.casefold().startswith(name.casefold()):
                comment = comment[len(name):].strip(" ;")
            if comment.startswith("(") and ")" in comment:  # "(under X); more" -> "under X; more"
                end = comment.index(")")
                comment = comment[1:end] + comment[end + 1:]
            if comment:
                comments.setdefault(tag, []).append(comment)
        elif line.startswith("#") and not re.match(r"#\s*\d+,", line) and "new tags" not in line:
            notes.append(line.lstrip("# "))
    note = " ".join(notes)
    for tag in re.findall(r"\b(\d{2,6})\b", note):
        comments.setdefault(int(tag), []).append(f"{tradition}: {note}")

# entries in our sample (groups and texts), and the tags they are matched through (their tags and all ancestors)
sample = pd.read_csv("../data/preprocessed/entry_covariates.csv")
through = entry_tags[entry_tags["entry_id"].isin(sample["entry_id"])][["entry_id", "tag_ids"]].explode("tag_ids")
through = through.rename(columns={"tag_ids": "tag_id"}).drop_duplicates()
through["tag_id"] = through["tag_id"].astype(int)
through = through.merge(entry_metadata[["entry_id", "entry_name", "year_from", "year_to", "poll_name"]], on="entry_id")
through["text"] = through["poll_name"].str.contains("Text")

# entries a listed tag brings in that we exclude by hand from its tradition
entry_names = entry_metadata.drop_duplicates("entry_id").set_index("entry_id")["entry_name"]
for tradition, tags in traditions.items():
    for tag in tags:
        brought = sorted(set(through.loc[through["tag_id"] == tag, "entry_id"]) & set(excludes[tradition]))
        if brought:
            listing = "; ".join(f"{e} ({entry_names[e]})" for e in brought)
            comments.setdefault(tag, []).append(f"brings in entries excluded by hand from {tradition}: {listing}")

root = 8  # "Religious Group"

def path_names(tag):
    return " › ".join(str(tag_names.get(i, i)) for i in paths.get(tag, [tag]) if i != root)

def examples(tag):
    rows = through[through["tag_id"] == tag].sort_values("year_from").head(3)
    return "; ".join(f"{r.entry_name} ({'text, ' if r.text else ''}{r.year_from} to {r.year_to})" for r in rows.itertuples())

# listed tags (current coding), and the unclassified tags in the religious tree with the most uncoded entries
listed = {}
for tradition, tags in traditions.items():
    for tag in tags:
        listed.setdefault(tag, []).append(tradition)
n_entries = through.groupby("tag_id")["entry_id"].nunique()
uncoded_entries = entry_metadata.loc[~entry_metadata[list(traditions)].any(axis=1), "entry_id"]
n_uncoded = through[through["entry_id"].isin(uncoded_entries)].groupby("tag_id")["entry_id"].nunique()
listed_ids = set(listed)
religious = {t for t, p in paths.items() if p[0] == root and t != root}
unclassified = sorted(t for t in religious if not listed_ids.intersection(paths[t]))
unclassified = n_uncoded.reindex(unclassified).dropna().sort_values(ascending=False, kind="stable").head(n_unclassified).index

sheet = pd.DataFrame(
    [{"tag_id": t, "tradition": "; ".join(listed[t])} for t in listed]
    + [{"tag_id": int(t), "tradition": "none"} for t in unclassified]
)
sheet["comment"] = sheet["tag_id"].map(lambda t: " | ".join(comments.get(t, [])))
sheet["expert_tradition"] = ""
sheet["tag"] = sheet["tag_id"].map(tag_names)
sheet["path"] = sheet["tag_id"].map(path_names)
sheet["entries"] = sheet["tag_id"].map(n_entries).fillna(0).astype(int)
sheet["texts"] = sheet["tag_id"].map(through[through["text"]].groupby("tag_id")["entry_id"].nunique()).fillna(0).astype(int)
sheet["uncoded"] = sheet["tag_id"].map(n_uncoded).fillna(0).astype(int)
sheet = sheet[sheet["entries"] > 0]  # tags that only match religious places
sheet["examples"] = sheet["tag_id"].map(examples)
entry_ids = through.sort_values("year_from").groupby("tag_id")["entry_id"].apply(lambda e: "; ".join(map(str, e)))
sheet["entry_ids"] = sheet["tag_id"].map(entry_ids).fillna("")

# order: traditions as listed above (tags on several lists after their first), most entries first; then unclassified,
# most uncoded entries first
order = {t: i for i, t in enumerate(list(traditions) + ["none"])}
sheet["order"] = sheet["tradition"].str.split("; ").str[0].map(order)
sheet["rank"] = sheet["uncoded"].where(sheet["tradition"] == "none", sheet["entries"])
sheet = sheet.sort_values(["order", "rank", "entries"], ascending=[True, False, False], kind="stable").drop(columns=["order", "rank"])
sheet = sheet[["tradition", "comment", "expert_tradition", "tag_id", "tag", "path", "entries", "texts", "uncoded", "examples", "entry_ids"]]
assert not sheet.astype(str).apply(lambda c: c.str.contains("\t")).any().any()  # tabs separate the columns
sheet.to_csv("data/coding_traditions_tags.tsv", sep="\t", index=False)
print(sheet["tradition"].value_counts().to_string())

"""
Coding sheet for the six traditions, tab 2: entries (for review by an expert).

One row per entry in our sample (groups and texts). Columns:
- coding: none (no tradition, "other"), by hand (included or excluded by hand for at least one tradition) or automatic
  (through the tags only); rows in this order, so the automatic ones can largely be skipped
- type: group or text
- notes: reasons for the hand coding; "several traditions"; "starts before the tradition" (christian before 0 CE,
  islamic before 600 CE, buddhist before 600 BCE)
- reviewed: empty, for the expert to tick
- christian, islamic, jewish, buddhist, hindu, chinese: "x" where we code the entry (several possible), for the expert
  to change
- entry_id, entry, years, world_region, expert (who coded the entry), tags (its tags outside the language tree)
Writes data/coding_traditions_entries.tsv.
"""

starts = {"christian": 0, "islamic": 600, "buddhist": -600}  # entries starting earlier are flagged
coded = {t: set(e) for t, e in zip(traditions, [christian_entries, islamic_entries, jewish_entries,
                                                 buddhist_entries, hindu_entries, chinese_entries])}
includes = {
    "christian": christian_include, "islamic": islamic_include, "jewish": {},
    "buddhist": buddhist_include, "hindu": hindu_include, "chinese": {},
}
region_data = pd.read_csv("../data/sccsrv3/region_data.csv")[["region_id", "world_region"]].drop_duplicates("region_id")
entries = (
    entry_metadata[entry_metadata["entry_id"].isin(sample["entry_id"])]
    .drop_duplicates("entry_id")
    .merge(region_data, on="region_id", how="left")
)

# tags of each entry (all trees except language)
own = entry_tags[~entry_tags["entrytag_path"].fillna("").str.startswith("Language[")]
own_tags = own.groupby("entry_id")["entrytag_name"].apply(lambda t: "; ".join(dict.fromkeys(t)))


def notes(row):
    out = []
    for tradition in traditions:
        if row.entry_id in includes[tradition]:
            out.append(f"included by hand in {tradition}: {includes[tradition][row.entry_id]}")
        if row.entry_id in excludes[tradition]:
            out.append(f"excluded by hand from {tradition}: {excludes[tradition][row.entry_id]}")
    in_traditions = [t for t in traditions if row.entry_id in coded[t]]
    if len(in_traditions) > 1:
        out.append("several traditions")
    for tradition, start in starts.items():
        if tradition in in_traditions and row.year_from < start:
            out.append(f"starts before the tradition ({tradition}, {row.year_from})")
    return " | ".join(out)


by_hand = set().union(*includes.values(), *excludes.values())
entries["coding"] = "automatic"
entries.loc[entries["entry_id"].isin(by_hand), "coding"] = "by hand"
entries.loc[~entries["entry_id"].isin(set().union(*coded.values())), "coding"] = "none"
entries["type"] = entries["poll_name"].str.contains("Text").map({True: "text", False: "group"})
entries["notes"] = entries.apply(notes, axis=1)
entries["reviewed"] = ""
for tradition in traditions:
    entries[tradition] = entries["entry_id"].isin(coded[tradition]).map({True: "x", False: ""})
entries["entry"] = entries["entry_name"]
entries["years"] = entries["year_from"].astype(str) + " to " + entries["year_to"].astype(str)
entries["expert"] = entries["expert_name"]
entries["tags"] = entries["entry_id"].map(own_tags).fillna("")

entries["order"] = entries["coding"].map({"none": 0, "by hand": 1, "automatic": 2})
entries = entries.sort_values(["order", "type", "year_from"]).drop(columns="order")
columns = ["coding", "type", "notes", "reviewed", *traditions, "entry_id", "entry", "years", "world_region", "expert", "tags"]
entries = entries[columns]
assert not entries.astype(str).apply(lambda c: c.str.contains("\t")).any().any()  # tabs separate the columns
entries.to_csv("data/coding_traditions_entries.tsv", sep="\t", index=False)
print(pd.crosstab(entries["coding"], entries["type"]).to_string())

"""
Coding sheet for "Abrahamic" (for review by an expert, e.g. as a tab next to the two above).

Abrahamic = christian, islamic or jewish (as coded above), or tagged "Abrahamic" (905). Used as a yes/no covariate in
the region x time models (modeling/14_abrahamic.Rmd), where it is almost the same as "from 0 CE" in Southwest Asia,
Europe and Africa; the entries that break this pattern carry most of the information, so they come first.

Rows: one per entry in the modeling window (groups and texts in our sample; Southwest Asia, Europe, Africa and East
Asia; start year from 3000 BCE to 1500 CE; without eHRAF and Pulotu). Columns:
- entry, years (BCE / CE)
- abrahamic: "x" where we code the entry as Abrahamic, for the expert to change
- reviewed, expert_comment: empty, for the expert
- check: "by hand" (included or excluded by hand), "breaks the pattern" (Abrahamic before 0 CE, or not Abrahamic from
  0 CE in Southwest Asia, Europe or Africa) or "automatic"; rows in this order
- notes: reasons for the hand coding, and why the entry breaks the pattern
- type (group or text), world_region, entry_id, expert (who coded the entry), tags (outside the language tree)
Writes data/coding_abrahamic.tsv.
"""

western = ["Southwest Asia", "Europe", "Africa"]
window_regions = western + ["East Asia"]
hand = {
    "christian": (christian_include, christian_exclude), "islamic": (islamic_include, islamic_exclude),
    "jewish": ({}, jewish_exclude), "abrahamic": ({}, abrahamic_exclude),
}

ab = (
    entry_metadata[entry_metadata["entry_id"].isin(sample["entry_id"])]
    .drop_duplicates("entry_id")
    .merge(region_data, on="region_id", how="left")
)
source = ab["data_source"].fillna("")
ab = ab[
    ab["world_region"].isin(window_regions)
    & ab["year_from"].between(-3000, 1499)
    & (source != "eHRAF")
    & ~source.str.startswith("Pulotu")
].copy()
ab["is_abrahamic"] = ab["entry_id"].isin(abrahamic_entries)
ab["by_hand"] = ab["entry_id"].isin(set().union(*(set(i) | set(e) for i, e in hand.values())))
ab["breaks"] = (ab["is_abrahamic"] & (ab["year_from"] < 0)) | (
    ~ab["is_abrahamic"] & (ab["year_from"] >= 0) & ab["world_region"].isin(western)
)


def abrahamic_notes(row):
    out = []
    for tradition, (include, exclude) in hand.items():
        if row.entry_id in include:
            out.append(f"included by hand in {tradition}: {include[row.entry_id]}")
        if row.entry_id in exclude:
            out.append(f"excluded by hand from {tradition}: {exclude[row.entry_id]}")
    if row.is_abrahamic and row.year_from < 0:
        out.append("Abrahamic, starts before 0 CE")
    if not row.is_abrahamic and row.year_from >= 0 and row.world_region in western:
        out.append(f"not Abrahamic, starts from 0 CE in {row.world_region}")
    return " | ".join(out)


ab["check"] = "automatic"
ab.loc[ab["breaks"], "check"] = "breaks the pattern"
ab.loc[ab["by_hand"], "check"] = "by hand"
ab["entry"] = ab["entry_name"]
era = lambda y: f"{-y} BCE" if y < 0 else f"{y} CE"
ab["years"] = ab["year_from"].map(era) + " to " + ab["year_to"].map(era)
ab["abrahamic"] = ab["is_abrahamic"].map({True: "x", False: ""})
ab["reviewed"] = ""
ab["expert_comment"] = ""
ab["notes"] = ab.apply(abrahamic_notes, axis=1)
ab["type"] = ab["poll_name"].str.contains("Text").map({True: "text", False: "group"})
ab["expert"] = ab["expert_name"]
ab["tags"] = ab["entry_id"].map(own_tags).fillna("")

ab["order"] = ab["check"].map({"by hand": 0, "breaks the pattern": 1, "automatic": 2})
ab = ab.sort_values(["order", "type", "year_from"]).drop(columns="order")
columns = ["entry", "years", "abrahamic", "reviewed", "expert_comment", "check", "notes",
           "type", "world_region", "entry_id", "expert", "tags"]
ab = ab[columns]
assert ab["entry_id"].is_unique
assert not ab.astype(str).apply(lambda c: c.str.contains("\t")).any().any()  # tabs separate the columns
ab.to_csv("data/coding_abrahamic.tsv", sep="\t", index=False)
print(pd.crosstab([ab["check"], ab["abrahamic"]], ab["type"], margins=True).to_string())
