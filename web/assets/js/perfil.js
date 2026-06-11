/* ════════════════════════════════════════
   MODAL DE PERFIL — LogiStock
════════════════════════════════════════ */
const P_KEY = 'logistock_profile_accounts';

function pLoadAccounts() {
  try { const r = localStorage.getItem(P_KEY); return r ? JSON.parse(r) : pDefault(); }
  catch { return pDefault(); }
}
function pDefault() {
  const email = localStorage.getItem('usuarioLogado') || 'usuario';
  const nome = email.includes('@') ? email.split('@')[0] : email;
  const initials = nome.slice(0,2).toUpperCase();
  return [
    {
      id: 1, name: nome.charAt(0).toUpperCase() + nome.slice(1),
      role: 'Usuário LogiStock', email: email.includes('@') ? email : email + '@logistock.com',
      matricula: 'LOG-000001', cargo: 'Usuário', setor: 'Logística',
      initials: initials, photo: null, active: true
    }
  ];
}
function pSave(acc) { localStorage.setItem(P_KEY, JSON.stringify(acc)); }
function pGetActive() { return pAccounts.find(a => a.active) || pAccounts[0]; }

let pAccounts = pLoadAccounts();

/* Sync header name */
function pSyncHeader() {
  const acc = pGetActive();
  document.querySelectorAll('.nome-perfil-header').forEach(el => el.textContent = acc.name);
  document.querySelectorAll('.nome-perfil-menu').forEach(el => el.textContent = acc.name);
}
document.addEventListener('DOMContentLoaded', pSyncHeader);

/* ── Open / Close ── */
function openProfileModal() {
  pLoadForm();
  pRenderAccounts();
  document.getElementById('overlay-profile').classList.add('open');
  document.querySelectorAll('.ptab-btn').forEach((b, i) => b.classList.toggle('active', i === 0));
  document.querySelectorAll('.ptab-panel').forEach((p, i) => p.classList.toggle('active', i === 0));
  pCloseChangePw();
}
function closeProfileModal() {
  document.getElementById('overlay-profile').classList.remove('open');
}
function pHandleOverlay(e) {
  if (e.target === document.getElementById('overlay-profile')) closeProfileModal();
}

/* ── Tabs ── */
function pSwitchTab(id, btn) {
  document.querySelectorAll('.ptab-btn').forEach(b => b.classList.remove('active'));
  document.querySelectorAll('.ptab-panel').forEach(p => p.classList.remove('active'));
  btn.classList.add('active');
  document.getElementById('ptab-' + id).classList.add('active');
}

/* ── Load form ── */
function pLoadForm() {
  const acc = pGetActive();
  document.getElementById('pedit-name').value     = acc.name;
  document.getElementById('pedit-email').value    = acc.email;
  document.getElementById('pedit-matricula').value = acc.matricula;
  document.getElementById('pedit-cargo').value    = acc.cargo;
  document.getElementById('pedit-setor').value    = acc.setor;
  document.getElementById('pheader-name').textContent  = acc.name;
  document.getElementById('pheader-role').textContent  = acc.role;
  document.getElementById('pheader-email').textContent = acc.email;
  pRenderAvLg(document.getElementById('pprofile-av'), acc);
}

function pRenderAvLg(el, acc) {
  el.className = 'pav-lg';
  if (acc.photo) { el.innerHTML = `<img src="${acc.photo}" alt="">`; }
  else { el.textContent = acc.initials; }
}
function pRenderAvSm(el, acc) {
  el.className = 'pav-sm';
  if (acc.photo) { el.innerHTML = `<img src="${acc.photo}" alt="">`; }
  else { el.textContent = acc.initials; }
}

/* ── Photo ── */
function pTriggerPhoto() { document.getElementById('pphoto-input').click(); }
function pHandlePhoto(e) {
  const f = e.target.files[0]; if (!f) return;
  const r = new FileReader();
  r.onload = ev => {
    const acc = pGetActive();
    acc.photo = ev.target.result;
    pSave(pAccounts);
    pLoadForm();
    pRenderAccounts();
    logiToast('Foto atualizada!', 'success');
  };
  r.readAsDataURL(f);
}

/* ── Save profile ── */
function pSaveProfile() {
  const name  = document.getElementById('pedit-name').value.trim();
  const email = document.getElementById('pedit-email').value.trim();
  if (!name) { logiToast('O nome não pode ficar vazio.', 'error'); return; }
  if (!email.includes('@')) { logiToast('E-mail inválido.', 'error'); return; }
  const acc = pGetActive();
  acc.name  = name;
  acc.email = email;
  const parts = name.split(' ').filter(Boolean);
  acc.initials = (parts[0][0] + (parts[1]?.[0] || '')).toUpperCase();
  pSave(pAccounts);
  pLoadForm();
  pSyncHeader();
  pRenderAccounts();
  logiToast('Perfil salvo com sucesso!', 'success');
}
function pCancelEdit() { pLoadForm(); }

/* ── Accounts ── */
function pRenderAccounts() {
  const list = document.getElementById('paccounts-list');
  list.innerHTML = '';
  pAccounts.forEach(acc => {
    const div = document.createElement('div');
    div.className = 'paccount-item' + (acc.active ? ' pcurrent' : '');
    const av = document.createElement('div');
    pRenderAvSm(av, acc);
    div.innerHTML = `
      <div class="pacc-info">
        <div class="pacc-name">${acc.name}</div>
        <div class="pacc-sub">${acc.email}</div>
      </div>
      ${acc.active ? '<span class="pacc-badge">Ativa</span>' : ''}
      ${!acc.active ? `<button class="pacc-remove" title="Remover" onclick="pRemoveAcc(event,${acc.id})"><i class="fa-solid fa-xmark"></i></button>` : ''}
    `;
    div.insertBefore(av, div.firstChild);
    if (!acc.active) div.addEventListener('click', () => pSwitchToAcc(acc.id));
    list.appendChild(div);
  });
}
function pSwitchToAcc(id) {
  pAccounts.forEach(a => a.active = (a.id === id));
  pSave(pAccounts);
  pLoadForm(); pSyncHeader(); pRenderAccounts();
  logiToast('Conta alterada!', 'success');
}
function pRemoveAcc(e, id) {
  e.stopPropagation();
  pAccounts = pAccounts.filter(a => a.id !== id);
  pSave(pAccounts);
  pRenderAccounts();
  logiToast('Conta removida.');
}
function pGoToLogin() {
  logiToast('Redirecionando para o login…');
  setTimeout(() => { closeProfileModal(); }, 1200);
}

/* ── Logout ── */
function pConfirmLogout() {
  logiToast('Saindo da conta…');
  setTimeout(() => {
    localStorage.removeItem('usuarioLogado');
    closeProfileModal();
    window.location.href = '../../index.html';
  }, 1200);
}

/* ── Change password ── */
function pOpenChangePw() {
  document.getElementById('pconfig-main').style.display = 'none';
  document.getElementById('pconfig-password').classList.add('open');
  ['ppw-current','ppw-new','ppw-confirm'].forEach(id => document.getElementById(id).value = '');
  document.getElementById('ppw-bar').style.width = '0%';
  document.getElementById('ppw-hint').textContent = 'Digite uma nova senha';
  document.getElementById('ppw-hint').style.color = '';
}
function pCloseChangePw() {
  document.getElementById('pconfig-main').style.display = '';
  document.getElementById('pconfig-password').classList.remove('open');
}
function pCheckPwStrength(v) {
  let s = 0;
  if (v.length >= 8) s++;
  if (/[A-Z]/.test(v)) s++;
  if (/[0-9]/.test(v)) s++;
  if (/[^A-Za-z0-9]/.test(v)) s++;
  const L = [
    {p:'0%',  c:'transparent',      t:'Digite uma nova senha'},
    {p:'25%', c:'#dc2626',          t:'Fraca — inclua números e letras'},
    {p:'50%', c:'#d97706',          t:'Razoável — adicione caracteres especiais'},
    {p:'75%', c:'#2563eb',          t:'Boa — quase lá!'},
    {p:'100%',c:'#16a34a',          t:'Forte — ótima senha!'},
  ];
  const lv = v.length === 0 ? 0 : s;
  const lvl = L[lv];
  const bar = document.getElementById('ppw-bar');
  const hint = document.getElementById('ppw-hint');
  bar.style.width = lvl.p; bar.style.background = lvl.c;
  hint.textContent = lvl.t; hint.style.color = lvl.c === 'transparent' ? '' : lvl.c;
}
function pSavePw() {
  const cur   = document.getElementById('ppw-current').value;
  const nw    = document.getElementById('ppw-new').value;
  const conf  = document.getElementById('ppw-confirm').value;
  if (!cur) { logiToast('Informe a senha atual.', 'error'); return; }
  if (nw.length < 6) { logiToast('A nova senha deve ter pelo menos 6 caracteres.', 'error'); return; }
  if (nw !== conf) { logiToast('As senhas não conferem.', 'error'); return; }
  logiToast('Senha atualizada com sucesso!', 'success');
  pCloseChangePw();
}

/* ── Toast ── */
function logiToast(msg, type = 'success') {
  let toast = document.getElementById('logi-toast-el');
  if (!toast) {
    toast = document.createElement('div');
    toast.id = 'logi-toast-el';
    toast.className = 'logi-toast';
    document.body.appendChild(toast);
  }
  const icon = type === 'error' ? 'fa-circle-xmark' : 'fa-circle-check';
  toast.innerHTML = `<i class="fa-solid ${icon}"></i> ${msg}`;
  toast.className = `logi-toast ${type}`;
  requestAnimationFrame(() => { requestAnimationFrame(() => toast.classList.add('show')); });
  clearTimeout(toast._t);
  toast._t = setTimeout(() => toast.classList.remove('show'), 2800);
}
