/**
 * ui.js - UI rendering and interaction
 */

const UI = {
  currentInput: '',
  selectedSuggestion: -1,
};

function setupUI() {
  const input = document.getElementById('guess-input');
  const btn = document.getElementById('guess-btn');
  const autoComplete = document.getElementById('auto-complete');

  // Debounce timer for search input
  let debounceTimer = null;

  // Input handler with debounce
  input.addEventListener('input', function(e) {
    UI.currentInput = this.value;
    UI.selectedSuggestion = -1;
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(() => updateAutoComplete(this.value), 150);
    btn.disabled = this.value.trim().length === 0 || !DATA.loaded;
  });

  // Keydown for enter and arrow keys
  input.addEventListener('keydown', function(e) {
    const suggestions = autoComplete.querySelectorAll('.auto-item');
    if (e.key === 'Enter') {
      e.preventDefault();
      if (UI.selectedSuggestion >= 0 && suggestions[UI.selectedSuggestion]) {
        this.value = suggestions[UI.selectedSuggestion].textContent;
        autoComplete.innerHTML = '';
        btn.disabled = false;
      }
      submitGuess();
    } else if (e.key === 'ArrowDown') {
      e.preventDefault();
      UI.selectedSuggestion = Math.min(UI.selectedSuggestion + 1, suggestions.length - 1);
      updateSuggestionHighlight(suggestions);
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      UI.selectedSuggestion = Math.max(UI.selectedSuggestion - 1, -1);
      updateSuggestionHighlight(suggestions);
    } else if (e.key === 'Escape') {
      autoComplete.innerHTML = '';
      UI.selectedSuggestion = -1;
    }
  });

  // Button click
  btn.addEventListener('click', submitGuess);

  // Reveal answer button
  document.getElementById('reveal-btn').addEventListener('click', revealAnswer);

  // Handle input blur (hide suggestions after click)
  input.addEventListener('blur', function() {
    setTimeout(() => { autoComplete.innerHTML = ''; }, 200);
  });

  // Filter toggle
  document.getElementById('filter-toggle').addEventListener('click', function() {
    document.getElementById('filter-bar').classList.toggle('open');
    // Populate teams when first opened
    populateTeamFilter('');
  });

  // Welcome banner
  const welcomeBanner = document.getElementById('welcome-banner');
  if (welcomeBanner) {
    try {
      if (localStorage.getItem('welcomeDismissed')) {
        welcomeBanner.style.display = 'none';
      }
    } catch (e) {}
    document.getElementById('welcome-close').addEventListener('click', function() {
      welcomeBanner.style.display = 'none';
      try { localStorage.setItem('welcomeDismissed', '1'); } catch (e) {}
    });
  }

  // Region filter change → update team dropdown
  document.getElementById('filter-region').addEventListener('change', function() {
    populateTeamFilter(this.value);
    // Refresh auto-complete if there's input
    if (input.value.trim()) updateAutoComplete(input.value);
  });

  // Team filter change → refresh auto-complete
  document.getElementById('filter-team').addEventListener('change', function() {
    if (input.value.trim()) updateAutoComplete(input.value);
  });
}

function populateTeamFilter(regionFilter) {
  const select = document.getElementById('filter-team');
  const currentVal = select.value;
  const teams = getTeamsByRegion(regionFilter);
  select.innerHTML = '<option value="">全部战队</option>';
  teams.forEach(team => {
    const opt = document.createElement('option');
    opt.value = team;
    opt.textContent = team;
    select.appendChild(opt);
  });
  // Restore previous selection if still valid
  if (currentVal && teams.includes(currentVal)) {
    select.value = currentVal;
  }
}

function updateAutoComplete(query) {
  const container = document.getElementById('auto-complete');
  if (!query || query.length < 1) {
    container.innerHTML = '';
    return;
  }

  const regionFilter = document.getElementById('filter-region')?.value || '';
  const teamFilter = document.getElementById('filter-team')?.value || '';
  const results = searchPlayers(query, regionFilter, teamFilter);
  if (results.length === 0) {
    container.innerHTML = '';
    return;
  }

  container.innerHTML = results.map(name =>
    `<div class="auto-item" data-name="${name}">${name}</div>`
  ).join('');

  // Click handler for suggestions
  container.querySelectorAll('.auto-item').forEach(el => {
    el.addEventListener('click', function() {
      document.getElementById('guess-input').value = this.dataset.name;
      container.innerHTML = '';
      document.getElementById('guess-btn').disabled = false;
      document.getElementById('guess-input').focus();
    });
  });
}

function updateSuggestionHighlight(suggestions) {
  suggestions.forEach((el, i) => {
    el.style.background = i === UI.selectedSuggestion ? 'var(--bg-hover)' : '';
    el.style.color = i === UI.selectedSuggestion ? 'var(--text-primary)' : '';
    el.style.borderColor = i === UI.selectedSuggestion ? 'var(--accent-red)' : '';
  });
}

function submitGuess() {
  const input = document.getElementById('guess-input');
  const name = input.value.trim();

  if (!name || GAME.isOver || !DATA.loaded) return;
  if (!findPlayer(name)) {
    setHint(`❌ 未找到选手 "${name}"，请输入正确的选手 ID`);
    return;
  }

  // Check if already guessed (case-insensitive)
  if (GAME.guesses.some(g => g.guess.name.toLowerCase() === name.toLowerCase())) {
    setHint(`⚠️ 已经猜过 "${name}" 了，试试其他选手`);
    return;
  }

  const result = compareGuess(name);
  if (!result) return;

  addGuess(result);
  renderGuessRow(result);
  updateGuessCount();

  if (result.isWin) {
    setHint(`🎉 猜对了！共 ${GAME.guesses.length} 次`);
    disableInput(true);
    showWinModal(false);
    recordWin(GAME.guesses.length);
  } else if (GAME.isOver) {
    const t = GAME.targetPlayer;
    setHint(`😔 已达最大猜测次数 (${getMaxGuesses()} 次)，答案是 ${t.name}（${t.team_cn || t.team} · ${t.age}岁 · ${t.championships}冠）`);
    disableInput(true);
    showWinModal(true);
    recordLoss();
  } else {
    const remaining = getMaxGuesses() - GAME.guesses.length;
    const hint = getSmartHint(result);
    const pct = getExcludedPercent();
    setHint(`${hint}（剩余 ${remaining} 次${pct > 0 ? ` · 已排除约 ${pct}% 选手` : ''}）`);
  }

  input.value = '';
  input.focus();
  document.getElementById('auto-complete').innerHTML = '';
  document.getElementById('guess-btn').disabled = true;
}

/**
 * Render a single guess row in the history
 */
function renderGuessRow(result) {
  const container = document.getElementById('guess-history');
  const f = result.fields;
  const guess = result.guess;

  const row = document.createElement('div');
  row.className = 'guess-row';

  const idBadge = feedbackBadge(f.id.status, guess.name);
  row.innerHTML = `
    <div class="col col-id">${idBadge}</div>
    <div class="col col-age">${renderHintField(f.age)}</div>
    <div class="col col-region">${renderMultiField(f.region)}</div>
    <div class="col col-team">${renderMultiField(f.team)}</div>
    <div class="col col-champ">${renderHintField(f.champ)}</div>
    <div class="col col-hero">${renderAgentField(f.agent, guess)}</div>
    <div class="col col-nationality">${feedbackBadge(f.nationality.status, f.nationality.value)}</div>
    <div class="col col-debut">${renderHintField(f.debut)}</div>
  `;

  container.insertBefore(row, container.firstChild);
}

function feedbackBadge(status, text) {
  const cls = `badge badge-${status}`;
  return `<span class="${cls}">${text}</span>`;
}

// Unified hint field renderer (age, championships, debut year)
function renderHintField(field) {
  if (field.status === 'hint-up') {
    return `<span class="badge badge-hint-up">${field.value} 🔺</span>`;
  } else if (field.status === 'hint-down') {
    return `<span class="badge badge-hint-down">${field.value} 🔻</span>`;
  }
  return feedbackBadge(field.status, field.value);
}

// Unified multi-value field renderer (region, team)
function renderMultiField(field) {
  if (!field.items || field.items.length === 0) {
    return feedbackBadge(field.status, '未知');
  }
  let html = '<div class="multi-field">';
  html += '<div class="multi-list">';
  field.items.forEach(item => {
    const cls = item.matched ? 'badge badge-correct' : 'badge badge-wrong';
    html += `<span class="${cls}">${item.name_cn || item.name}</span>`;
  });
  html += '</div>';
  html += '</div>';
  return html;
}

function renderAgentField(field, guess) {
  const agents = field.value || [];
  const agentsCn = guess.agents_cn || [];
  const status = field.status;
  const matches = field.matches || [];

  let html = '<div class="agent-icons-row">';
  agents.forEach((agent, i) => {
    const iconPath = getAgentIconPath(agent);
    const cnName = agentsCn[i] || agent;
    const matched = matches[i]?.matched;
    const wrapClass = matched ? 'agent-icon-wrap matched' : (matched === false ? 'agent-icon-wrap unmatched' : 'agent-icon-wrap');
    const iconClass = matched ? 'agent-icon agent-icon-matched' : (matched === false ? 'agent-icon agent-icon-unmatched' : 'agent-icon');
    const title = matched ? `${cnName} ✓` : (matched === false ? `${cnName} ✗` : cnName);
    html += `<div class="${wrapClass}"><img src="${iconPath}" alt="${agent}" title="${title}" class="${iconClass}" onerror="this.parentElement.style.display='none'"></div>`;
  });

  // Fill empty slots
  for (let i = agents.length; i < 3; i++) {
    html += `<span class="badge badge-wrong">-</span>`;
  }

  // Status indicator — color only, no count text
  const badgeClass = status === 'correct' ? 'badge-correct'
    : status === 'partial' ? 'badge-partial' : 'badge-wrong';
  const label = status === 'correct' ? '✓'
    : status === 'partial' ? '~' : '✗';
  html += `<span class="badge ${badgeClass}" style="margin-left:4px;font-size:0.65rem;min-width:20px;padding:1px 5px">${label}</span>`;
  html += '</div>';

  return html;
}

function updateGuessCount() {
  const remaining = Math.max(0, getMaxGuesses() - GAME.guesses.length);
  document.getElementById('guess-count').textContent = `已猜 ${GAME.guesses.length} 次`;
  const remEl = document.getElementById('remaining-count');
  if (remaining > 0 && !GAME.isOver) {
    remEl.textContent = `剩余 ${remaining} 次`;
  } else if (GAME.isOver) {
    remEl.textContent = '游戏结束';
  } else {
    remEl.textContent = '';
  }
}

function disableInput(disabled) {
  const input = document.getElementById('guess-input');
  const btn = document.getElementById('guess-btn');
  const revealBtn = document.getElementById('reveal-btn');
  input.disabled = disabled;
  btn.disabled = disabled;
  if (revealBtn) revealBtn.disabled = disabled;
  input.placeholder = disabled ? '游戏已结束，刷新页面开始新一局' : '输入选手 ID... 如 ZmjjKK、f0rsakeN、TenZ';
}

function resetUI() {
  document.getElementById('guess-history').innerHTML = '';
  document.getElementById('win-modal').style.display = 'none';
  document.getElementById('share-section').style.display = 'none';
  document.getElementById('guess-input').value = '';
  document.getElementById('guess-input').disabled = false;
  document.getElementById('guess-input').placeholder = '输入选手 ID... 如 ZmjjKK、f0rsakeN、TenZ';
  document.getElementById('guess-btn').disabled = true;
  updateGuessCount();
  setHint(`🎯 已经选定目标选手，开始猜测吧！共 ${DATA.players.length} 名选手可选`);
}

function newGame() {
  resetGame();
  resetUI();
  document.getElementById('guess-input').focus();
  // Remove confetti canvas if present
  document.querySelectorAll('.confetti-canvas').forEach(c => c.remove());
}

function setHint(text) {
  document.getElementById('hint-text').textContent = text;
}

function getSmartHint(result) {
  const f = result.fields;
  const target = GAME.targetPlayer;
  const givenHints = GAME.hintsGiven || [];
  GAME.hintsGiven = givenHints;

  const hints = [];

  // Region (high priority — eliminates many players)
  if (f.region.status === 'wrong' && !givenHints.includes('region')) {
    hints.push({ text: `赛区不对，目标来自 ${REGION_CN[target.region] || target.region} 赛区`, key: 'region', priority: 10 });
  }

  // Team
  if (f.team.status === 'wrong' && !givenHints.includes('team') && result.guess.team) {
    const teamNames = [target.team_cn || target.team];
    if (target.previous_teams_cn) teamNames.push(...target.previous_teams_cn);
    hints.push({ text: `战队不对，目标曾效力 ${teamNames.join('、')}`, key: 'team', priority: 8 });
  }

  // Nationality
  if (f.nationality.status === 'wrong' && !givenHints.includes('nationality')) {
    const nat = target.nationality_cn || target.nationality;
    hints.push({ text: `国籍不对，目标来自 ${nat}`, key: 'nationality', priority: 7 });
  }

  // Age direction
  if (f.age.status === 'hint-up' && !givenHints.includes('age')) {
    hints.push({ text: `目标选手年龄更大（${target.age}岁左右）`, key: 'age', priority: 6 });
  } else if (f.age.status === 'hint-down' && !givenHints.includes('age')) {
    hints.push({ text: `目标选手年龄更小（${target.age}岁左右）`, key: 'age', priority: 6 });
  }

  // Championship direction
  if (f.champ.status === 'hint-up' && !givenHints.includes('champ')) {
    hints.push({ text: `目标冠军数更多（${target.championships}冠）`, key: 'champ', priority: 5 });
  } else if (f.champ.status === 'hint-down' && !givenHints.includes('champ')) {
    hints.push({ text: `目标冠军数更少（${target.championships}冠）`, key: 'champ', priority: 5 });
  }

  // Debut year direction
  if (f.debut.status === 'hint-up' && !givenHints.includes('debut')) {
    hints.push({ text: `目标出道更晚（${target.debut_year}年出道）`, key: 'debut', priority: 4 });
  } else if (f.debut.status === 'hint-down' && !givenHints.includes('debut')) {
    hints.push({ text: `目标出道更早（${target.debut_year}年出道）`, key: 'debut', priority: 4 });
  }

  // Agent partial match (lowest priority)
  if (f.agent.status === 'partial' && !givenHints.includes('agent')) {
    hints.push({ text: `代表英雄部分匹配（有 ${f.agent.matchCount}/3 个重叠）`, key: 'agent', priority: 3 });
  }

  // Sort by priority descending
  hints.sort((a, b) => b.priority - a.priority);

  if (hints.length > 0) {
    givenHints.push(hints[0].key);
    return '💡 ' + hints[0].text;
  }

  // Fallback hints from field-level comparisons
  targetFallbacks: {
    if (f.age.status === 'hint-up') { return '💡 目标选手年龄更大'; break targetFallbacks; }
    if (f.age.status === 'hint-down') { return '💡 目标选手年龄更小'; break targetFallbacks; }
    if (f.champ.status === 'hint-up') { return '💡 目标冠军数更多'; break targetFallbacks; }
    if (f.champ.status === 'hint-down') { return '💡 目标冠军数更少'; break targetFallbacks; }
    if (f.debut.status === 'hint-up') { return '💡 目标出道更晚'; break targetFallbacks; }
    if (f.debut.status === 'hint-down') { return '💡 目标出道更早'; break targetFallbacks; }
    if (f.agent.status === 'partial') { return '💡 代表英雄部分匹配，注意共同英雄'; break targetFallbacks; }
  }

  return '💡 换个方向试试！';
}

// Estimate how many players are excluded based on current feedback
function getExcludedPercent() {
  const total = DATA.players.length;
  if (total === 0 || GAME.guesses.length === 0) return 0;
  const lastResult = GAME.guesses[GAME.guesses.length - 1];
  if (!lastResult) return 0;

  // Simple heuristic: count fields that are WRONG (eliminates all players sharing that value)
  // and HINT_UP/HINT_DOWN (eliminates players on the wrong side)
  const target = GAME.targetPlayer;
  let remaining = total;

  // Age elimination
  const f = lastResult.fields;
  if (f.age.status === 'wrong' && target.age !== '' && lastResult.guess.age !== '') {
    remaining = Math.max(1, remaining - Math.floor(remaining * 0.15));
  }

  return Math.round((1 - remaining / total) * 100);
}

/* ===== Reveal / Give Up ===== */

function revealAnswer() {
  if (GAME.isOver) return;
  if (!confirm('确定要揭晓答案吗？揭晓后本局游戏将结束。')) return;

  GAME.isOver = true;
  disableInput(true);
  const t = GAME.targetPlayer;
  setHint(`😔 答案是 ${t.name}（${t.team_cn || t.team} · ${t.age}岁 · ${t.championships}冠）`);
  showWinModal(true);
  recordLoss();
}

/* ===== Win Modal Outside Close ===== */

function closeWinModalOutside(event) {
  if (event.target === event.currentTarget) {
    document.getElementById('win-modal').style.display = 'none';
    document.getElementById('share-section').style.display = 'flex';
  }
}

/* ===== Confetti Celebration ===== */

function spawnConfetti() {
  // Remove existing confetti canvas
  document.querySelectorAll('.confetti-canvas').forEach(c => c.remove());

  const canvas = document.createElement('canvas');
  canvas.className = 'confetti-canvas';
  canvas.style.cssText = 'position:fixed;top:0;left:0;width:100%;height:100%;pointer-events:none;z-index:9999;';
  document.body.appendChild(canvas);

  const ctx = canvas.getContext('2d');
  const W = canvas.width = canvas.offsetWidth;
  const H = canvas.height = canvas.offsetHeight;
  const colors = ['#ff4655', '#3fb58a', '#f5b748', '#4a9eff', '#ff6b4a', '#ece8e1', '#a0a8b4'];
  const pieces = [];

  for (let i = 0; i < 120; i++) {
    pieces.push({
      x: Math.random() * W,
      y: Math.random() * H - H,
      w: Math.random() * 8 + 4,
      h: Math.random() * 6 + 3,
      color: colors[Math.floor(Math.random() * colors.length)],
      rotation: Math.random() * 360,
      rotSpeed: (Math.random() - 0.5) * 8,
      speedX: (Math.random() - 0.5) * 3,
      speedY: Math.random() * 4 + 2,
      opacity: 1,
      swing: Math.random() * 2 - 1,
    });
  }

  let frame = 0;
  const MAX_FRAMES = 180;

  function animate() {
    frame++;
    if (frame > MAX_FRAMES) {
      canvas.style.opacity = Math.max(0, parseFloat(canvas.style.opacity || 1) - 0.05);
      if (parseFloat(canvas.style.opacity || 1) <= 0) {
        canvas.remove();
        return;
      }
    }
    ctx.clearRect(0, 0, W, H);
    for (const p of pieces) {
      p.x += p.speedX + Math.sin(frame * 0.05 + p.swing) * 0.5;
      p.y += p.speedY;
      p.rotation += p.rotSpeed;
      ctx.save();
      ctx.translate(p.x, p.y);
      ctx.rotate((p.rotation * Math.PI) / 180);
      ctx.globalAlpha = p.opacity;
      ctx.fillStyle = p.color;
      ctx.fillRect(-p.w / 2, -p.h / 2, p.w, p.h);
      ctx.restore();
    }
    requestAnimationFrame(animate);
  }
  animate();
}

function showWinModal(revealed) {
  const modal = document.getElementById('win-modal');
  const target = GAME.targetPlayer;

  // Set animation class
  modal.className = 'modal-overlay' + (revealed ? ' modal-lose' : ' modal-win');

  document.getElementById('modal-title').textContent = revealed ? '😔 游戏结束' : '🎉 恭喜猜中！';

  // Trigger confetti on win
  if (!revealed) spawnConfetti();
  document.getElementById('modal-player').textContent = target.name;
  document.getElementById('modal-stats').innerHTML =
    `${target.team_cn || target.team} · ${REGION_CN[target.region] || target.region} · ${target.age}岁 · ${target.championships}冠`;

  // Full answer detail with all fields
  const nat = target.nationality_cn || target.nationality || '未知';
  const debut = target.debut_year || '未知';
  const allTeams = [target.team];
  if (target.previous_teams) allTeams.push(...target.previous_teams);
  const allRegions = [target.region];
  if (target.previous_regions) allRegions.push(...target.previous_regions);
  const teamCnMap = {};
  teamCnMap[target.team] = target.team_cn || target.team;
  (target.previous_teams_cn || []).forEach((cn, i) => {
    teamCnMap[target.previous_teams[i]] = cn;
  });

  document.getElementById('modal-answer-detail').innerHTML = `
    <div class="answer-grid">
      <div class="answer-item">
        <span class="answer-label">国籍</span>
        <span class="answer-value">${nat}</span>
      </div>
      <div class="answer-item">
        <span class="answer-label">出道年</span>
        <span class="answer-value">${debut}</span>
      </div>
      <div class="answer-item">
        <span class="answer-label">年龄</span>
        <span class="answer-value">${target.age || '??'}岁</span>
      </div>
      <div class="answer-item">
        <span class="answer-label">冠军数</span>
        <span class="answer-value">${target.championships || 0}冠</span>
      </div>
      <div class="answer-item">
        <span class="answer-label">所有赛区</span>
        <span class="answer-value">${allRegions.map(r => REGION_CN[r] || r).join(' → ')}</span>
      </div>
      <div class="answer-item answer-item-full">
        <span class="answer-label">所有战队</span>
        <span class="answer-value">${allTeams.map(t => teamCnMap[t] || t).join(' → ')}</span>
      </div>
      <div class="answer-item answer-item-full">
        <span class="answer-label">代表英雄</span>
        <span class="answer-value">${(target.agents_cn || target.agents || []).join(' · ')}</span>
      </div>
    </div>
  `;

  // Generate result grid
  const emojiMap = {
    'correct': '🟩', 'partial': '🟨', 'wrong': '⬛',
    'hint-up': '🔺', 'hint-down': '🔻',
  };
  const fieldKeys = ['id', 'age', 'region', 'team', 'champ', 'agent', 'nationality', 'debut'];

  let resultHtml = '';
  GAME.guesses.forEach(g => {
    fieldKeys.forEach(key => {
      const emoji = emojiMap[g.fields[key].status] || '⬜';
      resultHtml += `<span class="result-block">${emoji}</span>`;
    });
    resultHtml += '<br>';
  });

  document.getElementById('modal-result').innerHTML = resultHtml;
  modal.style.display = 'flex';

  document.getElementById('share-section').style.display = 'flex';
}

function shareResult() {
  const text = generateShareText();
  navigator.clipboard.writeText(text).then(() => {
    showToast('📋 已复制到剪贴板！');
  }).catch(() => {
    showToast('📋 复制失败，请手动复制');
  });
}

function showToast(message) {
  const existing = document.querySelector('.toast');
  if (existing) existing.remove();

  const toast = document.createElement('div');
  toast.className = 'toast';
  toast.textContent = message;
  document.body.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transition = 'opacity 0.3s ease';
    setTimeout(() => toast.remove(), 300);
  }, 2500);
}

/* ===== Settings Panel ===== */

function openSettings() {
  const modal = document.getElementById('settings-modal');
  const slider = document.getElementById('max-guesses-slider');
  const display = document.getElementById('max-guesses-display');
  const note = document.getElementById('max-guesses-note');

  slider.value = getMaxGuesses();
  display.textContent = getMaxGuesses();
  note.textContent = getMaxGuessesNote(getMaxGuesses());

  // Update stats
  const stats = loadStats();
  document.getElementById('stat-games').textContent = stats.gamesPlayed;
  document.getElementById('stat-winrate').textContent = getWinRate();
  document.getElementById('stat-streak').textContent = stats.currentStreak;
  document.getElementById('stat-best').textContent = stats.bestStreak;

  modal.style.display = 'flex';
}

function closeSettings() {
  document.getElementById('settings-modal').style.display = 'none';
}

function closeSettingsOutside(event) {
  if (event.target === event.currentTarget) {
    closeSettings();
  }
}

function onMaxGuessesChange(val) {
  const num = parseInt(val);
  document.getElementById('max-guesses-display').textContent = num;
  document.getElementById('max-guesses-note').textContent = getMaxGuessesNote(num);
  setMaxGuesses(num);
  updateGuessCount();
  // Update hint if game is not over
  if (!GAME.isOver && GAME.guesses.length > 0) {
    const remaining = Math.max(0, getMaxGuesses() - GAME.guesses.length);
    setHint(`⚙️ 已调整最大猜测次数为 ${getMaxGuesses()}，剩余 ${remaining} 次`);
  }
}

function getMaxGuessesNote(n) {
  if (n >= 15) return `当前设置：共 ${n} 次，适合轻松休闲`;
  if (n <= 5) return `当前设置：共 ${n} 次，挑战模式！`;
  return `当前设置：共 ${n} 次猜测机会`;
}

/* ===== Feedback Functions ===== */

function openFeedback() {
  const modal = document.getElementById('feedback-modal');
  modal.style.display = 'flex';

  // Pre-fill player input with target if game is active
  const playerInput = document.getElementById('feedback-player');
  if (GAME && GAME.targetPlayer) {
    playerInput.value = GAME.targetPlayer.name;
  } else {
    playerInput.value = '';
  }

  // Setup auto-complete for player input
  playerInput.addEventListener('input', function() {
    const container = document.getElementById('feedback-suggest');
    const query = this.value.trim();
    if (!query || query.length < 1) {
      container.innerHTML = '';
      return;
    }
    const results = searchPlayers(query, '', '');
    if (results.length === 0) {
      container.innerHTML = '';
      return;
    }
    container.innerHTML = results.map(name =>
      `<div class="auto-item" data-name="${name}">${name}</div>`
    ).join('');
    container.querySelectorAll('.auto-item').forEach(el => {
      el.addEventListener('click', function() {
        document.getElementById('feedback-player').value = this.dataset.name;
        container.innerHTML = '';
      });
    });
  });

  // Clear other fields
  document.getElementById('feedback-field').value = '';
  document.getElementById('feedback-correct').value = '';
  document.getElementById('feedback-note').value = '';
}

function closeFeedback() {
  document.getElementById('feedback-modal').style.display = 'none';
  document.getElementById('feedback-suggest').innerHTML = '';
}

function closeFeedbackOutside(event) {
  if (event.target === event.currentTarget) {
    closeFeedback();
  }
}

function submitFeedback() {
  const player = document.getElementById('feedback-player').value.trim();
  const field = document.getElementById('feedback-field').value;
  const correct = document.getElementById('feedback-correct').value.trim();
  const note = document.getElementById('feedback-note').value.trim();

  // Validate required fields
  if (!player) {
    showToast('⚠️ 请填写选手 ID');
    document.getElementById('feedback-player').focus();
    return;
  }
  if (!field) {
    showToast('⚠️ 请选择错误字段');
    return;
  }
  if (!correct) {
    showToast('⚠️ 请描述正确信息');
    document.getElementById('feedback-correct').focus();
    return;
  }

  // Map field value to Chinese label
  const fieldLabels = {
    'age': '年龄',
    'region': '赛区',
    'team': '战队',
    'championships': '冠军数',
    'agents': '代表英雄',
    'other': '其他',
  };

  const title = encodeURIComponent(`[数据反馈] ${player} - ${fieldLabels[field] || field}`);
  const body = encodeURIComponent(
    `## 选手信息\n- **选手 ID**：${player}\n- **错误字段**：${fieldLabels[field] || field}\n\n` +
    `## 正确信息\n${correct}\n\n` +
    (note ? `## 补充说明\n${note}\n\n` : '') +
    `---\n*由 VCT 猜选手游戏反馈功能提交*`
  );

  const url = `https://github.com/qianmeng123456/VALORANT-pro-guess/issues/new?title=${title}&body=${body}`;

  // Open GitHub Issues in new tab
  window.open(url, '_blank');
  showToast('✅ 已跳转到 GitHub，请确认提交 Issue');
  closeFeedback();
}

// Close settings modal with Escape key
document.addEventListener('keydown', function(e) {
  if (e.key === 'Escape') {
    const settingsModal = document.getElementById('settings-modal');
    if (settingsModal.style.display === 'flex') {
      closeSettings();
      return;
    }
    const feedbackModal = document.getElementById('feedback-modal');
    if (feedbackModal.style.display === 'flex') {
      closeFeedback();
      return;
    }
  }

  // Press "/" or "。" to focus the guess input (only when not in a modal or input)
  if ((e.key === '/' || e.key === '。') && !GAME.isOver) {
    const active = document.activeElement;
    if (active && (active.tagName === 'INPUT' || active.tagName === 'TEXTAREA')) return;
    const settingsModal = document.getElementById('settings-modal');
    if (settingsModal.style.display === 'flex') return;
    e.preventDefault();
    document.getElementById('guess-input').focus();
  }
});
