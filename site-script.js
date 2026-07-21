// Jerry Lyons | Next Step Realty — site interactions
// Lead forms submit to two places at once:
//   1. Follow Up Boss directly, via a Cloudflare Worker relay (FUB_RELAY_URL)
//      that calls FUB's official /events API. This creates a fully structured
//      lead — name, address, tags, correct lead type — and triggers FUB's own
//      agent-assignment and automation rules.
//   2. Formspree, which forwards a plain-text copy to Jerry's FUB lead-capture
//      email as a backup safety net in case the relay is ever down.
// Both are fire-and-forget: a failure in one never blocks the other, and never
// blocks the on-page "thanks" confirmation the visitor sees.

var FORMSPREE_ENDPOINT = 'https://formspree.io/f/mbdnozpq';

// Cloudflare Worker relay for Follow Up Boss integration
var FUB_RELAY_URL = 'https://fub-lead-relay.jerry-3a4.workers.dev';

// Reads every field out of a form into a plain object.
function collectFormValues(form) {
  var values = {};
  var fd = new FormData(form);
  fd.forEach(function (val, key) {
    if (typeof val === 'string') values[key] = val;
  });
  return values;
}

// Sends a lead straight to Follow Up Boss via the relay. Non-blocking and
// silently no-ops if the relay isn't configured yet or the request fails —
// the Formspree backup still covers the lead either way.
function sendToFUB(formType, tagsCsv, values, pageUrl) {
  if (!FUB_RELAY_URL || FUB_RELAY_URL.indexOf('REPLACE-WITH') !== -1) return;

  var name = values.name || '';
  var firstName = values.firstName || '';
  var lastName = values.lastName || '';
  if (!firstName && name) {
    var parts = name.trim().split(/\s+/);
    firstName = parts.shift() || '';
    lastName = parts.join(' ');
  }

  var knownKeys = ['name', 'firstName', 'lastName', 'email', 'phone', 'address', 'city', 'state', 'zip', 'timeline'];
  var extra = [];
  Object.keys(values).forEach(function (k) {
    if (knownKeys.indexOf(k) === -1 && values[k]) extra.push(k + ': ' + values[k]);
  });

  var payload = {
    formType: formType,
    tags: tagsCsv ? tagsCsv.split(',').map(function (t) { return t.trim(); }).filter(Boolean) : [],
    firstName: firstName,
    lastName: lastName,
    email: values.email || '',
    phone: values.phone || '',
    address: values.address || '',
    city: values.city || '',
    state: values.state || '',
    zip: values.zip || '',
    timeline: values.timeline || '',
    message: extra.join('; '),
    pageUrl: pageUrl || window.location.href
  };

  fetch(FUB_RELAY_URL, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  }).catch(function () { /* non-fatal; Formspree backup still covers this lead */ });
}

document.addEventListener('DOMContentLoaded', function () {
  // Mobile nav toggle
  var toggle = document.querySelector('.menu-toggle');
  var nav = document.querySelector('.main-nav');
  if (toggle && nav) {
    toggle.addEventListener('click', function () {
      var isOpen = nav.style.display === 'flex';
      nav.style.display = isOpen ? 'none' : 'flex';
      nav.style.flexDirection = 'column';
      nav.style.position = 'absolute';
      nav.style.top = '64px';
      nav.style.left = '0';
      nav.style.right = '0';
      nav.style.background = '#fff';
      nav.style.padding = '18px 24px';
      nav.style.borderBottom = '1px solid #E4E2DA';
    });
  }

  // Floating chat widget (Ben Kinney-style proactive greeting)
  var chatWidget = document.getElementById('chat-widget');
  if (chatWidget) {
    var chatGreeting = document.getElementById('chat-greeting');
    var chatBubbleBtn = document.getElementById('chat-bubble-btn');
    var chatGreetingClose = document.getElementById('chat-greeting-close');
    var chatBadge = document.getElementById('chat-badge');

    var greetingTimer = setTimeout(function () {
      if (chatGreeting) chatGreeting.classList.add('visible');
    }, 2500);

    function dismissGreeting() {
      clearTimeout(greetingTimer);
      if (chatGreeting) chatGreeting.classList.remove('visible');
    }
    function clearBadge() {
      if (chatBadge) chatBadge.classList.add('hidden');
    }

    if (chatGreetingClose) {
      chatGreetingClose.addEventListener('click', function (e) {
        e.stopPropagation();
        dismissGreeting();
      });
    }
    if (chatGreeting) {
      chatGreeting.addEventListener('click', function () {
        clearBadge();
        dismissGreeting();
        if (chatBubbleBtn) chatBubbleBtn.click();
      });
    }
    if (chatBubbleBtn) {
      chatBubbleBtn.addEventListener('click', function () {
        clearBadge();
        dismissGreeting();
      });
    }
  }

  // Live lead-capture form submission (e.g. "Schedule My Free Call")
  document.querySelectorAll('form[data-lead-form]').forEach(function (form) {
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var panel = form.closest('.form-panel');
      var confirmBox = panel ? panel.querySelector('.confirm-box') : null;
      var values = collectFormValues(form);
      var formData = new FormData(form);
      formData.append('_subject', 'New Website Lead: ' + (form.dataset.leadForm || 'Website Form'));
      if (form.dataset.fubTags) formData.append('fub_tags', form.dataset.fubTags);

      sendToFUB(form.dataset.leadForm || 'general', form.dataset.fubTags || '', values);

      fetch(FORMSPREE_ENDPOINT, {
        method: 'POST',
        body: formData,
        headers: { 'Accept': 'application/json' }
      }).finally(function () {
        form.style.display = 'none';
        if (confirmBox) confirmBox.style.display = 'block';
      });
    });
  });

  // Guided quiz modal (Ben Kinney-style: intent -> timeline -> contact -> thanks)
  var quizOverlay = document.getElementById('quiz-overlay');
  if (quizOverlay) {
    var progressBar = document.getElementById('quiz-progress-bar');
    var steps = quizOverlay.querySelectorAll('.quiz-step');
    var state = { intent: null, intentLabel: null, timeline: null };

    function goToStep(n) {
      steps.forEach(function (s) {
        s.classList.toggle('active', s.getAttribute('data-step') === String(n));
      });
      if (progressBar) progressBar.style.width = (n * 25) + '%';
    }
    function openQuiz() {
      state = { intent: null, intentLabel: null, timeline: null };
      goToStep(1);
      quizOverlay.classList.add('open');
    }
    function closeQuiz() {
      quizOverlay.classList.remove('open');
    }
    document.querySelectorAll('[data-open-quiz]').forEach(function (btn) {
      btn.addEventListener('click', openQuiz);
    });
    var quizClose = document.getElementById('quiz-close');
    if (quizClose) quizClose.addEventListener('click', closeQuiz);
    var quizDone = document.getElementById('quiz-done');
    if (quizDone) quizDone.addEventListener('click', closeQuiz);
    quizOverlay.addEventListener('click', function (e) {
      if (e.target === quizOverlay) closeQuiz();
    });
    quizOverlay.querySelectorAll('[data-step="1"] .quiz-option-btn').forEach(function (btn) {
      btn.addEventListener('click', function () {
        state.intent = btn.dataset.intent;
        state.intentLabel = btn.dataset.answer;
        goToStep(2);
      });
    });
    quizOverlay.querySelectorAll('[data-step="2"] .quiz-option-btn').forEach(function (btn) {
      btn.addEventListener('click', function () {
        state.timeline = btn.dataset.answer;
        goToStep(3);
      });
    });
    quizOverlay.querySelectorAll('.quiz-back').forEach(function (btn) {
      btn.addEventListener('click', function () {
        goToStep(btn.dataset.back);
      });
    });
    var quizForm = document.getElementById('quiz-contact-form');
    if (quizForm) {
      quizForm.addEventListener('submit', function (e) {
        e.preventDefault();
        var heading = document.getElementById('quiz-thanks-heading');
        var body = document.getElementById('quiz-thanks-body');
        var label = state.intentLabel || 'your situation';
        if (body) {
          body.textContent = "Thanks — since you're " + label.toLowerCase() + " (timeline: " + (state.timeline || 'flexible') + "), I'll follow up personally within one business day with next steps tailored to that.";
        }

        var values = collectFormValues(quizForm);
        values.timeline = state.timeline || '';
        sendToFUB('quiz', state.intent || 'General Inquiry', values);

        var formData = new FormData(quizForm);
        formData.append('_subject', 'New Website Lead: Quiz (' + (state.intentLabel || 'General Inquiry') + ')');
        formData.append('intent', state.intent || '');
        formData.append('timeline', state.timeline || '');

        fetch(FORMSPREE_ENDPOINT, {
          method: 'POST',
          body: formData,
          headers: { 'Accept': 'application/json' }
        }).finally(function () {
          goToStep(4);
        });
      });
    }
  }

  // Footer contact form submission
  var footerForm = document.getElementById('footer-contact-form');
  if (footerForm) {
    footerForm.addEventListener('submit', function (e) {
      e.preventDefault();
      var select = footerForm.querySelector('select[name="footer-intent"]');
      var intent = select ? select.value : 'General Inquiry';
      var confirmBox = footerForm.parentElement.querySelector('.confirm-box');
      var values = collectFormValues(footerForm);
      var formData = new FormData(footerForm);
      formData.append('_subject', 'New Website Lead: Footer Form (' + intent + ')');

      sendToFUB('footer-contact', intent, values);

      fetch(FORMSPREE_ENDPOINT, {
        method: 'POST',
        body: formData,
        headers: { 'Accept': 'application/json' }
      }).finally(function () {
        footerForm.style.display = 'none';
        if (confirmBox) confirmBox.style.display = 'block';
      });
    });
  }

  // Home valuation form — submits a real lead to Follow Up Boss + Formspree,
  // then shows an illustrative instant estimate (not a real AVM) while Jerry
  // follows up personally.
  var valForm = document.getElementById('valuation-form');
  if (valForm) {
    valForm.addEventListener('submit', function (e) {
      e.preventDefault();
      var resultBox = document.getElementById('valuation-result');
      var low = Math.floor((320 + Math.random() * 140));
      var high = low + Math.floor(20 + Math.random() * 40);
      document.getElementById('val-low').textContent = '$' + low + 'K';
      document.getElementById('val-high').textContent = '$' + high + 'K';

      var fubTags = 'Website Seller Lead, Home Valuation Lead, Home Report Subscriber';
      var values = collectFormValues(valForm);
      sendToFUB('home-valuation', fubTags, values);

      var formData = new FormData(valForm);
      formData.append('_subject', 'New Website Lead: Website – Home Valuation');
      formData.append('fub_tags', fubTags);

      fetch(FORMSPREE_ENDPOINT, {
        method: 'POST',
        body: formData,
        headers: { 'Accept': 'application/json' }
      }).finally(function () {
        valForm.style.display = 'none';
        if (resultBox) resultBox.style.display = 'block';
      });
    });
  }
});
