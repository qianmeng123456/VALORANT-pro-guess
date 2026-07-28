/**
 * data.js - Player data loader
 * Loads the player database from players.json
 */

const DATA = {
  players: [],
  playerMap: {}, // name -> player
  allNames: [],  // sorted list of player names
  loaded: false,
  loadError: null,
};

async function loadPlayerData() {
  try {
    const response = await fetch('data/players.json');
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    DATA.players = await response.json();

    // Build lookup map and name list
    DATA.playerMap = {};
    DATA.players.forEach(p => {
      DATA.playerMap[p.name] = p;
    });
    DATA.allNames = DATA.players.map(p => p.name).sort();
    DATA.loaded = true;

    // Update UI
    document.getElementById('player-count').textContent = `${DATA.players.length} 名选手`;
    enableGuessInput();
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
  input.placeholder = '输入选手 ID...';
  btn.disabled = false;
}

function findPlayer(name) {
  return DATA.playerMap[name] || null;
}

function searchPlayers(query) {
  if (!query || query.length < 1) return [];
  const q = query.toLowerCase();
  return DATA.allNames.filter(name => name.toLowerCase().includes(q)).slice(0, 8);
}
