"""Download Valorant agent icons from the official API."""
import os
import urllib.request
import json

AGENTS = {
    "Jett": "add6443a-41bd-e414-f6ad-e58d267f4e95",
    "Raze": "f94c3b30-42be-e959-889c-5aa313dba261",
    "Phoenix": "eb93336a-449b-9c1b-0a54-a891f7921d69",
    "Reyna": "a3bfb853-43b2-7238-a4f1-ad90e9e46bcc",
    "Yoru": "7f94d92c-4234-0a36-9646-3a87eb8b5c89",
    "Neon": "bb2a4828-46eb-8cd1-e765-15848195d751",
    "Chamber": "22697a3d-45bf-8dd7-4fec-84a9e28c69d7",
    "Sage": "569fdd95-4d10-43ab-ca70-79becc718b46",
    "Skye": "6f2a04ca-43e0-be17-7f36-b3908627744d",
    "Killjoy": "1e58de9c-4950-5125-93e9-a0aee9f98746",
    "Cypher": "117ed9e3-49f3-6512-3ccf-0cada7e3823b",
    "Viper": "707eab51-4836-f488-046a-cda6bf494859",
    "Omen": "8e253930-4c05-31dd-1b6c-968525494517",
    "Brimstone": "9f0d8ba9-4140-b941-57d3-a7ad57c6b417",
    "Astra": "41fb69c1-4189-7b37-f117-bcaf1e96f1bf",
    "Harbor": "95b78ed7-4637-86d9-7e41-71ba8c293152",
    "Clove": "1dbf2edd-4729-0984-3115-daa5eed44993",
    "Sova": "320b2a48-4d9b-a075-30f1-1f93a9b638fa",
    "Breach": "5f8d3a7f-467b-97f3-062c-13acf203c006",
    "KAY/O": "601dbbe7-43ce-be57-2a40-4abd24953621",
    "Fade": "dade69b4-4f5a-8528-247b-219e5a1facd6",
    "Gekko": "e370fa57-4757-3604-3648-499e1f642d3f",
    "Vyse": "efba5359-4016-a1e5-7626-b1ae76895940",
    "Deadlock": "cc8b64c8-4b25-4ff9-6e7f-37b4da43d235",
    "Iso": "0e38b510-41a8-5780-5e8f-568b2a4f2d6c",
    "Tejo": "b444168c-4e35-8076-db47-ef9bf368f384",
    "Waylay": "df1cb487-4902-002e-5c17-d28e83e78588",
}

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "src", "assets", "agents")
os.makedirs(OUTPUT_DIR, exist_ok=True)

for name, uuid in AGENTS.items():
    url = f"https://media.valorant-api.com/agents/{uuid}/displayicon.png"
    filename = f"{name.lower().replace('/', '_')}.png"
    filepath = os.path.join(OUTPUT_DIR, filename)

    if os.path.exists(filepath) and os.path.getsize(filepath) > 1000:
        print(f"  SKIP {name} (already exists)")
        continue

    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as resp:
            with open(filepath, 'wb') as f:
                f.write(resp.read())
        size = os.path.getsize(filepath)
        print(f"  OK   {name} ({size} bytes)")
    except Exception as e:
        print(f"  FAIL {name}: {e}")

print(f"\nDownloaded {len(os.listdir(OUTPUT_DIR))} agent icons to {OUTPUT_DIR}")
