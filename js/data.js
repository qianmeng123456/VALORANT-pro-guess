/**
 * data.js - Player data loader
 * Loads the player database from players.json
 */

const DATA = {
  players: [],
  playerMap: {}, // name -> player
  playerMapLower: {}, // lowercase name -> player (for case-insensitive lookup)
  allNames: [],  // sorted list of player names
  loaded: false,
  loadError: null,
};

async function loadPlayerData() {
  try {
    const response = await fetch('data/players.json');
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    DATA.players = await response.json();

    // Build lookup maps and name list
    DATA.playerMap = {};
    DATA.playerMapLower = {};
    DATA.players.forEach(p => {
      DATA.playerMap[p.name] = p;
      DATA.playerMapLower[p.name.toLowerCase()] = p;
    });
    DATA.allNames = DATA.players.map(p => p.name).sort();
    DATA.loaded = true;

    // Update UI
    document.getElementById('player-count').textContent = `${DATA.players.length} 名选手`;
    return true;
  } catch (err) {
    DATA.loadError = err.message;
    document.getElementById('player-count').textContent = '加载失败';
    document.getElementById('hint-text').textContent = `⚠️ 数据加载失败: ${err.message}`;
    return false;
  }
}

function enableGuessInput() {
  const input = document.getElementById('guess-input');
  const btn = document.getElementById('guess-btn');
  input.disabled = false;
  input.placeholder = '输入选手 ID... 如 ZmjjKK、f0rsakeN、TenZ';
  btn.disabled = false;
}

function findPlayer(name) {
  return DATA.playerMap[name] || DATA.playerMapLower[name.toLowerCase()] || null;
}

function searchPlayers(query, regionFilter, teamFilter) {
  if (!query || query.length < 1) return [];
  const q = query.toLowerCase();
  return DATA.allNames.filter(name => {
    if (!name.toLowerCase().includes(q)) return false;
    if (regionFilter || teamFilter) {
      const player = DATA.playerMap[name];
      if (!player) return false;
      if (regionFilter && player.region !== regionFilter) return false;
      if (teamFilter && player.team !== teamFilter) return false;
    }
    return true;
  }).slice(0, 8);
}

function getTeamsByRegion(regionFilter) {
  const teams = new Set();
  DATA.players.forEach(p => {
    if (!regionFilter || p.region === regionFilter) {
      teams.add(p.team);
    }
  });
  return Array.from(teams).sort();
}
