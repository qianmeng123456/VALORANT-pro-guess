/**
 * game.js - Core game logic
 * Handles guess comparison, color feedback, game state
 */

const GAME = {
  targetPlayer: null,
  guesses: [],
  isOver: false,
};

// Feedback types
const FEEDBACK = {
  CORRECT: 'correct',
  PARTIAL: 'partial',
  WRONG: 'wrong',
  HINT_UP: 'hint-up',
  HINT_DOWN: 'hint-down',
};

// Chinese text for regions
const REGION_CN = {
  'Americas': '美洲',
  'EMEA': 'EMEA',
  'Pacific': '太平洋',
  'China': '中国',
};

function initGame() {
  GAME.guesses = [];
  GAME.isOver = false;

  // Random challenge: pick a random player for each session
  const randomIdx = Math.floor(Math.random() * DATA.players.length);
  GAME.targetPlayer = DATA.players[randomIdx];

  document.getElementById('game-date').textContent =
    `第 ${DATA.allNames.indexOf(GAME.targetPlayer.name) + 1}/${DATA.players.length} 号 · 随机一局`;

  return GAME.targetPlayer;
}

/**
 * Compare a guessed player against the target player.
 * Returns feedback object with color-coded results for each field.
 */
function compareGuess(guessedName) {
  const guess = findPlayer(guessedName);
  const target = GAME.targetPlayer;

  if (!guess) return null;

  const result = {
    guess: guess,
    fields: {},
    matchCount: 0,
    totalFields: 6,
  };

  // 1. ID - exact match
  if (guess.name === target.name) {
    result.fields.id = { status: FEEDBACK.CORRECT, value: guess.name };
  } else {
    result.fields.id = { status: FEEDBACK.WRONG, value: guess.name };
  }

  // 2. Age - with up/down hints
  const gAge = parseInt(guess.age);
  const tAge = parseInt(target.age);
  if (guess.age === target.age && guess.age !== '') {
    result.fields.age = { status: FEEDBACK.CORRECT, value: guess.age };
  } else if (isNaN(gAge) || guess.age === '') {
    result.fields.age = { status: FEEDBACK.WRONG, value: guess.age || '??' };
  } else if (gAge < tAge) {
    result.fields.age = { status: FEEDBACK.HINT_UP, value: guess.age }; // target is older
  } else {
    result.fields.age = { status: FEEDBACK.HINT_DOWN, value: guess.age }; // target is younger
  }

  // 3. Region
  if (guess.region === target.region) {
    result.fields.region = { status: FEEDBACK.CORRECT, value: REGION_CN[guess.region] || guess.region };
  } else {
    result.fields.region = { status: FEEDBACK.WRONG, value: REGION_CN[guess.region] || guess.region };
  }

  // 4. Team
  if (guess.team === target.team) {
    result.fields.team = { status: FEEDBACK.CORRECT, value: guess.team_cn || guess.team };
  } else {
    result.fields.team = { status: FEEDBACK.WRONG, value: guess.team_cn || guess.team };
  }

  // 5. Championship count
  const gChamp = parseInt(guess.championships) || 0;
  const tChamp = parseInt(target.championships) || 0;
  if (gChamp === tChamp) {
    result.fields.champ = { status: FEEDBACK.CORRECT, value: gChamp };
  } else if (gChamp < tChamp) {
    result.fields.champ = { status: FEEDBACK.HINT_UP, value: gChamp };
  } else {
    result.fields.champ = { status: FEEDBACK.HINT_DOWN, value: gChamp };
  }

  // 6. Agent (top 3) - per-agent matching
  const guessAgents = (guess.agents || []).map(a => a.toLowerCase());
  const targetAgents = (target.agents || []).map(a => a.toLowerCase());
  const agentMatches = (guess.agents || []).map(agent => ({
    name: agent,
    matched: targetAgents.includes(agent.toLowerCase())
  }));
  const matchCount = agentMatches.filter(a => a.matched).length;

  if (matchCount === 3) {
    result.fields.agent = { status: FEEDBACK.CORRECT, value: guess.agents || [], matches: agentMatches, matchCount: 3 };
  } else if (matchCount > 0) {
    result.fields.agent = { status: FEEDBACK.PARTIAL, value: guess.agents || [], matches: agentMatches, matchCount };
  } else {
    result.fields.agent = { status: FEEDBACK.WRONG, value: guess.agents || [], matches: agentMatches, matchCount: 0 };
  }

  // Count total matches
  let correctCount = 0;
  let partialCount = 0;
  for (const key of ['id', 'age', 'region', 'team', 'champ', 'agent']) {
    if (result.fields[key].status === FEEDBACK.CORRECT) correctCount++;
    else if (result.fields[key].status === FEEDBACK.PARTIAL) partialCount++;
  }
  result.matchCount = correctCount;
  result.partialCount = partialCount;

  // Check if won (all correct)
  result.isWin = correctCount === result.totalFields;

  return result;
}

function getGuessHistory() {
  return GAME.guesses;
}

function addGuess(guessResult) {
  GAME.guesses.push(guessResult);
  if (guessResult.isWin) {
    GAME.isOver = true;
  } else if (GAME.guesses.length >= MAX_GUESSES) {
    GAME.isOver = true;
  }
}

function isGameOver() {
  return GAME.isOver;
}

/**
 * Generate share text (emoji grid similar to Wordle)
 */
function generateShareText() {
  const target = GAME.targetPlayer;
  const guesses = GAME.guesses;
  const emojiMap = {
    'correct': '🟩',
    'partial': '🟨',
    'wrong': '⬛',
    'hint-up': '🔺',
    'hint-down': '🔻',
  };

  let text = `🎯 无畏契约选手猜一猜\n`;
  text += `${guesses.length} 次猜中 ${target.name}\n\n`;

  const fieldLabels = ['ID', '年龄', '赛区', '战队', '冠军', '英雄'];

  for (const guess of guesses) {
    const line = fieldLabels.map((label, i) => {
      const key = ['id', 'age', 'region', 'team', 'champ', 'agent'][i];
      return emojiMap[guess.fields[key].status] || '⬜';
    }).join('');
    text += line + '\n';
  }

  text += `\nfuyiba.valorant-guess.game`;
  return text;
}

// Agent icon filename helper
function getAgentIconPath(agentName) {
  const name = agentName.toLowerCase().replace(/[^a-z0-9]/g, '_');
  return `assets/agents/${name}.png`;
}

// Max guesses before game over (configurable, persisted to localStorage)
let MAX_GUESSES = (() => {
  try {
    return parseInt(localStorage.getItem('maxGuesses')) || 8;
  } catch (e) {
    return 8;
  }
})();

function setMaxGuesses(n) {
  const val = Math.max(3, Math.min(20, parseInt(n) || 8));
  MAX_GUESSES = val;
  try {
    localStorage.setItem('maxGuesses', String(val));
  } catch (e) {}
}

function getMaxGuesses() {
  return MAX_GUESSES;
}
