(() => {
  'use strict';
  const cfg = window.TARDevHub || {};
  const $ = (id) => document.getElementById(id);
  const state = { status: null, preview: null, action: null, repos: [] };

  const log = (message, type = 'info') => {
    const terminal = $('tar-terminal');
    if (!terminal) return;
    const row = document.createElement('div');
    row.className = `tar-log tar-log--${type}`;
    const time = new Date().toLocaleTimeString('en-GB', { hour12: false });
    row.textContent = `[${time}] ${message}`;
    terminal.appendChild(row);
    terminal.scrollTop = terminal.scrollHeight;
  };

  const busy = (value, step = '') => {
    document.querySelectorAll('.tar-action, #tar-connect, #tar-save-selection, #tar-disconnect, #tar-refresh-repos, #tar-refresh-branches, #tar-init-git, #tar-execute').forEach((el) => {
      if (value) {
        el.dataset.wasDisabled = el.disabled ? '1' : '0';
        el.disabled = true;
      } else if (el.dataset.wasDisabled !== '1') {
        el.disabled = false;
      }
      if (!value) delete el.dataset.wasDisabled;
    });
    const wrap = $('tar-progress-wrap');
    if (wrap) wrap.hidden = !value;
    if (value) {
      $('tar-progress-bar').style.width = '65%';
      $('tar-current-step').textContent = step || 'Working…';
    } else {
      $('tar-progress-bar').style.width = '100%';
      setTimeout(() => { if (wrap) wrap.hidden = true; }, 250);
    }
  };

  async function api(path, options = {}) {
    const response = await fetch(cfg.rest + path, {
      credentials: 'same-origin',
      ...options,
      headers: {
        'Content-Type': 'application/json',
        'X-WP-Nonce': cfg.nonce,
        ...(options.headers || {}),
      },
    });
    const data = await response.json().catch(() => ({}));
    if (!response.ok) {
      const error = new Error(data.message || data.code || `Request failed (${response.status})`);
      error.data = data.data || {};
      throw error;
    }
    return data;
  }

  function setBadge(el, text, kind = '') {
    el.textContent = text;
    el.className = `tar-badge${kind ? ` tar-badge--${kind}` : ''}`;
  }

  function renderStatus(status) {
    state.status = status;
    $('tar-stat-branch').textContent = status.branch || '—';
    $('tar-stat-sha').textContent = status.shortSha || '—';
    $('tar-stat-dirty').textContent = status.gitAvailable ? (status.isDirty ? 'Changes detected' : 'Clean') : 'Unavailable';
    $('tar-stat-git').textContent = status.gitAvailable ? 'Ready' : 'Not initialized';
    $('tar-repo-path').textContent = status.repoPath || '—';
    $('tar-saved-repo').textContent = status.githubRepo || '—';
    $('tar-saved-branch').textContent = status.githubBranch || '—';
    $('tar-git-init-box').hidden = !!status.gitAvailable;
    const connection = $('tar-connection-badge');
    if (status.githubConnectionStatus === 'verified') setBadge(connection, 'Connected', 'success');
    else if (status.githubConnectionStatus === 'incomplete') setBadge(connection, 'Connected · select repo', 'warning');
    else setBadge(connection, 'Disconnected', 'muted');
    const login = $('tar-login-badge');
    if (status.githubLogin) {
      login.hidden = false;
      login.textContent = `@${status.githubLogin}`;
    } else login.hidden = true;
    $('tar-token').placeholder = status.githubTokenSet ? '••••••••••••••••' : 'github_pat_...';
    if (status.githubRepo && [...$('tar-repo').options].some((o) => o.value === status.githubRepo)) $('tar-repo').value = status.githubRepo;
    if (status.githubBranch && [...$('tar-branch').options].some((o) => o.value === status.githubBranch)) $('tar-branch').value = status.githubBranch;
  }

  async function loadStatus() {
    const status = await api('status', { method: 'GET', headers: {} });
    renderStatus(status);
    return status;
  }

  async function loadRepos(preferred = '') {
    const data = await api('github/repos', { method: 'GET', headers: {} });
    state.repos = data.repositories || [];
    const select = $('tar-repo');
    const wanted = preferred || select.value || state.status?.githubRepo || '';
    select.innerHTML = '<option value="">Select repository</option>';
    state.repos.forEach((repo) => {
      const option = document.createElement('option');
      option.value = repo.fullName;
      option.textContent = `${repo.fullName}${repo.private ? ' • Private' : ''}`;
      select.appendChild(option);
    });
    if ([...select.options].some((o) => o.value === wanted)) select.value = wanted;
    if (select.value) await loadBranches(select.value, state.status?.githubBranch || '');
  }

  async function loadBranches(repo = $('tar-repo').value, preferred = '') {
    if (!repo) return;
    const data = await api(`github/branches?repo=${encodeURIComponent(repo)}`, { method: 'GET', headers: {} });
    const select = $('tar-branch');
    const wanted = preferred || select.value || '';
    select.innerHTML = '<option value="">Select branch</option>';
    (data.branches || []).forEach((branch) => {
      const option = document.createElement('option');
      option.value = branch;
      option.textContent = branch;
      select.appendChild(option);
    });
    if ([...select.options].some((o) => o.value === wanted)) select.value = wanted;
  }

  function renderPreview(preview) {
    state.preview = preview;
    $('tar-review-card').hidden = false;
    $('tar-sync-state').textContent = (preview.syncState || 'not_reviewed').replaceAll('_', ' ');
    $('tar-local-ahead').textContent = String(preview.localAhead ?? 0);
    $('tar-remote-ahead').textContent = String(preview.remoteAhead ?? 0);
    $('tar-review-summary').textContent = `${preview.fileCount || 0} file(s) reviewed · expected action: ${(preview.expectedAction || 'noop').replaceAll('_', ' ')}`;
    const blockers = $('tar-blockers');
    blockers.innerHTML = '';
    (preview.blocked || []).forEach((item) => {
      const row = document.createElement('div');
      row.className = 'tar-alert tar-alert--danger';
      const strong = document.createElement('strong');
      strong.textContent = item.path;
      const text = document.createElement('span');
      text.textContent = ` — ${item.reason}`;
      row.append(strong, text);
      blockers.appendChild(row);
    });
    const tbody = $('tar-review-files');
    tbody.innerHTML = '';
    (preview.files || []).forEach((file) => {
      const tr = document.createElement('tr');
      [file.status || 'M', file.path || '', file.direction || 'local'].forEach((value) => {
        const td = document.createElement('td');
        td.textContent = value;
        tr.appendChild(td);
      });
      tbody.appendChild(tr);
    });
    $('tar-execute').disabled = !!(preview.blocked || []).length || preview.expectedAction === 'blocked';
  }

  async function review(action) {
    busy(true, `Reviewing ${action} safely…`);
    state.action = action;
    state.preview = null;
    log(`Secure ${action} review started.`);
    try {
      const data = await api('git/preview', { method: 'POST', body: JSON.stringify({ action }) });
      renderPreview(data.preview);
      if ((data.preview.blocked || []).length) log(`Review blocked by ${data.preview.blocked.length} safety finding(s).`, 'warning');
      else log(`Review complete. Expected action: ${data.preview.expectedAction}.`, 'success');
      $('tar-current-step').textContent = 'Review completed.';
    } catch (error) {
      log(error.message, 'error');
      $('tar-current-step').textContent = error.message;
    } finally {
      busy(false);
      if (state.preview && !(state.preview.blocked || []).length) $('tar-execute').disabled = false;
    }
  }

  async function execute() {
    if (!state.preview || !state.action) return;
    const action = state.action;
    busy(true, `Executing reviewed ${action}…`);
    log(`Executing reviewed ${action} action.`);
    try {
      const data = await api('git/execute', {
        method: 'POST',
        body: JSON.stringify({
          action,
          fingerprint: state.preview.fingerprint,
          message: $('tar-commit-message').value.trim(),
        }),
      });
      (data.logs || []).forEach((entry) => log(entry.message, entry.type || 'info'));
      log(data.message || 'Operation completed.', 'success');
      $('tar-current-step').textContent = data.message || 'Operation completed successfully.';
      state.preview = null;
      $('tar-review-card').hidden = true;
      await loadStatus();
    } catch (error) {
      log(error.message, 'error');
      $('tar-current-step').textContent = error.message;
      state.preview = null;
      $('tar-execute').disabled = true;
    } finally {
      busy(false);
    }
  }

  async function boot() {
    try {
      const status = await loadStatus();
      log('Developer Hub loaded.', 'success');
      if (status.githubTokenSet) {
        try { await loadRepos(status.githubRepo || ''); } catch (e) { log(e.message, 'warning'); }
      }
    } catch (error) {
      log(error.message, 'error');
    }
  }

  $('tar-toggle-token')?.addEventListener('click', () => {
    const input = $('tar-token');
    input.type = input.type === 'password' ? 'text' : 'password';
    $('tar-toggle-token').textContent = input.type === 'password' ? 'Show' : 'Hide';
  });

  $('tar-connect')?.addEventListener('click', async () => {
    const token = $('tar-token').value.trim();
    if (!token) return log('Enter a GitHub token first.', 'warning');
    busy(true, 'Verifying GitHub account…');
    try {
      const data = await api('github/connect', { method: 'POST', body: JSON.stringify({ token }) });
      $('tar-token').value = '';
      log(`GitHub account @${data.login} verified.`, 'success');
      await loadStatus();
      await loadRepos();
    } catch (error) { log(error.message, 'error'); }
    finally { busy(false); }
  });

  $('tar-refresh-repos')?.addEventListener('click', async () => {
    try { busy(true, 'Loading repositories…'); await loadRepos(); log('Repositories refreshed.', 'success'); }
    catch (e) { log(e.message, 'error'); } finally { busy(false); }
  });

  $('tar-repo')?.addEventListener('change', async (event) => {
    state.preview = null;
    $('tar-review-card').hidden = true;
    try { await loadBranches(event.target.value, ''); } catch (e) { log(e.message, 'error'); }
  });

  $('tar-refresh-branches')?.addEventListener('click', async () => {
    try { busy(true, 'Loading branches…'); await loadBranches(); log('Branches refreshed.', 'success'); }
    catch (e) { log(e.message, 'error'); } finally { busy(false); }
  });

  $('tar-save-selection')?.addEventListener('click', async () => {
    const repo = $('tar-repo').value;
    const branch = $('tar-branch').value;
    if (!repo || !branch) return log('Select a repository and branch.', 'warning');
    try {
      busy(true, 'Saving repository selection…');
      await api('github/selection', { method: 'POST', body: JSON.stringify({ repo, branch }) });
      log(`Saved ${repo} @ ${branch}.`, 'success');
      await loadStatus();
    } catch (e) { log(e.message, 'error'); } finally { busy(false); }
  });

  $('tar-disconnect')?.addEventListener('click', async () => {
    try {
      busy(true, 'Disconnecting GitHub…');
      await api('github/disconnect', { method: 'DELETE', body: '{}' });
      $('tar-repo').innerHTML = '<option value="">Select repository</option>';
      $('tar-branch').innerHTML = '<option value="">Select branch</option>';
      log('GitHub disconnected.', 'success');
      await loadStatus();
    } catch (e) { log(e.message, 'error'); } finally { busy(false); }
  });

  $('tar-init-git')?.addEventListener('click', async () => {
    if (!window.confirm('Initialize Git in the configured project root? This writes .git metadata and Developer Hub safety rules.')) return;
    try {
      busy(true, 'Initializing Git repository…');
      await api('git/init', { method: 'POST', body: '{}' });
      log('Local Git repository initialized.', 'success');
      await loadStatus();
    } catch (e) { log(e.message, 'error'); } finally { busy(false); }
  });

  document.querySelectorAll('.tar-action').forEach((button) => button.addEventListener('click', () => review(button.dataset.action)));
  $('tar-execute')?.addEventListener('click', execute);
  $('tar-clear-log')?.addEventListener('click', () => { $('tar-terminal').innerHTML = ''; });
  boot();
})();
