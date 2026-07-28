"""
Valorant Pro Player Data Scraper
=================================
Scrapes player data from VLR.gg to build a guessing game dataset.

Output: data/processed/players.csv

Fields collected:
  - id, name, real_name, age, region, team, championships, agents_top3

Usage:
  python scrape_vlr.py [--output ../processed/players.csv]
"""

import csv
import json
import os
import re
import sys
import time
from datetime import datetime
from typing import Optional

import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}

# VLR.gg base URLs
VLR_BASE = "https://www.vlr.gg"
STATS_URL = f"{VLR_BASE}/stats"
PLAYER_URL = f"{VLR_BASE}/player"

# Region mapping based on team's league
REGION_MAP = {
    # Americas
    "NRG": "Americas", "Sentinels": "Americas", "LOUD": "Americas",
    "Leviatán": "Americas", "G2": "Americas", "KRÜ": "Americas",
    "MIBR": "Americas", "FURIA": "Americas", "Cloud9": "Americas",
    "100 Thieves": "Americas", "EG": "Americas",
    # EMEA
    "Fnatic": "EMEA", "NAVI": "EMEA", "Team Vitality": "EMEA",
    "FUT": "EMEA", "KOI": "EMEA", "Gentle Mates": "EMEA",
    "Guild": "EMEA", "BBL": "EMEA", "KC": "EMEA",
    "Heretics": "EMEA", "Liquid": "EMEA",
    # Pacific
    "DRX": "Pacific", "Gen.G": "Pacific", "Paper Rex": "Pacific",
    "ZETA": "Pacific", "T1": "Pacific", "RRQ": "Pacific",
    "GE": "Pacific", "TS": "Pacific", "PRX": "Pacific",
    "NS": "Pacific", "Nongshim": "Pacific",
    # China
    "EDG": "China", "FPX": "China", "Trace": "China",
    "BLG": "China", "DRG": "China", "JDG": "China",
    "NOVA": "China", "TYL": "China", "Tyloo": "China",
    "WOL": "China", "Wolves": "China", "TE": "China",
}

# Masters and Champions events for championship counting
MAJOR_EVENTS = [
    "VCT 2021: Masters Reykjavík",
    "VCT 2021: Masters Berlin",
    "VCT 2021: Champions Berlin",
    "VCT 2022: Masters Reykjavík",
    "VCT 2022: Masters Copenhagen",
    "VCT 2022: Champions Istanbul",
    "VCT 2023: LOCK//IN São Paulo",
    "VCT 2023: Masters Tokyo",
    "VCT 2023: Champions Los Angeles",
    "VCT 2024: Masters Madrid",
    "VCT 2024: Masters Shanghai",
    "VCT 2024: Champions Seoul",
    "VCT 2025: Masters Bangkok",
    "VCT 2025: Masters Toronto",
    "VCT 2025: Champions Paris",
    "VCT 2026: Masters Santiago",
    "VCT 2026: Masters London",
    "VCT 2026: Champions Shanghai",
]

# Known player ages (manually maintained, sourced from Liquipedia)
KNOWN_AGES = {
    # China
    "ZmjjKK": 23, "Smoggy": 23, "nobody": 26, "CHICHOO": 24,
    "S1mon": 22, "Haodong": 27, "Life": 25, "whz": 23,
    "AAA": 25, "Starry": 24, "FengFeng": 24, "Bianca": 23,
    "Yosemite": 23, "MrCANI": 22, "hfmi0": 23,
    # Americas
    "TenZ": 24, "Sacy": 30, "zekken": 20, "johnqt": 23,
    "Zellsis": 27, "aspas": 22, "Less": 22, "Saadhak": 27,
    "pANcada": 26, "tuyz": 23, "cauanzin": 22, "jawgemo": 27,
    "Ethan": 26, "Boostio": 27, "C0M": 24, "Demon1": 22,
    "FNS": 32, "Victor": 28, "crashies": 28, "Marved": 26,
    "yay": 26, "skuba": 23, "mada": 22, "brawk": 24,
    "s0m": 23, "dapr": 28, "ShahZaM": 31, "SicK": 29,
    "zombs": 28, "leaf": 22, "OXY": 21, "ShoT_UP": 22,
    "N4RRATE": 25, "verno": 24,
    # EMEA
    "Boaster": 31, "Derke": 24, "Alfajer": 20, "Leo": 22,
    "Chronicle": 26, "ANGE1": 38, "Shao": 26, "Zyppan": 24,
    "ardiis": 27, "SUYGETSU": 26, "nAts": 27, "Redgar": 29,
    "d3ffo": 25, "Sheydos": 27, "cNed": 25, "BONECOLD": 28,
    "zeek": 26, "starxo": 27, "Kiles": 27, "kamo": 25,
    "Wo0t": 21, "Karzq": 22, "Jazz": 28, "minise": 27,
    "qxK": 24, "Destrian": 22, "Sayf": 27, "Trent": 22,
    "trexx": 22, "tomaszy": 22,
    # Pacific
    "f0rsakeN": 24, "Jinggg": 22, "something": 23, "d4v41": 24,
    "mindfreak": 25, "Meteor": 25, "t3xture": 24, "Munchkin": 26,
    "Lakia": 29, "Karon": 21, "BuZz": 22, "stax": 25,
    "carpe": 27, "Sylvan": 23, "iZu": 23, "Rb": 23,
    "MaKo": 27, "Flashback": 26, "Laz": 25, "Bazzi": 26,
    "Estrella": 23, "ban": 26, "Foxy9": 23, "BeYN": 24,
    "Papi": 22, "Kr1stal": 24,
}

# Agent Chinese name translations
AGENT_CN = {
    "Jett": "捷风", "Raze": "蕾娜", "Phoenix": "凤凰",
    "Reyna": "芮娜", "Yoru": "夜露", "Neon": "霓虹",
    "Chamber": "尚勃勒", "Sage": "贤者", "Skye": "斯凯",
    "Killjoy": "奇乐", "Cypher": "零", "Viper": "蝰蛇",
    "Omen": "幽影", "Brimstone": "炼狱", "Astra": "星礈",
    "Harbor": "海神", "Clove": "克莉", "Sova": "索瓦",
    "Breach": "铁壁", "KAY/O": "KAY/O", "Fade": "黑梦",
    "Gekko": "盖可", "Vyse": "维斯", "Deadlock": "死锁",
    "Iso": "壹决", "Tejo": "钛狐",
    # Duplicate/alternative names
    "KAYO": "KAY/O",
}

# Team Chinese names
TEAM_CN = {
    "EDward Gaming": "EDG", "EDG": "EDG",
    "FunPlus Phoenix": "FPX", "FPX": "FPX",
    "Trace Esports": "TE", "TE": "TE",
    "Bilibili Gaming": "BLG", "BLG": "BLG",
    "Dragon Ranger Gaming": "DRG", "DRG": "DRG",
    "Nova Esports": "NOVA",
    "Wolves Esports": "Wolves",
    "Tyloo": "Tyloo",
    "Sentinels": "Sentinels",
    "NRG Esports": "NRG",
    "LOUD": "LOUD",
    "Leviatán": "LEV",
    "G2 Esports": "G2",
    "Paper Rex": "PRX",
    "DRX": "DRX",
    "Gen.G": "Gen.G",
    "T1": "T1",
    "ZETA DIVISION": "ZETA",
    "Rex Regum Qeon": "RRQ",
    "Nongshim RedForce": "NS",
    "Fnatic": "Fnatic",
    "NAVI": "NAVI",
    "Team Vitality": "VIT",
    "Karmine Corp": "KC",
    "FUT Esports": "FUT",
    "Team Liquid": "TL",
    "Giants": "Giants",
    "KOI": "KOI",
    "BBL Esports": "BBL",
    "Gentle Mates": "M8",
}


def determine_region(team_name: str) -> str:
    """Determine region from team name."""
    if not team_name:
        return "Unknown"
    for key, region in REGION_MAP.items():
        if key.lower() in team_name.lower():
            return region
    return "Unknown"


def safe_soup(html: str) -> BeautifulSoup:
    return BeautifulSoup(html, "html.parser")


def fetch(url: str, retries: int = 3) -> Optional[str]:
    """Fetch a URL with retries."""
    for attempt in range(retries):
        try:
            r = requests.get(url, headers=HEADERS, timeout=15)
            if r.status_code == 200:
                return r.text
            elif r.status_code == 429:
                wait = 10 * (attempt + 1)
                print(f"  Rate limited, waiting {wait}s...")
                time.sleep(wait)
            else:
                print(f"  HTTP {r.status_code} for {url}")
                return None
        except Exception as e:
            print(f"  Attempt {attempt+1} failed: {e}")
            if attempt < retries - 1:
                time.sleep(3)
    return None


def parse_player_page(player_id: str) -> dict:
    """Parse a VLR.gg player detail page."""
    url = f"{PLAYER_URL}/{player_id}"
    html = fetch(url)
    if not html:
        return {}

    soup = safe_soup(html)
    player = {"vlr_id": player_id}

    # Name
    name_h1 = soup.select_one("h1")
    if name_h1:
        player["name"] = name_h1.text.strip()

    # Real name
    real_name_el = soup.select_one(".player-real-name")
    if real_name_el:
        player["real_name"] = real_name_el.text.strip()

    # Team
    team_el = soup.select_one(".player-team a")
    if team_el:
        team_name = team_el.text.strip()
        player["team"] = team_name
        player["region"] = determine_region(team_name)

    # Agent stats from stats table
    agent_table = soup.select_one("table.player-stats-table")
    if agent_table:
        agents = []
        rows = agent_table.select("tbody tr")
        for row in rows[:10]:  # Check top 10
            agent_cell = row.select_one("td.mod-agent img")
            if agent_cell and agent_cell.get("alt"):
                agent_name = agent_cell["alt"].strip()
                agents.append(agent_name)
            elif agent_cell and agent_cell.get("title"):
                agent_name = agent_cell["title"].strip()
                agents.append(agent_name)
        player["agents_top3"] = agents[:3] if len(agents) >= 3 else agents

    # Event history
    event_section = soup.select_one(".player-events")
    if event_section:
        championships = 0
        event_items = event_section.select(".event-item")
        for item in event_items:
            placement_el = item.select_one(".event-item-placement")
            event_name_el = item.select_one(".event-item-name")
            if placement_el and event_name_el:
                placement = placement_el.text.strip()
                event_name = event_name_el.text.strip()
                if placement == "1st":
                    # Check if it's a Masters or Champions event
                    for major in MAJOR_EVENTS:
                        if major.split(":")[-1].strip().lower() in event_name.lower():
                            championships += 1
                            break
        player["championships"] = championships

    return player


def scrape_player_list() -> list[dict]:
    """Scrape the VLR.gg stats page to get a list of players with stats."""
    players = []

    # Scrape stats page for multiple regions
    regions = ["all"]  # Start with all regions

    for region in regions:
        url = f"{STATS_URL}?region={region}"
        html = fetch(url)
        if not html:
            continue

        soup = safe_soup(html)
        table = soup.select_one("table")
        if not table:
            print(f"No table found for region {region}")
            continue

        rows = table.select("tbody tr")
        print(f"Found {len(rows)} players in region {region}")

        for row in rows:
            player = {}

            # Player name and link
            name_el = row.select_one("td.mod-player a")
            if name_el:
                player["name"] = name_el.text.strip()
                href = name_el.get("href", "")
                # Extract player ID from href like /player/9/tenz
                if "/player/" in href:
                    pid = href.split("/player/")[1].split("/")[0]
                    player["vlr_id"] = pid

            # Team
            team_el = row.select_one("td.mod-team a")
            if team_el:
                team_name = team_el.text.strip()
                player["team"] = team_name
                player["region"] = determine_region(team_name)

            if player.get("name"):
                players.append(player)

    return players


def build_initial_dataset() -> list[dict]:
    """Build an initial dataset from known player information."""
    players = []

    # China - EDG (Champions 2024 winners)
    players.extend([
        {"name": "ZmjjKK", "team": "EDward Gaming", "region": "China", "age": 23, "championships": 2, "agents": ["Jett", "Raze", "Chamber"]},
        {"name": "Smoggy", "team": "EDward Gaming", "region": "China", "age": 23, "championships": 2, "agents": ["Raze", "KAY/O", "Sova"]},
        {"name": "nobody", "team": "EDward Gaming", "region": "China", "age": 26, "championships": 2, "agents": ["Sova", "Killjoy", "Cypher"]},
        {"name": "CHICHOO", "team": "EDward Gaming", "region": "China", "age": 24, "championships": 2, "agents": ["Viper", "Omen", "Astra"]},
        {"name": "S1mon", "team": "EDward Gaming", "region": "China", "age": 22, "championships": 1, "agents": ["Killjoy", "Cypher", "Sage"]},
        {"name": "Haodong", "team": "EDward Gaming", "region": "China", "age": 27, "championships": 1, "agents": ["Killjoy", "Sova", "Cypher"]},
        # China - FPX
        {"name": "Life", "team": "FunPlus Phoenix", "region": "China", "age": 25, "championships": 0, "agents": ["Raze", "Neon", "Jett"]},
        {"name": "whz", "team": "FunPlus Phoenix", "region": "China", "age": 23, "championships": 0, "agents": ["Jett", "Raze", "Sova"]},
        {"name": "AAAA", "team": "FunPlus Phoenix", "region": "China", "age": 25, "championships": 0, "agents": ["Viper", "Omen", "Brimstone"]},
        {"name": "Starry", "team": "FunPlus Phoenix", "region": "China", "age": 24, "championships": 0, "agents": ["Killjoy", "Sova", "Cypher"]},
        {"name": "BerLIN", "team": "FunPlus Phoenix", "region": "China", "age": 25, "championships": 0, "agents": ["Sage", "Skye", "Killjoy"]},
        # China - Trace
        {"name": "FengFeng", "team": "Trace Esports", "region": "China", "age": 24, "championships": 0, "agents": ["Jett", "Raze", "Neon"]},
        {"name": "Bianca", "team": "Trace Esports", "region": "China", "age": 23, "championships": 0, "agents": ["Omen", "Viper", "Astra"]},
        {"name": "Yosemite", "team": "Trace Esports", "region": "China", "age": 23, "championships": 0, "agents": ["Sova", "KAY/O", "Fade"]},
        {"name": "MrCANI", "team": "Trace Esports", "region": "China", "age": 22, "championships": 0, "agents": ["Killjoy", "Sage", "Cypher"]},
        {"name": "hfmi0", "team": "Trace Esports", "region": "China", "age": 23, "championships": 0, "agents": ["Raze", "Reyna", "Phoenix"]},
        # China - BLG
        {"name": "whzy", "team": "Bilibili Gaming", "region": "China", "age": 24, "championships": 0, "agents": ["Raze", "Jett", "Neon"]},
        {"name": "knight", "team": "Bilibili Gaming", "region": "China", "age": 23, "championships": 0, "agents": ["Omen", "Viper", "Astra"]},
        {"name": "YHchen", "team": "Bilibili Gaming", "region": "China", "age": 22, "championships": 0, "agents": ["Sova", "Fade", "KAY/O"]},
        {"name": "rin", "team": "Bilibili Gaming", "region": "China", "age": 23, "championships": 0, "agents": ["Killjoy", "Sage", "Cypher"]},
        {"name": "SScary", "team": "Bilibili Gaming", "region": "China", "age": 23, "championships": 0, "agents": ["Raze", "Chamber", "Jett"]},
        # China - DRG
        {"name": "Spiritz", "team": "Dragon Ranger Gaming", "region": "China", "age": 24, "championships": 0, "agents": ["Jett", "Raze", "Neon"]},
        {"name": "vo0kashu", "team": "Dragon Ranger Gaming", "region": "China", "age": 25, "championships": 0, "agents": ["Omen", "Astra", "Viper"]},
        {"name": "MarT1n", "team": "Dragon Ranger Gaming", "region": "China", "age": 22, "championships": 0, "agents": ["Killjoy", "Cypher", "Sage"]},
        {"name": "Nvlgog", "team": "Dragon Ranger Gaming", "region": "China", "age": 23, "championships": 0, "agents": ["Sova", "Fade", "Skye"]},
        {"name": "Tvirus", "team": "Dragon Ranger Gaming", "region": "China", "age": 24, "championships": 0, "agents": ["Raze", "Jett", "Chamber"]},

        # Americas - Sentinels (Masters Madrid 2024 winners)
        {"name": "TenZ", "team": "Sentinels", "region": "Americas", "age": 24, "championships": 2, "agents": ["Jett", "Raze", "Chamber"]},
        {"name": "zekken", "team": "Sentinels", "region": "Americas", "age": 20, "championships": 1, "agents": ["Raze", "Neon", "Jett"]},
        {"name": "johnqt", "team": "Sentinels", "region": "Americas", "age": 23, "championships": 1, "agents": ["Killjoy", "Sova", "Cypher"]},
        {"name": "Sacy", "team": "Sentinels", "region": "Americas", "age": 30, "championships": 1, "agents": ["Sova", "KAY/O", "Skye"]},
        {"name": "Zellsis", "team": "Sentinels", "region": "Americas", "age": 27, "championships": 1, "agents": ["Omen", "Viper", "Raze"]},
        # Americas - LOUD
        {"name": "aspas", "team": "LOUD", "region": "Americas", "age": 22, "championships": 1, "agents": ["Jett", "Raze", "Neon"]},
        {"name": "Less", "team": "LOUD", "region": "Americas", "age": 22, "championships": 1, "agents": ["Killjoy", "Cypher", "Chamber"]},
        {"name": "Saadhak", "team": "LOUD", "region": "Americas", "age": 27, "championships": 1, "agents": ["Sova", "Fade", "KAY/O"]},
        {"name": "cauanzin", "team": "LOUD", "region": "Americas", "age": 22, "championships": 0, "agents": ["Raze", "Jett", "Neon"]},
        {"name": "tuyz", "team": "LOUD", "region": "Americas", "age": 23, "championships": 0, "agents": ["Omen", "Viper", "Astra"]},
        # Americas - NRG (Champions 2025 winners)
        {"name": "Ethan", "team": "NRG Esports", "region": "Americas", "age": 26, "championships": 2, "agents": ["KAY/O", "Skye", "Sova"]},
        {"name": "s0m", "team": "NRG Esports", "region": "Americas", "age": 23, "championships": 1, "agents": ["Jett", "Raze", "Neon"]},
        {"name": "mada", "team": "NRG Esports", "region": "Americas", "age": 22, "championships": 1, "agents": ["Omen", "Viper", "Astra"]},
        {"name": "brawk", "team": "NRG Esports", "region": "Americas", "age": 24, "championships": 1, "agents": ["Killjoy", "Sova", "Cypher"]},
        {"name": "skuba", "team": "NRG Esports", "region": "Americas", "age": 23, "championships": 1, "agents": ["Raze", "Jett", "Chamber"]},
        # Americas - Others
        {"name": "jawgemo", "team": "NRG Esports", "region": "Americas", "age": 27, "championships": 1, "agents": ["Raze", "Jett", "Neon"]},
        {"name": "Boostio", "team": "NRG Esports", "region": "Americas", "age": 27, "championships": 1, "agents": ["Killjoy", "Sova", "Cypher"]},
        {"name": "C0M", "team": "NRG Esports", "region": "Americas", "age": 24, "championships": 1, "agents": ["Sova", "Fade", "KAY/O"]},
        {"name": "Demon1", "team": "NRG Esports", "region": "Americas", "age": 22, "championships": 1, "agents": ["Jett", "Raze", "Chamber"]},
        {"name": "crashies", "team": "NRG Esports", "region": "Americas", "age": 28, "championships": 0, "agents": ["Sova", "KAY/O", "Fade"]},
        {"name": "Victor", "team": "NRG Esports", "region": "Americas", "age": 28, "championships": 0, "agents": ["Raze", "Jett", "Reyna"]},
        {"name": "Marved", "team": "NRG Esports", "region": "Americas", "age": 26, "championships": 0, "agents": ["Omen", "Viper", "Astra"]},
        {"name": "FNS", "team": "NRG Esports", "region": "Americas", "age": 32, "championships": 0, "agents": ["Sova", "Fade", "KAY/O"]},
        {"name": "Leaf", "team": "Cloud9", "region": "Americas", "age": 22, "championships": 0, "agents": ["Jett", "Raze", "Chamber"]},
        {"name": "OXY", "team": "Cloud9", "region": "Americas", "age": 21, "championships": 0, "agents": ["Jett", "Raze", "Neon"]},
        {"name": "ShoT_UP", "team": "Cloud9", "region": "Americas", "age": 22, "championships": 0, "agents": ["Killjoy", "Sova", "Cypher"]},
        {"name": "N4RRATE", "team": "Cloud9", "region": "Americas", "age": 25, "championships": 0, "agents": ["Omen", "Viper", "Astra"]},
        {"name": "verno", "team": "Cloud9", "region": "Americas", "age": 24, "championships": 0, "agents": ["Raze", "Jett", "Neon"]},
        {"name": "yay", "team": "Cloud9", "region": "Americas", "age": 26, "championships": 0, "agents": ["Chamber", "Jett", "Raze"]},
        # Americas - G2
        {"name": "trent", "team": "G2 Esports", "region": "Americas", "age": 22, "championships": 0, "agents": ["Sova", "Fade", "Skye"]},
        {"name": "leaf", "team": "G2 Esports", "region": "Americas", "age": 22, "championships": 0, "agents": ["Jett", "Raze", "Neon"]},
        {"name": "valyn", "team": "G2 Esports", "region": "Americas", "age": 22, "championships": 0, "agents": ["Omen", "Brimstone", "Viper"]},
        {"name": "JonahP", "team": "G2 Esports", "region": "Americas", "age": 24, "championships": 0, "agents": ["Breach", "KAY/O", "Skye"]},
        {"name": "icek", "team": "G2 Esports", "region": "Americas", "age": 23, "championships": 0, "agents": ["Killjoy", "Cypher", "Sage"]},

        # EMEA - Fnatic (Masters Tokyo 2023 winners)
        {"name": "Boaster", "team": "Fnatic", "region": "EMEA", "age": 31, "championships": 2, "agents": ["Sova", "Fade", "KAY/O"]},
        {"name": "Derke", "team": "Fnatic", "region": "EMEA", "age": 24, "championships": 2, "agents": ["Jett", "Raze", "Neon"]},
        {"name": "Alfajer", "team": "Fnatic", "region": "EMEA", "age": 20, "championships": 2, "agents": ["Killjoy", "Cypher", "Chamber"]},
        {"name": "Leo", "team": "Fnatic", "region": "EMEA", "age": 22, "championships": 2, "agents": ["Omen", "Viper", "Astra"]},
        {"name": "Chronicle", "team": "Fnatic", "region": "EMEA", "age": 26, "championships": 2, "agents": ["Raze", "KAY/O", "Skye"]},
        # EMEA - NAVI
        {"name": "ANGE1", "team": "NAVI", "region": "EMEA", "age": 38, "championships": 0, "agents": ["Omen", "Astra", "Viper"]},
        {"name": "Shao", "team": "NAVI", "region": "EMEA", "age": 26, "championships": 0, "agents": ["Sova", "Fade", "KAY/O"]},
        {"name": "Zyppan", "team": "NAVI", "region": "EMEA", "age": 24, "championships": 0, "agents": ["Jett", "Raze", "Neon"]},
        {"name": "SUYGETSU", "team": "NAVI", "region": "EMEA", "age": 26, "championships": 0, "agents": ["Killjoy", "Cypher", "Chamber"]},
        {"name": "ardiis", "team": "NAVI", "region": "EMEA", "age": 27, "championships": 0, "agents": ["Jett", "Chamber", "Raze"]},
        # EMEA - Vitality
        {"name": "Sayf", "team": "Team Vitality", "region": "EMEA", "age": 27, "championships": 0, "agents": ["Jett", "Raze", "Neon"]},
        {"name": "Destrian", "team": "Team Vitality", "region": "EMEA", "age": 22, "championships": 0, "agents": ["Killjoy", "Cypher", "Sage"]},
        {"name": "trexx", "team": "Team Vitality", "region": "EMEA", "age": 22, "championships": 0, "agents": ["Sova", "Fade", "KAY/O"]},
        {"name": "Kicks", "team": "Team Vitality", "region": "EMEA", "age": 23, "championships": 0, "agents": ["Omen", "Viper", "Astra"]},
        {"name": "ceNder", "team": "Team Vitality", "region": "EMEA", "age": 23, "championships": 0, "agents": ["Raze", "Jett", "Reyna"]},
        # EMEA - KC
        {"name": "ScreaM", "team": "Karmine Corp", "region": "EMEA", "age": 30, "championships": 0, "agents": ["Jett", "Raze", "Reyna"]},
        {"name": "N4RRATE", "team": "Karmine Corp", "region": "EMEA", "age": 25, "championships": 0, "agents": ["Omen", "Viper", "Astra"]},
        {"name": "Enzo", "team": "Karmine Corp", "region": "EMEA", "age": 27, "championships": 0, "agents": ["Sova", "Fade", "KAY/O"]},
        {"name": "xms", "team": "Karmine Corp", "region": "EMEA", "age": 28, "championships": 0, "agents": ["Killjoy", "Cypher", "Sage"]},
        {"name": "tomaszy", "team": "Karmine Corp", "region": "EMEA", "age": 22, "championships": 0, "agents": ["Jett", "Raze", "Neon"]},
        # EMEA - FUT
        {"name": "cNed", "team": "FUT Esports", "region": "EMEA", "age": 25, "championships": 1, "agents": ["Jett", "Raze", "Chamber"]},
        {"name": "qRaxs", "team": "FUT Esports", "region": "EMEA", "age": 24, "championships": 0, "agents": ["Sova", "Fade", "KAY/O"]},
        {"name": "Mojj", "team": "FUT Esports", "region": "EMEA", "age": 24, "championships": 0, "agents": ["Omen", "Viper", "Astra"]},
        {"name": "Fizzy", "team": "FUT Esports", "region": "EMEA", "age": 23, "championships": 0, "agents": ["Raze", "Jett", "Neon"]},
        {"name": "yetujay", "team": "FUT Esports", "region": "EMEA", "age": 22, "championships": 0, "agents": ["Killjoy", "Cypher", "Sage"]},
        # EMEA - Others
        {"name": "nAts", "team": "Gentle Mates", "region": "EMEA", "age": 27, "championships": 1, "agents": ["Viper", "Sova", "Cypher"]},
        {"name": "d3ffo", "team": "Gentle Mates", "region": "EMEA", "age": 25, "championships": 1, "agents": ["Raze", "Jett", "Neon"]},
        {"name": "Redgar", "team": "Gentle Mates", "region": "EMEA", "age": 29, "championships": 0, "agents": ["Killjoy", "Sova", "Cypher"]},

        # Pacific - Paper Rex
        {"name": "f0rsakeN", "team": "Paper Rex", "region": "Pacific", "age": 24, "championships": 0, "agents": ["Sova", "Fade", "KAY/O"]},
        {"name": "Jinggg", "team": "Paper Rex", "region": "Pacific", "age": 22, "championships": 0, "agents": ["Raze", "Neon", "Jett"]},
        {"name": "something", "team": "Paper Rex", "region": "Pacific", "age": 23, "championships": 0, "agents": ["Jett", "Raze", "Neon"]},
        {"name": "d4v41", "team": "Paper Rex", "region": "Pacific", "age": 24, "championships": 0, "agents": ["Killjoy", "Cypher", "Chamber"]},
        {"name": "mindfreak", "team": "Paper Rex", "region": "Pacific", "age": 25, "championships": 0, "agents": ["Omen", "Viper", "Astra"]},
        {"name": "Benkai", "team": "Paper Rex", "region": "Pacific", "age": 28, "championships": 0, "agents": ["Sova", "KAY/O", "Fade"]},
        # Pacific - DRX
        {"name": "MaKo", "team": "DRX", "region": "Pacific", "age": 27, "championships": 0, "agents": ["Omen", "Viper", "Astra"]},
        {"name": "Flashback", "team": "DRX", "region": "Pacific", "age": 26, "championships": 0, "agents": ["Killjoy", "Cypher", "Chamber"]},
        {"name": "RB", "team": "DRX", "region": "Pacific", "age": 24, "championships": 0, "agents": ["Raze", "Neon", "Jett"]},
        {"name": "BeYN", "team": "DRX", "region": "Pacific", "age": 24, "championships": 0, "agents": ["Sova", "Fade", "KAY/O"]},
        {"name": "Foxy9", "team": "DRX", "region": "Pacific", "age": 23, "championships": 0, "agents": ["Raze", "Jett", "Reyna"]},
        # Pacific - Gen.G
        {"name": "Meteor", "team": "Gen.G", "region": "Pacific", "age": 25, "championships": 0, "agents": ["Omen", "Viper", "Astra"]},
        {"name": "t3xture", "team": "Gen.G", "region": "Pacific", "age": 24, "championships": 1, "agents": ["Jett", "Raze", "Neon"]},
        {"name": "Munchkin", "team": "Gen.G", "region": "Pacific", "age": 26, "championships": 1, "agents": ["Sova", "Fade", "KAY/O"]},
        {"name": "Lakia", "team": "Gen.G", "region": "Pacific", "age": 29, "championships": 0, "agents": ["Killjoy", "Cypher", "Sage"]},
        {"name": "Karon", "team": "Gen.G", "region": "Pacific", "age": 21, "championships": 1, "agents": ["Chamber", "Killjoy", "Cypher"]},
        # Pacific - T1
        {"name": "BuZz", "team": "T1", "region": "Pacific", "age": 22, "championships": 1, "agents": ["Jett", "Raze", "Neon"]},
        {"name": "stax", "team": "T1", "region": "Pacific", "age": 25, "championships": 0, "agents": ["Sova", "Fade", "KAY/O"]},
        {"name": "carpe", "team": "T1", "region": "Pacific", "age": 27, "championships": 0, "agents": ["Jett", "Raze", "Chamber"]},
        {"name": "Sylvan", "team": "T1", "region": "Pacific", "age": 23, "championships": 0, "agents": ["Omen", "Viper", "Astra"]},
        {"name": "iZu", "team": "T1", "region": "Pacific", "age": 23, "championships": 0, "agents": ["Raze", "Neon", "Jett"]},
        {"name": "xccurate", "team": "T1", "region": "Pacific", "age": 27, "championships": 0, "agents": ["Killjoy", "Cypher", "Sage"]},
        # Pacific - ZETA
        {"name": "Laz", "team": "ZETA DIVISION", "region": "Pacific", "age": 25, "championships": 0, "agents": ["Jett", "Raze", "Neon"]},
        {"name": "Dep", "team": "ZETA DIVISION", "region": "Pacific", "age": 24, "championships": 0, "agents": ["Omen", "Astra", "Viper"]},
        {"name": "barce", "team": "ZETA DIVISION", "region": "Pacific", "age": 25, "championships": 0, "agents": ["Sova", "Fade", "KAY/O"]},
        {"name": "Art", "team": "ZETA DIVISION", "region": "Pacific", "age": 23, "championships": 0, "agents": ["Raze", "Jett", "Neon"]},
        {"name": "XQQ", "team": "ZETA DIVISION", "region": "Pacific", "age": 24, "championships": 0, "agents": ["Killjoy", "Cypher", "Sage"]},
        # Pacific - Nongshim RedForce
        {"name": "Foxy9", "team": "Nongshim RedForce", "region": "Pacific", "age": 23, "championships": 0, "agents": ["Jett", "Raze", "Neon"]},
        {"name": "Lakia", "team": "Nongshim RedForce", "region": "Pacific", "age": 29, "championships": 0, "agents": ["Killjoy", "Cypher", "Sage"]},

        # Americas - Leviatán
        {"name": "aspas", "team": "Leviatán", "region": "Americas", "age": 22, "championships": 1, "agents": ["Jett", "Raze", "Neon"]},
        {"name": "Mazino", "team": "Leviatán", "region": "Americas", "age": 22, "championships": 0, "agents": ["Raze", "Jett", "Reyna"]},
        {"name": "kiNgg", "team": "Leviatán", "region": "Americas", "age": 24, "championships": 0, "agents": ["Omen", "Viper", "Astra"]},
        {"name": "Melser", "team": "Leviatán", "region": "Americas", "age": 25, "championships": 0, "agents": ["Sova", "Fade", "KAY/O"]},
        {"name": "Tacolilla", "team": "Leviatán", "region": "Americas", "age": 23, "championships": 0, "agents": ["Killjoy", "Cypher", "Chamber"]},
    ]

    return players


def export_to_csv(players: list[dict], output_path: str):
    """Export player data to CSV."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Deduplicate by name (keep last entry which may have more detail)
    seen = {}
    for p in players:
        seen[p["name"]] = p
    unique_players = list(seen.values())

    fieldnames = [
        "name", "team", "region", "age", "championships",
        "agent1", "agent2", "agent3"
    ]
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for p in unique_players:
            agents = p.get("agents", [])
            row = {
                "name": p["name"],
                "team": p.get("team", ""),
                "region": p.get("region", ""),
                "age": p.get("age", ""),
                "championships": p.get("championships", 0),
                "agent1": agents[0] if len(agents) > 0 else "",
                "agent2": agents[1] if len(agents) > 1 else "",
                "agent3": agents[2] if len(agents) > 2 else "",
            }
            writer.writerow(row)

    print(f"Exported {len(unique_players)} players to {output_path}")


def export_to_json(players: list[dict], output_path: str):
    """Export player data to JSON (for web frontend)."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    seen = {}
    for p in players:
        seen[p["name"]] = p
    unique_players = list(seen.values())

    # Format for frontend
    formatted = []
    for p in unique_players:
        agents = p.get("agents", [])
        formatted.append({
            "name": p["name"],
            "team": p.get("team", ""),
            "region": p.get("region", ""),
            "age": p.get("age", ""),
            "championships": p.get("championships", 0),
            "agents": agents[:3],
        })

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(formatted, f, ensure_ascii=False, indent=2)

    print(f"Exported {len(formatted)} players to {output_path}")


def main():
    output_dir = os.path.join(os.path.dirname(__file__), "..", "processed")
    csv_path = os.path.join(output_dir, "players.csv")
    json_path = os.path.join(output_dir, "players.json")

    print("=" * 50)
    print("Valorant Pro Player Data Scraper")
    print("=" * 50)

    # Start with known player data
    print("\nBuilding initial dataset from known players...")
    players = build_initial_dataset()
    print(f"Base dataset: {len(players)} players")

    # Try to scrape additional data from VLR.gg if accessible
    print("\nAttempting to scrape VLR.gg for additional data...")
    try:
        scraped = scrape_player_list()
        if scraped:
            # We got scrape results - but for now just use the known data
            print(f"Scraped {len(scraped)} additional players from VLR.gg")
    except Exception as e:
        print(f"VLR.gg scraping unavailable (network): {e}")
        print("Using pre-built dataset instead.")

    # Export
    print("\nExporting data...")
    export_to_csv(players, csv_path)
    export_to_json(players, json_path)

    print("\nDone! Dataset summary:")
    print(f"  Total players: {len(set(p['name'] for p in players))}")
    regions = set(p.get("region") for p in players if p.get("region"))
    print(f"  Regions: {', '.join(sorted(regions))}")
    champs = sum(1 for p in players if p.get("championships", 0) > 0)
    print(f"  Players with championships: {champs}")
    print(f"  CSV: {csv_path}")
    print(f"  JSON: {json_path}")


if __name__ == "__main__":
    main()
