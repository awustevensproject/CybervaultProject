(() => {
  const form = document.getElementById('signup-form');
  if (!form) return;

  const strengthUrl = form.dataset.strengthUrl;
  const csrfInput = form.querySelector('[name="csrf_token"]');
  const passwordInput = document.getElementById('password');
  const passwordField = document.getElementById('password-field');
  const strengthMeter = document.getElementById('strength-meter');
  const strengthBar = document.getElementById('strength-bar');
  const strengthLabel = document.getElementById('strength-label');
  const strengthMeta = document.getElementById('strength-meta');
  const requirementsWrap = document.getElementById('pw-requirements-wrap');
  const requirements = document.getElementById('pw-requirements');
  const breachStatusWrap = document.getElementById('breach-status-wrap');
  const breachStatus = document.getElementById('breach-status');
  const signupSubmit = document.getElementById('signup-submit');
  const signupHint = document.getElementById('signup-hint');
  const emailInput = document.getElementById('email');
  const usernameInput = document.getElementById('username');

  let breachState = 'idle';
  let strengthState = 'idle';
  let zxcvbnState = { strongEnough: false, score: 0 };
  let breachTimer = null;
  let strengthTimer = null;
  let breachRequestId = 0;
  let strengthRequestId = 0;

  function signupBlockers() {
    const blockers = [];
    const email = emailInput.value.trim();
    const username = usernameInput.value.trim();
    const pw = passwordInput.value;

    if (!email || !emailInput.checkValidity()) blockers.push('valid email');
    if (!/^[a-zA-Z0-9_]{3,20}$/.test(username)) blockers.push('valid username (3–20 chars)');
    if (pw.length < 10) blockers.push('10+ character password');
    else {
      if (!/[a-z]/.test(pw)) blockers.push('lowercase letter');
      if (!/[A-Z]/.test(pw)) blockers.push('uppercase letter');
      if (!/\d/.test(pw)) blockers.push('number');
      if (strengthState === 'checking') blockers.push('strength check to finish');
      else if (!zxcvbnState.strongEnough && strengthState !== 'unavailable') {
        blockers.push('stronger password (score 3+)');
      }
    }
    if (breachState === 'breached') blockers.push('a password not found in data breaches');
    if (breachState === 'unavailable') blockers.push('breach check to complete');
    return blockers;
  }

  function isSignupReady() {
    return signupBlockers().length === 0;
  }

  function updateSubmitState() {
    const ready = isSignupReady();
    const wasDisabled = signupSubmit.disabled;
    signupSubmit.disabled = !ready;
    if (ready && wasDisabled) {
      signupSubmit.classList.remove('is-ready');
      void signupSubmit.offsetWidth;
      signupSubmit.classList.add('is-ready');
    } else if (!ready) {
      signupSubmit.classList.remove('is-ready');
    }

    const hint = ready ? '' : `Still needed: ${signupBlockers().join(', ')}.`;
    signupHint.textContent = hint;
    signupHint.classList.toggle('has-text', Boolean(hint));
  }

  function ruleChecks(pw, analysis) {
    return {
      length: pw.length >= 10,
      lower: /[a-z]/.test(pw),
      upper: /[A-Z]/.test(pw),
      digit: /\d/.test(pw),
      zxcvbn: Boolean(analysis && analysis.strong_enough),
    };
  }

  function updateRequirements(pw, analysis) {
    const checks = ruleChecks(pw, analysis);
    requirements.querySelectorAll('li').forEach((item) => {
      item.classList.toggle('met', Boolean(checks[item.dataset.rule]));
    });
  }

  function setPasswordExpanded(expanded) {
    passwordField.classList.toggle('is-expanded', expanded);
  }

  function clearStrengthUI() {
    strengthMeter.classList.remove('show');
    requirementsWrap.classList.remove('show');
    breachStatusWrap.classList.remove('show');
    strengthMeta.classList.add('is-hidden');
    strengthMeta.textContent = '';
    breachStatus.textContent = '';
    breachStatus.className = 'breach-status anim-item';
    zxcvbnState = { strongEnough: false, score: 0 };
    strengthState = 'idle';
    breachState = 'idle';
    setPasswordExpanded(false);
    updateSubmitState();
  }

  function pulseStrengthBar() {
    strengthBar.classList.remove('is-updating');
    void strengthBar.offsetWidth;
    strengthBar.classList.add('is-updating');
  }

  function renderStrength(analysis) {
    setPasswordExpanded(true);
    strengthMeter.classList.add('show');
    requirementsWrap.classList.add('show');

    pulseStrengthBar();
    strengthBar.style.width = analysis.width;
    strengthBar.style.background = analysis.color;
    strengthLabel.textContent = `${analysis.label} · ${analysis.score}/4`;
    strengthLabel.style.color = analysis.color;

    if (analysis.crack_time) {
      strengthMeta.textContent = `Crack time: ${analysis.crack_time}`;
      strengthMeta.classList.remove('is-hidden');
    } else {
      strengthMeta.textContent = '';
      strengthMeta.classList.add('is-hidden');
    }

    zxcvbnState = { strongEnough: analysis.strong_enough, score: analysis.score };
    strengthState = 'ready';
    updateRequirements(passwordInput.value, analysis);
    updateSubmitState();
  }

  async function fetchStrength(pw) {
    const response = await fetch(strengthUrl, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ password: pw, csrf_token: csrfInput.value }),
    });
    if (!response.ok) throw new Error('strength_check_failed');
    return response.json();
  }

  function scheduleStrengthCheck(pw) {
    clearTimeout(strengthTimer);
    if (!pw) {
      clearStrengthUI();
      return;
    }

    strengthTimer = setTimeout(async () => {
      const requestId = ++strengthRequestId;
      strengthState = 'checking';
      setPasswordExpanded(true);
      strengthMeter.classList.add('show');
      requirementsWrap.classList.add('show');
      strengthLabel.textContent = 'Checking strength…';
      updateSubmitState();

      try {
        const analysis = await fetchStrength(pw);
        if (requestId !== strengthRequestId) return;
        renderStrength(analysis);
      } catch (_) {
        if (requestId !== strengthRequestId) return;
        strengthState = 'unavailable';
        strengthLabel.textContent = 'Strength check unavailable';
        requirementsWrap.classList.add('show');
        updateRequirements(pw, null);
        updateSubmitState();
      }
    }, 400);
  }

  async function sha1Hex(text) {
    const digest = await crypto.subtle.digest('SHA-1', new TextEncoder().encode(text));
    return Array.from(new Uint8Array(digest))
      .map((b) => b.toString(16).padStart(2, '0'))
      .join('')
      .toUpperCase();
  }

  async function checkBreached(pw) {
    const hash = await sha1Hex(pw);
    const prefix = hash.slice(0, 5);
    const suffix = hash.slice(5);
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 8000);
    try {
      const response = await fetch(`https://api.pwnedpasswords.com/range/${prefix}`, {
        headers: { 'Add-Padding': 'true' },
        signal: controller.signal,
      });
      if (!response.ok) throw new Error('hibp_unavailable');
      const body = await response.text();
      for (const line of body.split('\n')) {
        if (!line) continue;
        const [found, count] = line.split(':');
        if (found === suffix) return parseInt(count, 10);
      }
      return 0;
    } finally {
      clearTimeout(timeout);
    }
  }

  function setBreachStatus(state, message) {
    breachState = state;
    breachStatusWrap.classList.add('show');
    breachStatus.className = `breach-status anim-item ${state}`;
    breachStatus.textContent = message;
    updateSubmitState();
  }

  function scheduleBreachCheck(pw) {
    clearTimeout(breachTimer);
    if (!pw) return;

    breachTimer = setTimeout(async () => {
      const requestId = ++breachRequestId;
      setBreachStatus('checking', 'Checking against known data breaches…');

      try {
        const count = await checkBreached(pw);
        if (requestId !== breachRequestId) return;
        if (count > 0) {
          const times = count.toLocaleString();
          setBreachStatus(
            'breached',
            `Found in ${times} known data breach${count === 1 ? '' : 'es'}. Choose a different password.`
          );
        } else {
          setBreachStatus('safe', 'Not found in known data breaches.');
        }
      } catch (_) {
        if (requestId !== breachRequestId) return;
        setBreachStatus('unavailable', 'Breach check unavailable — still checked on submit.');
      }
    }, 450);
  }

  passwordInput.addEventListener('input', (event) => {
    const pw = event.target.value;
    if (pw) setPasswordExpanded(true);
    scheduleStrengthCheck(pw);
    scheduleBreachCheck(pw);
    updateSubmitState();
  });

  passwordInput.addEventListener('focus', () => setPasswordExpanded(true));
  emailInput.addEventListener('input', updateSubmitState);
  usernameInput.addEventListener('input', updateSubmitState);

  form.addEventListener('submit', (event) => {
    if (!isSignupReady()) event.preventDefault();
  });

  updateSubmitState();

  if (passwordInput.value) {
    setPasswordExpanded(true);
    scheduleStrengthCheck(passwordInput.value);
    scheduleBreachCheck(passwordInput.value);
  }

  passwordInput.addEventListener('copy', (event) => event.stopPropagation());
})();
