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
    totalFields: 8,
  };

  // Helper: get all teams (current + previous) for a player
  function getAllTeams(p) {
    const teams = p.team ? [p.team] : [];
    if (p.previous_teams) teams.push(...p.previous_teams);
    return teams;
  }

  // Helper: get all regions (current + previous) for a player
  function getAllRegions(p) {
    const regions = p.region ? [p.region] : [];
    if (p.previous_regions) regions.push(...p.previous_regions);
    return regions;
  }

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
    result.fields.age = { status: FEEDBACK.HINT_UP, value: guess.age };
  } else {
    result.fields.age = { status: FEEDBACK.HINT_DOWN, value: guess.age };
  }

  // 3. Region - multi-value matching
  const guessRegions = getAllRegions(guess);
  const targetRegions = getAllRegions(target);
  const regionItems = guessRegions.map(r => ({
    name: r,
    name_cn: REGION_CN[r] || r,
    matched: targetRegions.includes(r)
  }));
  const regionMatchCount = regionItems.filter(i => i.matched).length;
  result.fields.region = {
    status: regionMatchCount === guessRegions.length ? FEEDBACK.CORRECT
          : regionMatchCount > 0 ? FEEDBACK.PARTIAL : FEEDBACK.WRONG,
    items: regionItems,
    matchCount: regionMatchCount,
    totalCount: guessRegions.length,
  };

  // 4. Team - multi-value matching
  const guessTeams = getAllTeams(guess);
  const targetTeams = getAllTeams(target);
  const teamCnMap = {};
  teamCnMap[guess.team] = guess.team_cn || guess.team;
  if (target.team_cn) teamCnMap[target.team] = target.team_cn;
  (guess.previous_teams_cn || []).forEach((cn, i) => {
    teamCnMap[guess.previous_teams[i]] = cn;
  });
  (target.previous_teams_cn || []).forEach((cn, i) => {
    teamCnMap[target.previous_teams[i]] = cn;
  });
  const teamItems = guessTeams.map(t => ({
    name: t,
    name_cn: teamCnMap[t] || t,
    matched: targetTeams.includes(t)
  }));
  const teamMatchCount = teamItems.filter(i => i.matched).length;
  result.fields.team = {
    status: teamMatchCount === guessTeams.length ? FEEDBACK.CORRECT
          : teamMatchCount > 0 ? FEEDBACK.PARTIAL : FEEDBACK.WRONG,
    items: teamItems,
    matchCount: teamMatchCount,
    totalCount: guessTeams.length,
  };

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
  const agentMatchCount = agentMatches.filter(a => a.matched).length;
  if (agentMatchCount === 3) {
    result.fields.agent = { status: FEEDBACK.CORRECT, value: guess.agents || [], matches: agentMatches, matchCount: 3 };
  } else if (agentMatchCount > 0) {
    result.fields.agent = { status: FEEDBACK.PARTIAL, value: guess.agents || [], matches: agentMatches, matchCount: agentMatchCount };
  } else {
    result.fields.agent = { status: FEEDBACK.WRONG, value: guess.agents || [], matches: agentMatches, matchCount: 0 };
  }

  // 7. Nationality
  if (guess.nationality && target.nationality && guess.nationality === target.nationality) {
    result.fields.nationality = { status: FEEDBACK.CORRECT, value: guess.nationality_cn || guess.nationality };
  } else {
    result.fields.nationality = { status: FEEDBACK.WRONG, value: guess.nationality_cn || guess.nationality || '??' };
  }

  // 8. Debut year
  const gDebut = parseInt(guess.debut_year) || 0;
  const tDebut = parseInt(target.debut_year) || 0;
  if (gDebut === tDebut && gDebut > 0) {
    result.fields.debut = { status: FEEDBACK.CORRECT, value: gDebut };
  } else if (gDebut === 0 || tDebut === 0) {
    result.fields.debut = { status: FEEDBACK.WRONG, value: gDebut || '??' };
  } else if (gDebut < tDebut) {
    result.fields.debut = { status: FEEDBACK.HINT_UP, value: gDebut };
  } else {
    result.fields.debut = { status: FEEDBACK.HINT_DOWN, value: gDebut };
  }

  // Count total matches
  let correctCount = 0;
  let partialCount = 0;
  for (const key of ['id', 'age', 'region', 'team', 'champ', 'agent', 'nationality', 'debut']) {
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

  const fieldLabels = ['ID', '年龄', '赛区', '战队', '冠军', '英雄', '国籍', '出道'];
  const fieldKeys = ['id', 'age', 'region', 'team', 'champ', 'agent', 'nationality', 'debut'];

  for (const guess of guesses) {
    const line = fieldKeys.map(key => {
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
