// Jerry Lyons | Next Step Realty - website AI chat bubble.
// Add to a page with:
//   <script src="site-chat-agent.js" data-endpoint="https://jerry-chat-agent.<account>.workers.dev" defer></script>
// Talks to the jerry-chat-agent Cloudflare Worker. Conversation is kept in
// sessionStorage so it survives page-to-page navigation within the visit.
(function () {
  var script = document.currentScript;
  var ENDPOINT = (script && script.getAttribute('data-endpoint')) || '';
  var POSITION = (script && script.getAttribute('data-position')) === 'left' ? 'left' : 'right';
  var STORE = 'jl-chat-v1';
  var GREETING = "Hi! I'm Jerry Lyons' AI assistant. Are you buying, selling, renting, or investing? I can answer questions or get you connected with Jerry.";

  var state = load();

  function load() {
    try {
      var saved = JSON.parse(sessionStorage.getItem(STORE) || 'null');
      if (saved && Array.isArray(saved.messages)) return saved;
    } catch (e) { /* storage blocked */ }
    return { messages: [], specialist: 'general', leadSaved: false, open: false };
  }

  function save() {
    try { sessionStorage.setItem(STORE, JSON.stringify(state)); } catch (e) { /* ignore */ }
  }

  var css = '' +
    '.jlc-btn{position:fixed;bottom:20px;' + POSITION + ':20px;z-index:2147483000;width:60px;height:60px;border-radius:50%;border:0;background:#8c252c;color:#fff;box-shadow:0 6px 20px rgba(0,0,0,.25);cursor:pointer;display:flex;align-items:center;justify-content:center}' +
    '.jlc-btn svg{width:28px;height:28px}' +
    '.jlc-panel{position:fixed;bottom:92px;' + POSITION + ':20px;z-index:2147483000;width:370px;max-width:calc(100vw - 32px);height:540px;max-height:calc(100vh - 120px);background:#fff;border-radius:14px;box-shadow:0 12px 40px rgba(0,0,0,.28);display:none;flex-direction:column;overflow:hidden;font-family:Inter,Arial,sans-serif;color:#20231f}' +
    '.jlc-panel.open{display:flex}' +
    '.jlc-head{background:#151816;color:#fff;padding:14px 16px;display:flex;justify-content:space-between;align-items:center}' +
    '.jlc-head strong{display:block;font-size:15px}.jlc-head span{font-size:12px;color:#c8ccc8}' +
    '.jlc-close{background:none;border:0;color:#fff;font-size:22px;cursor:pointer;line-height:1}' +
    '.jlc-log{flex:1;overflow-y:auto;padding:14px;background:#f6f4ef;display:flex;flex-direction:column;gap:10px}' +
    '.jlc-msg{max-width:85%;padding:10px 12px;border-radius:12px;font-size:14px;line-height:1.45;white-space:pre-wrap;word-wrap:break-word}' +
    '.jlc-msg a{color:#8c252c;text-decoration:underline}' +
    '.jlc-bot{background:#fff;align-self:flex-start;border:1px solid #e5e2db}' +
    '.jlc-user{background:#8c252c;color:#fff;align-self:flex-end}' +
    '.jlc-typing{font-size:12px;color:#777;align-self:flex-start}' +
    '.jlc-form{display:flex;border-top:1px solid #e5e2db;background:#fff}' +
    '.jlc-form textarea{flex:1;border:0;padding:12px;font:inherit;font-size:14px;resize:none;height:48px;outline:none}' +
    '.jlc-form button{border:0;background:#8c252c;color:#fff;padding:0 16px;font-weight:700;cursor:pointer}' +
    '.jlc-form button[disabled]{opacity:.6;cursor:wait}' +
    '.jlc-foot{font-size:10.5px;color:#777;padding:6px 12px 8px;background:#fff;line-height:1.35}';

  var style = document.createElement('style');
  style.textContent = css;
  document.head.appendChild(style);

  var btn = document.createElement('button');
  btn.className = 'jlc-btn';
  btn.setAttribute('aria-label', 'Chat with Jerry Lyons\' AI assistant');
  btn.innerHTML = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>';

  var panel = document.createElement('div');
  panel.className = 'jlc-panel';
  panel.setAttribute('role', 'dialog');
  panel.setAttribute('aria-label', 'Chat with Jerry Lyons\' AI assistant');
  panel.innerHTML =
    '<div class="jlc-head"><div><strong>Jerry Lyons | Next Step Realty</strong><span>AI assistant · Jerry follows up personally</span></div>' +
    '<button class="jlc-close" aria-label="Close chat">&times;</button></div>' +
    '<div class="jlc-log" aria-live="polite"></div>' +
    '<form class="jlc-form"><textarea placeholder="Type your message…" aria-label="Message" maxlength="2000"></textarea><button type="submit">Send</button></form>' +
    '<div class="jlc-foot">AI assistant - answers may be imperfect and are not legal, tax, or lending advice. Contact info you share goes to Jerry. <a href="site-privacy.html">Privacy</a></div>';

  document.body.appendChild(btn);
  document.body.appendChild(panel);

  var log = panel.querySelector('.jlc-log');
  var form = panel.querySelector('.jlc-form');
  var input = form.querySelector('textarea');
  var send = form.querySelector('button');

  // Escape HTML, then turn bare URLs into links.
  function render(text) {
    var safe = text.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
    return safe.replace(/https?:\/\/[^\s<)]+[^\s<).,!?]/g, function (url) {
      return '<a href="' + url + '" target="_blank" rel="noopener">' + url + '</a>';
    });
  }

  function bubble(role, text) {
    var div = document.createElement('div');
    div.className = 'jlc-msg ' + (role === 'user' ? 'jlc-user' : 'jlc-bot');
    div.innerHTML = render(text);
    log.appendChild(div);
    log.scrollTop = log.scrollHeight;
  }

  function redraw() {
    log.innerHTML = '';
    bubble('assistant', GREETING);
    state.messages.forEach(function (m) { bubble(m.role, m.content); });
  }

  function setOpen(open) {
    state.open = open;
    panel.classList.toggle('open', open);
    save();
    if (open) { log.scrollTop = log.scrollHeight; input.focus(); }
  }

  btn.addEventListener('click', function () { setOpen(!panel.classList.contains('open')); });
  panel.querySelector('.jlc-close').addEventListener('click', function () { setOpen(false); });
  input.addEventListener('keydown', function (e) {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); form.requestSubmit(); }
  });

  form.addEventListener('submit', function (e) {
    e.preventDefault();
    var text = input.value.trim();
    if (!text || send.disabled) return;
    input.value = '';
    state.messages.push({ role: 'user', content: text });
    // Keep the newest turns; the worker accepts at most 40 and must start with the visitor.
    while (state.messages.length > 39) state.messages.splice(0, 2);
    save();
    bubble('user', text);

    var typing = document.createElement('div');
    typing.className = 'jlc-typing';
    typing.textContent = 'Typing…';
    log.appendChild(typing);
    log.scrollTop = log.scrollHeight;
    send.disabled = true;

    fetch(ENDPOINT, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        messages: state.messages,
        specialist: state.specialist,
        leadSaved: state.leadSaved,
        pageUrl: window.location.href
      })
    }).then(function (r) { return r.json(); }).then(function (data) {
      var reply = (data && data.reply) || "Sorry - I'm having trouble right now. You can reach Jerry at (410) 430-3877.";
      if (data && data.ok) {
        state.specialist = data.specialist || state.specialist;
        state.leadSaved = Boolean(data.leadSaved);
        state.messages.push({ role: 'assistant', content: reply });
      } else {
        state.messages.pop(); // drop the unanswered turn so history stays valid
      }
      save();
      typing.remove();
      bubble('assistant', reply);
    }).catch(function () {
      state.messages.pop();
      save();
      typing.remove();
      bubble('assistant', "Sorry - I couldn't connect. You can reach Jerry at (410) 430-3877 or Jerry@nextsteprealtymd.com.");
    }).then(function () { send.disabled = false; });
  });

  redraw();
  if (state.open) setOpen(true);
})();
