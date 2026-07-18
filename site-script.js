// Jerry Lyons | Next Step Realty — prototype interactions
// NOTE: This is a design/UX prototype. Forms below do not transmit data anywhere;
// at launch, wire each <form> to your chosen platform's native Follow Up Boss
// integration (or a Zapier webhook) per Section 9 of the strategy document.

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

  // Demo lead-capture form submission
  document.querySelectorAll('form[data-lead-form]').forEach(function (form) {
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var panel = form.closest('.form-panel');
      var confirmBox = panel ? panel.querySelector('.confirm-box') : null;
      form.style.display = 'none';
      if (confirmBox) confirmBox.style.display = 'block';
      console.log('[Prototype] Lead captured — in production this posts to: ' + form.dataset.leadForm + ' -> Follow Up Boss tags: ' + form.dataset.fubTags);
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
        console.log('[Prototype] Quiz lead captured — Follow Up Boss tags: ' + state.intent + ', Quiz Lead, Timeline: ' + state.timeline);
        goToStep(4);
      });
    }
  }

  // Footer contact form demo submission
  var footerForm = document.getElementById('footer-contact-form');
  if (footerForm) {
    footerForm.addEventListener('submit', function (e) {
      e.preventDefault();
      var select = footerForm.querySelector('select[name="footer-intent"]');
      var intent = select ? select.value : 'General Inquiry';
      var confirmBox = footerForm.parentElement.querySelector('.confirm-box');
      footerForm.style.display = 'none';
      if (confirmBox) confirmBox.style.display = 'block';
      console.log('[Prototype] Footer lead captured — intent: ' + intent);
    });
  }

  // Simple valuation "estimate" demo (illustrative only — not a real AVM)
  var valForm = document.getElementById('valuation-form');
  if (valForm) {
    valForm.addEventListener('submit', function (e) {
      e.preventDefault();
      var resultBox = document.getElementById('valuation-result');
      var low = Math.floor((320 + Math.random() * 140));
      var high = low + Math.floor(20 + Math.random() * 40);
      document.getElementById('val-low').textContent = '$' + low + 'K';
      document.getElementById('val-high').textContent = '$' + high + 'K';
      valForm.style.display = 'none';
      if (resultBox) resultBox.style.display = 'block';
    });
  }
});
