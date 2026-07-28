/**
 * main.js - Entry point
 * Initializes the game when the page loads
 */

async function init() {
  // Load player data
  const loaded = await loadPlayerData();
  if (!loaded) return;

  // Initialize game with target player
  const target = initGame();
  console.log(`🎯 Today's target: ${target.name} (${target.team})`);

  // Set up UI handlers
  setupUI();

  // Enable input
  document.getElementById('guess-input').disabled = false;
  document.getElementById('guess-btn').disabled = true;

  // Update hint
  setHint(`🎯 已经选定目标选手，开始猜测吧！共 ${DATA.players.length} 名选手可选`);

  // Show remaining guesses
  updateGuessCount();
}

// Start the game when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', init);
} else {
  init();
}

// Expose functions globally for onclick handlers
window.shareResult = shareResult;
window.openSettings = openSettings;
window.closeSettings = closeSettings;
window.closeSettingsOutside = closeSettingsOutside;
window.onMaxGuessesChange = onMaxGuessesChange;
