"""
Build the initial Valorant pro player dataset from known data.
No network access required - uses pre-compiled player data.

Output: data/processed/players.csv, data/processed/players.json
"""

import csv
import json
import os
import sys

# Player database: compiled from known VCT pro players
PLAYERS = [
    # === China (CN) ===
    # EDward Gaming (Champions 2024 winners)
    {"name": "ZmjjKK",   "team": "EDward Gaming",   "region": "China",   "age": 23, "championships": 2, "agents": ["Jett", "Raze", "Chamber"]},
    {"name": "Smoggy",   "team": "EDward Gaming",   "region": "China",   "age": 23, "championships": 2, "agents": ["Raze", "KAY/O", "Sova"]},
    {"name": "nobody",   "team": "EDward Gaming",   "region": "China",   "age": 26, "championships": 2, "agents": ["Sova", "Killjoy", "Cypher"]},
    {"name": "CHICHOO",  "team": "EDward Gaming",   "region": "China",   "age": 24, "championships": 2, "agents": ["Viper", "Omen", "Astra"]},
    {"name": "S1mon",    "team": "EDward Gaming",   "region": "China",   "age": 22, "championships": 1, "agents": ["Killjoy", "Cypher", "Sage"]},
    {"name": "Haodong",  "team": "EDward Gaming",   "region": "China",   "age": 27, "championships": 1, "agents": ["Killjoy", "Sova", "Cypher"]},
    # FunPlus Phoenix
    {"name": "Life",     "team": "FunPlus Phoenix", "region": "China",   "age": 25, "championships": 0, "agents": ["Raze", "Neon", "Jett"]},
    {"name": "whz",      "team": "FunPlus Phoenix", "region": "China",   "age": 23, "championships": 0, "agents": ["Jett", "Raze", "Sova"]},
    {"name": "AAAA",     "team": "FunPlus Phoenix", "region": "China",   "age": 25, "championships": 0, "agents": ["Viper", "Omen", "Brimstone"]},
    {"name": "Starry",   "team": "FunPlus Phoenix", "region": "China",   "age": 24, "championships": 0, "agents": ["Killjoy", "Sova", "Cypher"]},
    {"name": "BerLIN",   "team": "FunPlus Phoenix", "region": "China",   "age": 25, "championships": 0, "agents": ["Sage", "Skye", "Killjoy"]},
    # Trace Esports
    {"name": "FengFeng", "team": "Trace Esports",   "region": "China",   "age": 24, "championships": 0, "agents": ["Jett", "Raze", "Neon"]},
    {"name": "Bianca",   "team": "Trace Esports",   "region": "China",   "age": 23, "championships": 0, "agents": ["Omen", "Viper", "Astra"]},
    {"name": "Yosemite", "team": "Trace Esports",   "region": "China",   "age": 23, "championships": 0, "agents": ["Sova", "KAY/O", "Fade"]},
    {"name": "MrCANI",   "team": "Trace Esports",   "region": "China",   "age": 22, "championships": 0, "agents": ["Killjoy", "Sage", "Cypher"]},
    {"name": "hfmi0",    "team": "Trace Esports",   "region": "China",   "age": 23, "championships": 0, "agents": ["Raze", "Reyna", "Phoenix"]},
    # Bilibili Gaming
    {"name": "whzy",     "team": "Bilibili Gaming", "region": "China",   "age": 24, "championships": 0, "agents": ["Raze", "Jett", "Neon"]},
    {"name": "knight",   "team": "Bilibili Gaming", "region": "China",   "age": 23, "championships": 0, "agents": ["Omen", "Viper", "Astra"]},
    {"name": "YHchen",   "team": "Bilibili Gaming", "region": "China",   "age": 22, "championships": 0, "agents": ["Sova", "Fade", "KAY/O"]},
    {"name": "rin",      "team": "Bilibili Gaming", "region": "China",   "age": 23, "championships": 0, "agents": ["Killjoy", "Sage", "Cypher"]},
    {"name": "SScary",   "team": "Bilibili Gaming", "region": "China",   "age": 23, "championships": 0, "agents": ["Raze", "Chamber", "Jett"]},
    # Dragon Ranger Gaming
    {"name": "Spiritz",  "team": "Dragon Ranger Gaming", "region": "China", "age": 24, "championships": 0, "agents": ["Jett", "Raze", "Neon"]},
    {"name": "vo0kashu", "team": "Dragon Ranger Gaming", "region": "China", "age": 25, "championships": 0, "agents": ["Omen", "Astra", "Viper"]},
    {"name": "MarT1n",   "team": "Dragon Ranger Gaming", "region": "China", "age": 22, "championships": 0, "agents": ["Killjoy", "Cypher", "Sage"]},
    {"name": "Nvlgog",   "team": "Dragon Ranger Gaming", "region": "China", "age": 23, "championships": 0, "agents": ["Sova", "Fade", "Skye"]},
    {"name": "Tvirus",   "team": "Dragon Ranger Gaming", "region": "China", "age": 24, "championships": 0, "agents": ["Raze", "Jett", "Chamber"]},
    # Wolves
    {"name": "Pleets",   "team": "Wolves Esports",  "region": "China",   "age": 23, "championships": 0, "agents": ["Jett", "Raze", "Neon"]},
    {"name": "Juicy",    "team": "Wolves Esports",  "region": "China",   "age": 24, "championships": 0, "agents": ["Sova", "KAY/O", "Fade"]},
    {"name": "Lf",       "team": "Wolves Esports",  "region": "China",   "age": 23, "championships": 0, "agents": ["Omen", "Viper", "Astra"]},
    {"name": "Stary",    "team": "Wolves Esports",  "region": "China",   "age": 22, "championships": 0, "agents": ["Killjoy", "Cypher", "Sage"]},
    {"name": "Sinner",   "team": "Wolves Esports",  "region": "China",   "age": 23, "championships": 0, "agents": ["Raze", "Jett", "Chamber"]},

    # === Americas ===
    # Sentinels (Masters Madrid 2024, Reykjavík 2021)
    {"name": "TenZ",     "team": "Sentinels",       "region": "Americas", "age": 24, "championships": 2, "agents": ["Jett", "Raze", "Chamber"]},
    {"name": "zekken",   "team": "Sentinels",       "region": "Americas", "age": 20, "championships": 1, "agents": ["Raze", "Neon", "Jett"]},
    {"name": "johnqt",   "team": "Sentinels",       "region": "Americas", "age": 23, "championships": 1, "agents": ["Killjoy", "Sova", "Cypher"]},
    {"name": "Sacy",     "team": "Sentinels",       "region": "Americas", "age": 30, "championships": 1, "agents": ["Sova", "KAY/O", "Skye"]},
    {"name": "Zellsis",  "team": "Sentinels",       "region": "Americas", "age": 27, "championships": 1, "agents": ["Omen", "Viper", "Raze"]},
    {"name": "dapr",     "team": "Sentinels",       "region": "Americas", "age": 28, "championships": 1, "agents": ["Cypher", "Killjoy", "Sova"]},
    # NRG (Champions 2025 winners)
    {"name": "Ethan",    "team": "NRG Esports",     "region": "Americas", "age": 26, "championships": 2, "agents": ["KAY/O", "Skye", "Sova"]},
    {"name": "s0m",      "team": "NRG Esports",     "region": "Americas", "age": 23, "championships": 1, "agents": ["Jett", "Raze", "Neon"]},
    {"name": "mada",     "team": "NRG Esports",     "region": "Americas", "age": 22, "championships": 1, "agents": ["Omen", "Viper", "Astra"]},
    {"name": "brawk",    "team": "NRG Esports",     "region": "Americas", "age": 24, "championships": 1, "agents": ["Killjoy", "Sova", "Cypher"]},
    {"name": "skuba",    "team": "NRG Esports",     "region": "Americas", "age": 23, "championships": 1, "agents": ["Raze", "Jett", "Chamber"]},
    {"name": "jawgemo",  "team": "NRG Esports",     "region": "Americas", "age": 27, "championships": 1, "agents": ["Raze", "Jett", "Neon"]},
    {"name": "Boostio",  "team": "NRG Esports",     "region": "Americas", "age": 27, "championships": 1, "agents": ["Killjoy", "Sova", "Cypher"]},
    {"name": "C0M",      "team": "NRG Esports",     "region": "Americas", "age": 24, "championships": 1, "agents": ["Sova", "Fade", "KAY/O"]},
    {"name": "Demon1",   "team": "NRG Esports",     "region": "Americas", "age": 22, "championships": 1, "agents": ["Jett", "Raze", "Chamber"]},
    # LOUD (Champions 2022 winners)
    {"name": "aspas",    "team": "LOUD",            "region": "Americas", "age": 22, "championships": 1, "agents": ["Jett", "Raze", "Neon"]},
    {"name": "Less",     "team": "LOUD",            "region": "Americas", "age": 22, "championships": 1, "agents": ["Killjoy", "Cypher", "Chamber"]},
    {"name": "Saadhak",  "team": "LOUD",            "region": "Americas", "age": 27, "championships": 1, "agents": ["Sova", "Fade", "KAY/O"]},
    {"name": "cauanzin", "team": "LOUD",            "region": "Americas", "age": 22, "championships": 0, "agents": ["Raze", "Jett", "Neon"]},
    {"name": "tuyz",     "team": "LOUD",            "region": "Americas", "age": 23, "championships": 0, "agents": ["Omen", "Viper", "Astra"]},
    {"name": "pANcada",  "team": "LOUD",            "region": "Americas", "age": 26, "championships": 1, "agents": ["Viper", "Omen", "Astra"]},
    # Leviatán
    {"name": "Mazino",   "team": "Leviatán",        "region": "Americas", "age": 22, "championships": 0, "agents": ["Raze", "Jett", "Reyna"]},
    {"name": "kiNgg",    "team": "Leviatán",        "region": "Americas", "age": 24, "championships": 0, "agents": ["Omen", "Viper", "Astra"]},
    {"name": "Melser",   "team": "Leviatán",        "region": "Americas", "age": 25, "championships": 0, "agents": ["Sova", "Fade", "KAY/O"]},
    {"name": "Tacolilla","team": "Leviatán",        "region": "Americas", "age": 23, "championships": 0, "agents": ["Killjoy", "Cypher", "Chamber"]},
    # Cloud9
    {"name": "OXY",      "team": "Cloud9",          "region": "Americas", "age": 21, "championships": 0, "agents": ["Jett", "Raze", "Neon"]},
    {"name": "ShoT_UP",  "team": "Cloud9",          "region": "Americas", "age": 22, "championships": 0, "agents": ["Killjoy", "Sova", "Cypher"]},
    {"name": "N4RRATE",  "team": "Cloud9",          "region": "Americas", "age": 25, "championships": 0, "agents": ["Omen", "Viper", "Astra"]},
    {"name": "verno",    "team": "Cloud9",          "region": "Americas", "age": 24, "championships": 0, "agents": ["Raze", "Jett", "Neon"]},
    {"name": "yay",      "team": "Cloud9",          "region": "Americas", "age": 26, "championships": 0, "agents": ["Chamber", "Jett", "Raze"]},
    # G2 Esports
    {"name": "trent",    "team": "G2 Esports",      "region": "Americas", "age": 22, "championships": 0, "agents": ["Sova", "Fade", "Skye"]},
    {"name": "valyn",    "team": "G2 Esports",      "region": "Americas", "age": 22, "championships": 0, "agents": ["Omen", "Brimstone", "Viper"]},
    {"name": "JonahP",   "team": "G2 Esports",      "region": "Americas", "age": 24, "championships": 0, "agents": ["Breach", "KAY/O", "Skye"]},
    {"name": "icek",     "team": "G2 Esports",      "region": "Americas", "age": 23, "championships": 0, "agents": ["Killjoy", "Cypher", "Sage"]},
    # MIBR
    {"name": "frz",      "team": "MIBR",            "region": "Americas", "age": 25, "championships": 0, "agents": ["Jett", "Raze", "Neon"]},
    {"name": "mazin",    "team": "MIBR",            "region": "Americas", "age": 24, "championships": 0, "agents": ["Omen", "Viper", "Astra"]},
    {"name": "Art",      "team": "MIBR",            "region": "Americas", "age": 23, "championships": 0, "agents": ["Sova", "Fade", "KAY/O"]},
    {"name": "nox",      "team": "MIBR",            "region": "Americas", "age": 23, "championships": 0, "agents": ["Killjoy", "Cypher", "Sage"]},
    # 100 Thieves
    {"name": "Asuna",    "team": "100 Thieves",     "region": "Americas", "age": 25, "championships": 0, "agents": ["Jett", "Raze", "Reyna"]},
    {"name": "Bang",     "team": "100 Thieves",     "region": "Americas", "age": 24, "championships": 0, "agents": ["Sova", "KAY/O", "Fade"]},
    {"name": "Cryocells","team": "100 Thieves",     "region": "Americas", "age": 25, "championships": 0, "agents": ["Raze", "Jett", "Neon"]},
    {"name": "stellar",  "team": "100 Thieves",     "region": "Americas", "age": 28, "championships": 0, "agents": ["Omen", "Viper", "Breach"]},
    {"name": "Derrek",   "team": "100 Thieves",     "region": "Americas", "age": 26, "championships": 0, "agents": ["Killjoy", "Cypher", "Sage"]},

    # === EMEA ===
    # Fnatic (Masters Tokyo 2023, LOCK//IN 2023)
    {"name": "Boaster",  "team": "Fnatic",          "region": "EMEA",     "age": 31, "championships": 2, "agents": ["Sova", "Fade", "KAY/O"]},
    {"name": "Derke",    "team": "Fnatic",          "region": "EMEA",     "age": 24, "championships": 2, "agents": ["Jett", "Raze", "Neon"]},
    {"name": "Alfajer",  "team": "Fnatic",          "region": "EMEA",     "age": 20, "championships": 2, "agents": ["Killjoy", "Cypher", "Chamber"]},
    {"name": "Leo",      "team": "Fnatic",          "region": "EMEA",     "age": 22, "championships": 2, "agents": ["Omen", "Viper", "Astra"]},
    {"name": "Chronicle","team": "Fnatic",          "region": "EMEA",     "age": 26, "championships": 2, "agents": ["Raze", "KAY/O", "Skye"]},
    # NAVI
    {"name": "ANGE1",    "team": "NAVI",            "region": "EMEA",     "age": 38, "championships": 0, "agents": ["Omen", "Astra", "Viper"]},
    {"name": "Shao",     "team": "NAVI",            "region": "EMEA",     "age": 26, "championships": 0, "agents": ["Sova", "Fade", "KAY/O"]},
    {"name": "Zyppan",   "team": "NAVI",            "region": "EMEA",     "age": 24, "championships": 0, "agents": ["Jett", "Raze", "Neon"]},
    {"name": "SUYGETSU", "team": "NAVI",            "region": "EMEA",     "age": 26, "championships": 0, "agents": ["Killjoy", "Cypher", "Chamber"]},
    {"name": "ardiis",   "team": "NAVI",            "region": "EMEA",     "age": 27, "championships": 0, "agents": ["Jett", "Chamber", "Raze"]},
    {"name": "Dps",      "team": "NAVI",            "region": "EMEA",     "age": 23, "championships": 0, "agents": ["Killjoy", "Sage", "Cypher"]},
    # Team Vitality
    {"name": "Sayf",     "team": "Team Vitality",   "region": "EMEA",     "age": 27, "championships": 0, "agents": ["Jett", "Raze", "Neon"]},
    {"name": "Destrian", "team": "Team Vitality",   "region": "EMEA",     "age": 22, "championships": 0, "agents": ["Killjoy", "Cypher", "Sage"]},
    {"name": "trexx",    "team": "Team Vitality",   "region": "EMEA",     "age": 22, "championships": 0, "agents": ["Sova", "Fade", "KAY/O"]},
    {"name": "Kicks",    "team": "Team Vitality",   "region": "EMEA",     "age": 23, "championships": 0, "agents": ["Omen", "Viper", "Astra"]},
    # Karmine Corp
    {"name": "ScreaM",   "team": "Karmine Corp",    "region": "EMEA",     "age": 30, "championships": 0, "agents": ["Jett", "Raze", "Reyna"]},
    {"name": "Enzo",     "team": "Karmine Corp",    "region": "EMEA",     "age": 27, "championships": 0, "agents": ["Sova", "Fade", "KAY/O"]},
    {"name": "xms",      "team": "Karmine Corp",    "region": "EMEA",     "age": 28, "championships": 0, "agents": ["Killjoy", "Cypher", "Sage"]},
    {"name": "tomaszy",  "team": "Karmine Corp",    "region": "EMEA",     "age": 22, "championships": 0, "agents": ["Jett", "Raze", "Neon"]},
    {"name": "marteen",  "team": "Karmine Corp",    "region": "EMEA",     "age": 23, "championships": 0, "agents": ["Omen", "Viper", "Astra"]},
    # FUT Esports
    {"name": "cNed",     "team": "FUT Esports",     "region": "EMEA",     "age": 25, "championships": 1, "agents": ["Jett", "Raze", "Chamber"]},
    {"name": "qRaxs",    "team": "FUT Esports",     "region": "EMEA",     "age": 24, "championships": 0, "agents": ["Sova", "Fade", "KAY/O"]},
    {"name": "Mojj",     "team": "FUT Esports",     "region": "EMEA",     "age": 24, "championships": 0, "agents": ["Omen", "Viper", "Astra"]},
    {"name": "Fizzy",    "team": "FUT Esports",     "region": "EMEA",     "age": 23, "championships": 0, "agents": ["Raze", "Jett", "Neon"]},
    {"name": "yetujay",  "team": "FUT Esports",     "region": "EMEA",     "age": 22, "championships": 0, "agents": ["Killjoy", "Cypher", "Sage"]},
    # Gentle Mates
    {"name": "nAts",     "team": "Gentle Mates",    "region": "EMEA",     "age": 27, "championships": 1, "agents": ["Viper", "Sova", "Cypher"]},
    {"name": "d3ffo",    "team": "Gentle Mates",    "region": "EMEA",     "age": 25, "championships": 1, "agents": ["Raze", "Jett", "Neon"]},
    {"name": "Redgar",   "team": "Gentle Mates",    "region": "EMEA",     "age": 29, "championships": 0, "agents": ["Killjoy", "Sova", "Cypher"]},
    {"name": "BONECOLD", "team": "Gentle Mates",    "region": "EMEA",     "age": 28, "championships": 1, "agents": ["Omen", "Viper", "Astra"]},
    # Team Liquid

    {"name": "Jamppi",   "team": "Team Liquid",     "region": "EMEA",     "age": 25, "championships": 0, "agents": ["Jett", "Raze", "Neon"]},
    {"name": "Keiko",    "team": "Team Liquid",     "region": "EMEA",     "age": 24, "championships": 0, "agents": ["Sova", "Fade", "KAY/O"]},
    {"name": "Mistic",   "team": "Team Liquid",     "region": "EMEA",     "age": 26, "championships": 0, "agents": ["Omen", "Viper", "Astra"]},
    {"name": "Kryptix",  "team": "Team Liquid",     "region": "EMEA",     "age": 27, "championships": 0, "agents": ["Raze", "Jett", "Reyna"]},
    # Giants
    {"name": "fit1nho",  "team": "Giants",          "region": "EMEA",     "age": 25, "championships": 0, "agents": ["Jett", "Raze", "Neon"]},
    {"name": "rhyme",    "team": "Giants",          "region": "EMEA",     "age": 27, "championships": 0, "agents": ["Sova", "KAY/O", "Fade"]},
    {"name": "paz",      "team": "Giants",          "region": "EMEA",     "age": 24, "championships": 0, "agents": ["Omen", "Viper", "Astra"]},
    {"name": "hitori",   "team": "Giants",          "region": "EMEA",     "age": 26, "championships": 0, "agents": ["Killjoy", "Cypher", "Sage"]},
    {"name": "nukkye",   "team": "Giants",          "region": "EMEA",     "age": 28, "championships": 0, "agents": ["Raze", "Jett", "Reyna"]},
    # KOI
    {"name": "Sheydos",  "team": "KOI",             "region": "EMEA",     "age": 27, "championships": 0, "agents": ["Omen", "Viper", "Astra"]},
    {"name": "kamo",     "team": "KOI",             "region": "EMEA",     "age": 25, "championships": 0, "agents": ["Raze", "Jett", "Neon"]},
    {"name": "starxo",   "team": "KOI",             "region": "EMEA",     "age": 27, "championships": 0, "agents": ["Sova", "KAY/O", "Fade"]},
    {"name": "zeek",     "team": "KOI",             "region": "EMEA",     "age": 26, "championships": 1, "agents": ["Raze", "Jett", "Chamber"]},

    # === Pacific ===
    # Paper Rex
    {"name": "f0rsakeN", "team": "Paper Rex",       "region": "Pacific",  "age": 24, "championships": 0, "agents": ["Sova", "Fade", "KAY/O"]},
    {"name": "Jinggg",   "team": "Paper Rex",       "region": "Pacific",  "age": 22, "championships": 0, "agents": ["Raze", "Neon", "Jett"]},
    {"name": "something","team": "Paper Rex",       "region": "Pacific",  "age": 23, "championships": 0, "agents": ["Jett", "Raze", "Neon"]},
    {"name": "d4v41",    "team": "Paper Rex",       "region": "Pacific",  "age": 24, "championships": 0, "agents": ["Killjoy", "Cypher", "Chamber"]},
    {"name": "mindfreak","team": "Paper Rex",       "region": "Pacific",  "age": 25, "championships": 0, "agents": ["Omen", "Viper", "Astra"]},
    {"name": "Benkai",   "team": "Paper Rex",       "region": "Pacific",  "age": 28, "championships": 0, "agents": ["Sova", "KAY/O", "Fade"]},
    {"name": "PatMen",   "team": "Paper Rex",       "region": "Pacific",  "age": 22, "championships": 0, "agents": ["Raze", "Jett", "Neon"]},
    # DRX
    {"name": "MaKo",     "team": "DRX",             "region": "Pacific",  "age": 27, "championships": 0, "agents": ["Omen", "Viper", "Astra"]},
    {"name": "Flashback","team": "DRX",             "region": "Pacific",  "age": 26, "championships": 0, "agents": ["Killjoy", "Cypher", "Chamber"]},
    {"name": "RB",       "team": "DRX",             "region": "Pacific",  "age": 24, "championships": 0, "agents": ["Raze", "Neon", "Jett"]},
    {"name": "BeYN",     "team": "DRX",             "region": "Pacific",  "age": 24, "championships": 0, "agents": ["Sova", "Fade", "KAY/O"]},
    {"name": "Foxy9",    "team": "DRX",             "region": "Pacific",  "age": 23, "championships": 0, "agents": ["Raze", "Jett", "Reyna"]},

    # Gen.G (Masters Shanghai 2024 winners)
    {"name": "Meteor",   "team": "Gen.G",           "region": "Pacific",  "age": 25, "championships": 1, "agents": ["Omen", "Viper", "Astra"]},
    {"name": "t3xture",  "team": "Gen.G",           "region": "Pacific",  "age": 24, "championships": 1, "agents": ["Jett", "Raze", "Neon"]},
    {"name": "Munchkin", "team": "Gen.G",           "region": "Pacific",  "age": 26, "championships": 1, "agents": ["Sova", "Fade", "KAY/O"]},
    {"name": "Karon",    "team": "Gen.G",           "region": "Pacific",  "age": 21, "championships": 1, "agents": ["Chamber", "Killjoy", "Cypher"]},
    {"name": "yomani",   "team": "Gen.G",           "region": "Pacific",  "age": 22, "championships": 0, "agents": ["Raze", "Jett", "Neon"]},
    # T1 (Masters Bangkok 2025 winners)
    {"name": "BuZz",     "team": "T1",              "region": "Pacific",  "age": 22, "championships": 1, "agents": ["Jett", "Raze", "Neon"]},
    {"name": "stax",     "team": "T1",              "region": "Pacific",  "age": 25, "championships": 0, "agents": ["Sova", "Fade", "KAY/O"]},
    {"name": "carpe",    "team": "T1",              "region": "Pacific",  "age": 27, "championships": 0, "agents": ["Jett", "Raze", "Chamber"]},

    {"name": "iZu",      "team": "T1",              "region": "Pacific",  "age": 23, "championships": 0, "agents": ["Raze", "Neon", "Jett"]},
    {"name": "xccurate", "team": "T1",              "region": "Pacific",  "age": 27, "championships": 0, "agents": ["Killjoy", "Cypher", "Sage"]},
    # ZETA DIVISION
    {"name": "Laz",      "team": "ZETA DIVISION",   "region": "Pacific",  "age": 25, "championships": 0, "agents": ["Jett", "Raze", "Neon"]},
    {"name": "Dep",      "team": "ZETA DIVISION",   "region": "Pacific",  "age": 24, "championships": 0, "agents": ["Omen", "Astra", "Viper"]},
    {"name": "barce",    "team": "ZETA DIVISION",   "region": "Pacific",  "age": 25, "championships": 0, "agents": ["Sova", "Fade", "KAY/O"]},

    {"name": "XQQ",      "team": "ZETA DIVISION",   "region": "Pacific",  "age": 24, "championships": 0, "agents": ["Killjoy", "Cypher", "Sage"]},
    # Nongshim RedForce
    {"name": "Ban",      "team": "Nongshim RedForce","region": "Pacific",  "age": 26, "championships": 0, "agents": ["Jett", "Raze", "Neon"]},
    {"name": "Sylvan",   "team": "Nongshim RedForce","region": "Pacific",  "age": 23, "championships": 0, "agents": ["Omen", "Astra", "Viper"]},
    {"name": "Lakia",    "team": "Nongshim RedForce","region": "Pacific",  "age": 29, "championships": 0, "agents": ["Killjoy", "Cypher", "Sage"]},
    {"name": "Ezra",     "team": "Nongshim RedForce","region": "Pacific",  "age": 22, "championships": 0, "agents": ["Raze", "Jett", "Neon"]},
    {"name": "Sylval",   "team": "Nongshim RedForce","region": "Pacific",  "age": 23, "championships": 0, "agents": ["Sova", "Fade", "KAY/O"]},
    # Rex Regum Qeon
    {"name": "Lmemore",  "team": "Rex Regum Qeon",  "region": "Pacific",  "age": 24, "championships": 0, "agents": ["Jett", "Raze", "Neon"]},
    {"name": "Estrella", "team": "Rex Regum Qeon",  "region": "Pacific",  "age": 23, "championships": 0, "agents": ["Omen", "Viper", "Astra"]},
    {"name": "fl1pzjder","team": "Rex Regum Qeon",  "region": "Pacific",  "age": 22, "championships": 0, "agents": ["Sova", "KAY/O", "Fade"]},
    {"name": "Lamonster","team": "Rex Regum Qeon",  "region": "Pacific",  "age": 26, "championships": 0, "agents": ["Killjoy", "Cypher", "Sage"]},
    {"name": "Nexi",     "team": "Rex Regum Qeon",  "region": "Pacific",  "age": 23, "championships": 0, "agents": ["Raze", "Jett", "Chamber"]},
    # Global Esports
    {"name": "Suppr",    "team": "Global Esports",  "region": "Pacific",  "age": 24, "championships": 0, "agents": ["Jett", "Raze", "Neon"]},
    {"name": "Bazzi",    "team": "Global Esports",  "region": "Pacific",  "age": 26, "championships": 0, "agents": ["Omen", "Viper", "Astra"]},
    {"name": "Lightningfast","team":"Global Esports","region": "Pacific", "age": 25, "championships": 0, "agents": ["Sova", "Fade", "KAY/O"]},
    {"name": "WRONSKI",  "team": "Global Esports",  "region": "Pacific",  "age": 23, "championships": 0, "agents": ["Killjoy", "Cypher", "Sage"]},
    {"name": "Polvi",    "team": "Global Esports",  "region": "Pacific",  "age": 24, "championships": 0, "agents": ["Raze", "Jett", "Neon"]},
]

# Agent Chinese translations
AGENT_TRANSLATIONS = {
    "Jett": "捷风", "Raze": "雷兹", "Phoenix": "凤凰", "Reyna": "蕾娜",
    "Yoru": "夜露", "Neon": "霓虹", "Chamber": "尚勃勒", "Sage": "贤者",
    "Skye": "斯凯", "Killjoy": "奇乐", "Cypher": "零", "Viper": "蝰蛇",
    "Omen": "幽影", "Brimstone": "炼狱", "Astra": "星礈", "Harbor": "海神",
    "Clove": "克莉", "Sova": "索瓦", "Breach": "铁壁", "KAY/O": "KAY/O",
    "Fade": "黑梦", "Gekko": "盖可", "Vyse": "维斯", "Deadlock": "死锁",
    "Iso": "壹决", "Tejo": "钛狐",
}

# Team Chinese translations
TEAM_TRANSLATIONS = {
    "EDward Gaming": "EDG", "FunPlus Phoenix": "FPX", "Trace Esports": "TE",
    "Bilibili Gaming": "BLG", "Dragon Ranger Gaming": "DRG",
    "Wolves Esports": "Wolves", "Nova Esports": "NOVA",
    "Sentinels": "Sentinels", "NRG Esports": "NRG", "LOUD": "LOUD",
    "Leviatán": "LEV", "G2 Esports": "G2", "Cloud9": "C9",
    "100 Thieves": "100T", "MIBR": "MIBR", "FURIA": "FURIA",
    "Paper Rex": "PRX", "DRX": "DRX", "Gen.G": "Gen.G", "T1": "T1",
    "ZETA DIVISION": "ZETA", "Rex Regum Qeon": "RRQ",
    "Global Esports": "GE", "Nongshim RedForce": "NS",
    "Fnatic": "Fnatic", "NAVI": "NAVI", "Team Vitality": "VIT",
    "Karmine Corp": "KC", "FUT Esports": "FUT", "Team Liquid": "TL",
    "Gentle Mates": "M8", "Giants": "Giants", "KOI": "KOI",
}

# Region Chinese translations
REGION_TRANSLATIONS = {
    "Americas": "美洲", "EMEA": "EMEA", "Pacific": "太平洋", "China": "中国",
}


def deduplicate(players):
    """Remove duplicates, keeping the entry with more complete data."""
    seen = {}
    for p in players:
        key = p["name"]
        if key not in seen:
            seen[key] = p
        else:
            # Keep entry with more agents or higher championship count
            existing = seen[key]
            if len(p.get("agents", [])) > len(existing.get("agents", [])):
                seen[key] = p
            elif p.get("championships", 0) > existing.get("championships", 0):
                seen[key] = p
    return list(seen.values())


def export_csv(players, output_path):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    fieldnames = ["name", "team", "region", "age", "championships", "agent1", "agent2", "agent3"]
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for p in players:
            agents = p.get("agents", [])
            w.writerow({
                "name": p["name"],
                "team": p.get("team", ""),
                "region": p.get("region", ""),
                "age": p.get("age", ""),
                "championships": p.get("championships", 0),
                "agent1": agents[0] if len(agents) > 0 else "",
                "agent2": agents[1] if len(agents) > 1 else "",
                "agent3": agents[2] if len(agents) > 2 else "",
            })
    print(f"CSV exported: {output_path} ({len(players)} players)")


def export_json(players, output_path):
    """Export to the format the frontend needs."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    formatted = []
    for p in players:
        agents = p.get("agents", [])
        agents_cn = [AGENT_TRANSLATIONS.get(a, a) for a in agents[:3]]
        team_cn = TEAM_TRANSLATIONS.get(p.get("team", ""), p.get("team", ""))
        region_cn = REGION_TRANSLATIONS.get(p.get("region", ""), p.get("region", ""))
        formatted.append({
            "name": p["name"],
            "team": p.get("team", ""),
            "team_cn": team_cn,
            "region": p.get("region", ""),
            "region_cn": region_cn,
            "age": p.get("age", ""),
            "championships": p.get("championships", 0),
            "agents": agents[:3],
            "agents_cn": agents_cn,
        })
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(formatted, f, ensure_ascii=False, indent=2)
    print(f"JSON exported: {output_path} ({len(formatted)} players)")


def print_summary(players):
    unique = deduplicate(players)
    print(f"\n{'='*50}")
    print(f"Valorant Pro Player Dataset - Summary")
    print(f"{'='*50}")
    print(f"Total unique players: {len(unique)}")

    regions = {}
    for p in unique:
        r = p.get("region", "Unknown")
        regions[r] = regions.get(r, 0) + 1
    print(f"By region:")
    for r, c in sorted(regions.items(), key=lambda x: -x[1]):
        print(f"  {r}: {c} players")

    champs = [p for p in unique if p.get("championships", 0) > 0]
    print(f"Players with VCT championships: {len(champs)}")

    teams = {}
    for p in unique:
        t = p.get("team", "Unknown")
        teams[t] = teams.get(t, 0) + 1
    print(f"Teams represented: {len(teams)}")


def main():
    script_dir = os.path.dirname(__file__)
    output_dir = os.path.join(script_dir, "..", "processed")
    csv_path = os.path.join(output_dir, "players.csv")
    json_path = os.path.join(output_dir, "players.json")

    players = deduplicate(PLAYERS)
    export_csv(players, csv_path)
    export_json(players, json_path)
    print_summary(players)
    print(f"\n✅ Dataset ready! Copy {json_path} to src/data/ for the frontend.")


if __name__ == "__main__":
    main()
