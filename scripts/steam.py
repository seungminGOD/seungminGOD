import os
import requests

README_FILE = "README.md"

STEAM_API_KEY = os.environ["STEAM_API_KEY"]
STEAM_ID = "76561198035491721"

START = "<!-- STEAM-START -->"
END = "<!-- STEAM-END -->"


def get_data(url, params):
    response = requests.get(url, params=params, timeout=20)
    response.raise_for_status()
    return response.json()


# ===========================
# 프로필 정보
# ===========================

profile = get_data(
    "https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v2/",
    {
        "key": STEAM_API_KEY,
        "steamids": STEAM_ID
    }
)

player = profile["response"]["players"][0]

name = player["personaname"]
avatar = player["avatarfull"]
profile_url = player["profileurl"]
game = player.get("gameextrainfo")

states = {
    0: "⚫ Offline",
    1: "🟢 Online",
    2: "🔴 Busy",
    3: "🟡 Away",
    4: "😴 Snooze",
    5: "💱 Looking to Trade",
    6: "🎮 Looking to Play"
}

state = states.get(player["personastate"], "Unknown")


# ===========================
# Steam Level
# ===========================

level = get_data(
    "https://api.steampowered.com/IPlayerService/GetSteamLevel/v1/",
    {
        "key": STEAM_API_KEY,
        "steamid": STEAM_ID
    }
)

steam_level = level["response"]["player_level"]


# ===========================
# 보유 게임
# ===========================

owned = get_data(
    "https://api.steampowered.com/IPlayerService/GetOwnedGames/v1/",
    {
        "key": STEAM_API_KEY,
        "steamid": STEAM_ID,
        "include_appinfo": 1,
        "include_played_free_games": 1
    }
)

games = owned["response"].get("games", [])

game_count = owned["response"].get("game_count", 0)

total_minutes = sum(g["playtime_forever"] for g in games)
total_hours = round(total_minutes / 60, 1)

top_games = sorted(
    games,
    key=lambda x: x["playtime_forever"],
    reverse=True
)[:5]


# ===========================
# 최근 플레이
# ===========================

recent = get_data(
    "https://api.steampowered.com/IPlayerService/GetRecentlyPlayedGames/v1/",
    {
        "key": STEAM_API_KEY,
        "steamid": STEAM_ID
    }
)

recent_games = recent["response"].get("games", [])


# ===========================
# README 내용
# ===========================

steam = []

steam.append(f'<a href="{profile_url}">')
steam.append(f'<img width="120" src="{avatar}"/>')
steam.append("</a>")
steam.append("")
steam.append(f"## {name}")
steam.append("")
steam.append(f"🟢 **Status** : {state}")
steam.append("")
steam.append(f"🎖 **Steam Level** : {steam_level}")
steam.append("")
steam.append(f"🎮 **Owned Games** : {game_count}")
steam.append("")
steam.append(f"⏰ **Total Playtime** : {total_hours} hrs")
steam.append("")

if game:
    steam.append(f"🔥 **Currently Playing** : {game}")
else:
    steam.append("🔥 **Currently Playing** : None")

steam.append("")
steam.append("---")
steam.append("")
steam.append("### 🔥 Recently Played")
steam.append("")

if recent_games:
    for g in recent_games:
        steam.append(
            f"- {g['name']} ({round(g['playtime_2weeks']/60,1)} hrs / 2 weeks)"
        )
else:
    steam.append("- No recent games.")

steam.append("")
steam.append("---")
steam.append("")
steam.append("### 🏆 Top Played Games")
steam.append("")

for i, g in enumerate(top_games, start=1):
    steam.append(
        f"{i}. {g['name']} - {round(g['playtime_forever']/60,1)} hrs"
    )


steam_text = "\n".join(steam)


# ===========================
# README 수정
# ===========================

with open(README_FILE, "r", encoding="utf-8") as f:
    readme = f.read()

start = readme.find(START)
end = readme.find(END)

new_readme = (
    readme[:start + len(START)]
    + "\n"
    + steam_text
    + "\n"
    + readme[end:]
)

with open(README_FILE, "w", encoding="utf-8") as f:
    f.write(new_readme)

print("Steam README 업데이트 완료!")
