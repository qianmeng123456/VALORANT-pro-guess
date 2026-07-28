# QA Report - Valorant Pro Player Guessing Game

**Date:** 2026-07-28
**Project:** fuyiba (无畏契约选手猜一猜)
**Files evaluated:** 8 source files + 27 asset files

---

## 1. Data Quality Issues

### 1.1 [CRITICAL] Raze/Reyna Chinese Translation Swap

**File:** `data/scripts/build_dataset.py`, line 218
**File affected:** `src/data/players.json` (generated from the script)

The agent translation mapping has incorrect Chinese names:

```python
# Current (WRONG):
"Raze": "蕾娜",    # 蕾娜 is Reyna's Chinese name
"Reyna": "芮娜",   # incorrect for Reyna
```

The official Valorant Chinese client translations are:
- **Raze** = 雷兹 (not 蕾娜)
- **Reyna** = 芮娜 (or 蕾娜 in some community usage)

**Impact:** Every player in `players.json` who plays Raze has `agents_cn` entries showing "蕾娜" (Reyna's name) instead of "雷兹". This affects approximately 60+ players across all regions. For players who play both Raze and Reyna (e.g., hfmi0, Asuna, ScreaM, Mazino, Foxy9, Kryptix, nukkye), the confusion is compounded — both agent slots show variants of 蕾/芮 when they should be distinct.

**Recommendation:** Change the mapping to:
```python
"Raze": "雷兹",
"Reyna": "蕾娜",
```

Then regenerate `players.json`.

---

### 1.2 [HIGH] Duplicate Player Entries in Build Data

**File:** `data/scripts/build_dataset.py`

Four player names appear in the `PLAYERS` list multiple times with different team affiliations:

| Player | First occurrence | Second occurrence |
|--------|-----------------|-------------------|
| `nAts` | Gentle Mates (line 139) | Team Liquid (line 144) |
| `Sylvan` | T1 (line 187) | Nongshim RedForce (line 198) |
| `Lakia` | DRX (line 176) | Nongshim RedForce (line 199) |
| `Art` | MIBR (line 98) | ZETA DIVISION (line 194) |

The `deduplicate()` function keeps the first occurrence, silently discarding the second. This results in incomplete rosters for Team Liquid (only 4 players), Nongshim RedForce (only 3 players), and ZETA DIVISION (only 4 players).

**Recommendation:** These players have genuinely played for multiple teams (e.g., nAts was on Team Liquid before Gentle Mates). Decide which team roster represents the current/target season and remove the outdated entry, or add disambiguated entries (e.g., "nAts_TL").

---

### 1.3 [MEDIUM] Incomplete Team Rosters

Several teams have fewer than the standard 5-player roster:

| Team | Players in dataset |
|------|-------------------|
| G2 Esports | 4 (missing 1) |
| MIBR | 4 (missing 1) |
| KOI | 4 (missing 1) |
| Team Liquid | 4 (after nAts dedup) |
| Nongshim RedForce | 3 (after Sylvan & Lakia dedup) |
| ZETA DIVISION | 4 (after Art dedup) |
| Leviatán | 4 (missing 1) |
| Global Esports | 5 (complete) |
| FUT Esports | 5 (complete) |
| Gentle Mates | 4 (missing 1) |

**Recommendation:** Add missing players or document that only core rosters are included.

---

### 1.4 [MEDIUM] Stale Age Data

All player ages are hardcoded integers in `build_dataset.py`. As of July 2026, these ages are outdated — some by 2+ years. For example, TenZ is listed as 24 but would be approximately 25 given his 2001 birth year.

**Recommendation:** Either store birth years and compute age dynamically, or accept this as a known limitation and add a data freshness disclaimer.

---

### 1.5 [LOW] `team_cn` Redundancy for Certain Teams

Some teams have `team_cn` identical to `team` (e.g., Sentinels, LOUD, Fnatic, Gen.G, DRX). While harmless, it adds unnecessary data duplication.

---

## 2. Game Logic Bugs

### 2.1 [CRITICAL] `getAgentCN()` Function Always Returns Empty String

**File:** `src/js/game.js`, lines 201-205

```javascript
function getAgentCN(agentName) {
  const lookup = DATA.playerMap[GAME.guesses[0]?.guess?.name];
  // Use the agents_cn from whichever player data has it
  return '';
}
```

This function:
1. Performs a lookup it never uses.
2. Always returns an empty string `''`.
3. Accepts an `agentName` parameter it ignores.

**Impact:** Any code relying on `getAgentCN()` to display Chinese agent names will get nothing.

**Recommendation:** Implement properly:
```javascript
function getAgentCN(agentName) {
  const player = GAME.guesses[GAME.guesses.length - 1]?.guess;
  if (!player) return agentName;
  const idx = player.agents.indexOf(agentName);
  return (idx >= 0 && player.agents_cn) ? player.agents_cn[idx] : agentName;
}
```

Note: This function is not called anywhere in the current code, so the bug is dormant. The UI uses `guess.agents_cn[i]` directly in `renderAgentField()` instead.

---

### 2.2 [LOW] Dead Code in `initGame()`

**File:** `src/js/game.js`, lines 29-48

```javascript
function initGame() {
  // Pick a random player as the target
  const idx = Math.floor(Math.random() * DATA.players.length);
  GAME.targetPlayer = DATA.players[idx];   // <-- immediately overwritten below
  ...
  const dailyIdx = dateSeed % DATA.players.length;
  GAME.targetPlayer = DATA.players[dailyIdx];  // <-- actual target
  ...
}
```

The first random selection (lines 31-32) is computed and assigned but immediately overwritten by the date-seeded selection (lines 43-46).

**Recommendation:** Remove lines 31-32 (the stray random selection).

---

### 2.3 [LOW] Unused `getDailySeed()` Function

**File:** `src/js/game.js`, lines 51-55

The `getDailySeed()` function is defined but never called. The daily seed logic is duplicated inline in `initGame()`.

**Recommendation:** Either delete `getDailySeed()` or refactor `initGame()` to use it.

---

### 2.4 [LOW] Agent Comparison Uses Case-Insensitive Matching but No Trim

**File:** `src/js/game.js`, lines 120-121

```javascript
const guessAgents = (guess.agents || []).map(a => a.toLowerCase());
const targetAgents = (target.agents || []).map(a => a.toLowerCase());
```

Names are lowercased but not trimmed. If any agent name in the JSON has leading/trailing whitespace (currently none do), matching would fail.

---

### 2.5 [INFO] Win Detection Uses `correctCount === 6`

**File:** `src/js/game.js`, line 143

```javascript
result.isWin = correctCount === 6;
```

Since there are exactly 6 fields checked (id, age, region, team, champ, agent), this is correct. The constant 6 should ideally reference `result.totalFields` which is already defined as 6 on line 70, for maintainability.

---

## 3. UI/UX Issues

### 3.1 [MEDIUM] No Per-Agent Match Highlighting

**File:** `src/js/ui.js`, lines 178-203

In `renderAgentField()`, all three agent icons are rendered identically regardless of whether each individual agent matched the target. The only feedback is a collective badge ("匹配 1/3", "匹配 2/3", "全部正确", "无匹配").

**Impact:** Users cannot tell WHICH of their guessed agents matched. They have to deduce from the count alone.

**Recommendation:** Compare each agent individually against the target's agents and apply a green border/tint to matching agent icons and a red/muted style to non-matching ones. Example CSS addition: `.agent-icon.matched { border: 2px solid var(--color-correct); }` and `.agent-icon.unmatched { opacity: 0.4; }`.

---

### 3.2 [MEDIUM] No Maximum Guess Limit

**File:** `src/js/game.js`, `src/js/ui.js`

There is no cap on the number of guesses. With 157 players, a determined user could brute-force the answer by guessing every player. Most similar games (Wordle, LoLdle, etc.) limit attempts to 6-8.

**Recommendation:** Add a max guess limit (e.g., 8) and show a "game over" state when exceeded, revealing the target player.

---

### 3.3 [LOW] Agent Icon `onerror` Fallback Missing

**File:** `src/js/ui.js`, lines 184-188

Agent icons are rendered as `<img>` tags with no `onerror` handler:

```javascript
html += `<img src="${iconPath}" alt="${agent}" title="${agent} / ${cnName}" class="agent-icon">`;
```

If an icon file is missing, the browser shows a broken image icon. All 27 agent PNG files from the assets directory do exist, but if new agents are added to player data without corresponding icon files, broken images will appear.

**Recommendation:** Add an `onerror` fallback:
```javascript
html += `<img src="${iconPath}" alt="${agent}" title="${agent} / ${cnName}" class="agent-icon" onerror="this.style.display='none'">`;
```

---

### 3.4 [LOW] Auto-Complete Uses `textContent` Instead of `dataset.name`

**File:** `src/js/ui.js`, line 29

```javascript
this.value = suggestions[UI.selectedSuggestion].textContent;
```

Should use `suggestions[UI.selectedSuggestion].dataset.name` for robustness. In practice both values are identical since the auto-complete item renders just the player name, but `dataset.name` is the canonical source.

---

### 3.5 [LOW] No "Give Up / Reveal Answer" Button

Users cannot voluntarily end the game to see the answer without either guessing correctly or waiting until the next day (daily seed is date-based so the same player persists all day).

**Recommendation:** Add a "Show Answer" button that reveals the target and ends the game.

---

### 3.6 [LOW] No Way to Dismiss the Win Modal

**File:** `src/index.html`, line 61

The win modal has no close button or click-outside-to-dismiss behavior. The only way to interact after winning is via the Share or New Game buttons.

---

### 3.7 [LOW] Font Size Declines Sharply on Mobile

**File:** `src/css/style.css`, lines 432-442

The responsive breakpoints at 640px and 480px reduce font sizes and column widths aggressively. The `col-age` and `col-champ` drop to 0.75rem at 480px which may be hard to read on small screens.

---

## 4. Code Quality Issues

### 4.1 [MEDIUM] Date Seed Calculation Ignores Month/Day Separators

**File:** `src/js/game.js`, lines 43-44

```javascript
const dateStr = today.toISOString().split('T')[0];  // e.g., "2026-07-28"
const dateSeed = dateStr.split('-').reduce((a, b) => a + parseInt(b), 0);
```

This produces `2026 + 7 + 28 = 2061`. The problem is that different dates can produce the same seed (e.g., 2026-01-09 = 2036, 2026-01-18 = 2045 — these are different). Actually this is fine for uniqueness. But simpler dates like 2026-01-01 and 2026-02-00 (invalid) aren't an issue. The approach works for a daily seed but could be simplified.

The unused `getDailySeed()` uses a different algorithm altogether (sum of char codes), which is inconsistent.

---

### 4.2 [LOW] Build Script Output Path Mismatch

**File:** `data/scripts/build_dataset.py`, lines 339-347

The build script outputs to `data/processed/players.json`, but the frontend loads from `src/data/players.json`. This requires a manual copy step. The script acknowledges this in its print statement.

**Recommendation:** Either update the script to output directly to `src/data/players.json`, or add an automated copy step.

---

### 4.3 [LOW] `enableGuessInput()` Sets Button to Disabled=False, Then `main.js` Sets It Back to True

**File:** `src/js/data.js`, line 45 and `src/js/main.js`, line 20

- `loadPlayerData()` calls `enableGuessInput()` which sets `btn.disabled = false`
- `init()` in main.js then immediately sets `btn.disabled = true`

The net result is correct (button starts disabled), but there's a redundant state toggle.

---

### 4.4 [LOW] No Input Sanitization for Player Names

**File:** `src/js/ui.js`, line 95

The guess input value is only trimmed with `.trim()`. If a user types extra spaces in the middle (e.g., "Ten   Z"), it won't match the exact name "TenZ". This is arguably correct behavior since names must be typed exactly, but it could be confusing.

---

## 5. Recommendations Summary by Priority

### Critical (Must Fix)

1. **Fix Raze/Reyna Chinese translation** in `build_dataset.py` and regenerate `players.json` (Section 1.1)
2. **Fix or remove `getAgentCN()`** function (Section 2.1)

### High (Should Fix)

3. **Resolve duplicate player entries** in `build_dataset.py` — decide which team each player belongs to (Section 1.2)
4. **Add per-agent match highlighting** in the UI to show which specific agents matched (Section 3.1)
5. **Add a maximum guess limit** (e.g., 8) with a game-over state (Section 3.2)

### Medium (Consider Fixing)

6. **Add missing players** to incomplete team rosters (Section 1.3)
7. **Add agent icon `onerror` fallback** (Section 3.3)
8. **Add "Give Up / Reveal Answer" button** (Section 3.5)

### Low (Nice to Have)

9. **Remove dead code** in `initGame()` and `getDailySeed()` (Sections 2.2, 2.3)
10. **Align build script output path** with frontend loading path (Section 4.2)
11. **Add win modal dismiss** (click-outside or close button) (Section 3.6)
12. **Use `dataset.name`** in auto-complete selection instead of `textContent` (Section 3.4)
13. **Address stale age data** — consider birth years or add disclaimer (Section 1.4)

---

## 6. Things That Are Working Well

- **Auto-complete search** works correctly with case-insensitive matching and keyboard navigation
- **Duplicate guess prevention** correctly blocks re-guessing the same player
- **Daily seed mechanism** ensures all users get the same puzzle each day (good for social sharing)
- **Share/grid output** generates a shareable emoji grid similar to Wordle
- **Agent icon assets** (27 PNG files) are present and match the `getAgentIconPath()` naming convention (including the KAY/O -> `kay_o.png` transformation)
- **CSS styling** is responsive with two mobile breakpoints
- **Data loading** has proper error handling with user-visible error messages
- **All 157 players** in `players.json` have complete required fields (name, team, region, age, championships, agents, team_cn, agents_cn, region_cn)
- **Toast notification** system works cleanly for clipboard copy feedback
