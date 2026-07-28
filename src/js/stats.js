/**
 * stats.js - Game statistics with localStorage persistence
 * Tracks wins, streaks, and guess distribution across sessions.
 */

const STATS_KEY = 'vct_guess_stats';

const DEFAULT_STATS = {
  gamesPlayed: 0,
  gamesWon: 0,
  gamesLost: 0,
  currentStreak: 0,
  bestStreak: 0,
  guessDistribution: {},
  lastPlayedDate: '',
  history: [],
};

function loadStats() {
  try {
    const raw = localStorage.getItem(STATS_KEY);
    if (raw) {
      return { ...DEFAULT_STATS, ...JSON.parse(raw) };
    }
  } catch (e) {}
  return { ...DEFAULT_STATS };
}

function saveStats(stats) {
  try {
    localStorage.setItem(STATS_KEY, JSON.stringify(stats));
  } catch (e) {}
}

function recordWin(guessCount) {
  const stats = loadStats();
  const today = getLocalDateString();

  stats.gamesPlayed++;
  stats.gamesWon++;
  stats.currentStreak++;
  if (stats.currentStreak > stats.bestStreak) {
    stats.bestStreak = stats.currentStreak;
  }

  // Only count once per day (prevent double-count on refresh)
  if (stats.lastPlayedDate !== today) {
    const key = String(guessCount);
    stats.guessDistribution[key] = (stats.guessDistribution[key] || 0) + 1;
    stats.lastPlayedDate = today;

    stats.history.unshift({
      date: today,
      guesses: guessCount,
      won: true,
    });
    if (stats.history.length > 50) stats.history.length = 50;
  }

  saveStats(stats);
}

function recordLoss() {
  const stats = loadStats();
  const today = getLocalDateString();

  stats.gamesPlayed++;
  stats.gamesLost++;
  stats.currentStreak = 0;

  if (stats.lastPlayedDate !== today) {
    stats.lastPlayedDate = today;

    stats.history.unshift({
      date: today,
      guesses: 0,
      won: false,
    });
    if (stats.history.length > 50) stats.history.length = 50;
  }

  saveStats(stats);
}

function getWinRate() {
  const stats = loadStats();
  if (stats.gamesPlayed === 0) return '0%';
  return Math.round((stats.gamesWon / stats.gamesPlayed) * 100) + '%';
}

function getLocalDateString() {
  const d = new Date();
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;
}
