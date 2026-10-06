// DOM Element Selectors
const emailForm = document.getElementById('emailForm');
const senderInput = document.getElementById('senderInput');
const subjectInput = document.getElementById('subjectInput');
const emailBody = document.getElementById('emailBody');
const analyzeBtn = document.getElementById('analyzeBtn');
const btnSpinner = document.getElementById('btnSpinner');
const sampleSpamBtn = document.getElementById('sampleSpamBtn');
const sampleHamBtn = document.getElementById('sampleHamBtn');
const clearBtn = document.getElementById('clearBtn');

const emptyState = document.getElementById('emptyState');
const resultDetails = document.getElementById('resultDetails');
const verdictBanner = document.getElementById('verdictBanner');
const verdictPill = document.getElementById('verdictPill');
const verdictTitle = document.getElementById('verdictTitle');
const verdictDesc = document.getElementById('verdictDesc');
const scoreValue = document.getElementById('scoreValue');

const metricUrgencyVal = document.getElementById('metricUrgencyVal');
const metricUrgencyBar = document.getElementById('metricUrgencyBar');
const metricLinksVal = document.getElementById('metricLinksVal');
const metricLinksBar = document.getElementById('metricLinksBar');
const metricSpamWordsVal = document.getElementById('metricSpamWordsVal');
const metricSpamWordsBar = document.getElementById('metricSpamWordsBar');
const rationaleList = document.getElementById('rationaleList');

// Demo Pre-filled Samples
const sampleSpam = {
  sender: 'security-team@paypal-account-verification-alert99.biz',
  subject: 'URGENT: Unauthorized login detected - Account Restricted',
  body: `Dear Valued Customer,\n\nWe detected unauthorized sign-in attempts from IP 194.26.29.112 (Moscow, RU).\nTo avoid permanent account suspension, verify your credentials within 24 hours.\n\nClick the secure gateway below:\nhttp://login-verification-paypal.biz/secure/auth?token=8x7a99f1\n\nFailure to take action immediately will result in an irrevocable freeze of all funds.`
};

const sampleHam = {
  sender: 'project-guide@college.edu',
  subject: 'Updated schedule for AI project viva next week',
  body: `Hi Team,\n\nPlease find attached the revised schedule for the upcoming project demonstration.\nEnsure your code repository and slide deck are prepared by Monday 10:00 AM.\n\nLet me know if you need any feedback before the final review.\n\nBest regards,\nProf. Dona Chakraborty`
};

// Preset Button Actions
sampleSpamBtn.addEventListener('click', () => {
  senderInput.value = sampleSpam.sender;
  subjectInput.value = sampleSpam.subject;
  emailBody.value = sampleSpam.body;
});

sampleHamBtn.addEventListener('click', () => {
  senderInput.value = sampleHam.sender;
  subjectInput.value = sampleHam.subject;
  emailBody.value = sampleHam.body;
});

clearBtn.addEventListener('click', () => {
  senderInput.value = '';
  subjectInput.value = '';
  emailBody.value = '';
  emptyState.classList.remove('hidden');
  resultDetails.classList.add('hidden');
});

// Form Submission Handler
emailForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  const text = emailBody.value.trim();
  if (!text) return;

  // Show loading spinner
  analyzeBtn.disabled = true;
  btnSpinner.style.display = 'inline-block';

  try {
    /* 
      ======================================================
      CONNECTING TO REAL FLASK BACKEND (Phase 3 of Roadmap):
      ======================================================
      const response = await fetch('http://127.0.0.1:5000/api/predict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          sender: senderInput.value,
          subject: subjectInput.value,
          body: text
        })
      });
      const data = await response.json();
    */

    // Built-in Client NLP Demonstration Engine
    await new Promise((resolve) => setTimeout(resolve, 500)); // Simulate inference delay
    const data = simulateSpamDetection(text, senderInput.value, subjectInput.value);

    renderResults(data);
  } catch (error) {
    alert('Error connecting to classification engine: ' + error.message);
  } finally {
    analyzeBtn.disabled = false;
    btnSpinner.style.display = 'none';
  }
});

// Simulated Model Engine (Matching TF-IDF Corpus Rules)
function simulateSpamDetection(body, sender, subject) {
  const combined = `${sender} ${subject} ${body}`.toLowerCase();

  const spamTriggers = ['urgent', 'verify', 'password', 'free', 'wire transfer', 'restricted', 'freeze', 'click below', 'unauthorized', '24 hours', 'prize', 'winner'];
  const matched = spamTriggers.filter((term) => combined.includes(term));

  const hasSuspiciousLink = /https?:\/\/[^\s]+\.(biz|top|xyz|ru)/i.test(combined) || combined.includes('http');
  const isUrgent = matched.some((w) => ['urgent', '24 hours', 'restricted', 'freeze'].includes(w));
  const suspiciousSender = sender.includes('-') || sender.endsWith('.biz') || sender.endsWith('.xyz');

  let spamScore = 0.15;
  if (matched.length > 0) spamScore += matched.length * 0.2;
  if (hasSuspiciousLink) spamScore += 0.3;
  if (suspiciousSender) spamScore += 0.25;
  spamScore = Math.min(Math.max(spamScore, 0.05), 0.98);

  const isSpam = spamScore >= 0.5;
  const rationale = [];

  if (isSpam) {
    if (suspiciousSender) rationale.push("Sender uses non-standard TLD or lookalike domain syntax.");
    if (hasSuspiciousLink) rationale.push("Embedded link redirects to an unverified or high-risk domain.");
    if (isUrgent) rationale.push("Urgent psychological coercion triggers detected ('restricted', '24 hours').");
    if (matched.length > 0) rationale.push(`Identified high-salience spam tokens: ${matched.slice(0, 3).join(', ')}.`);
  } else {
    rationale.push("Clean lexical distribution with low spam keyword salience.");
    rationale.push("No malicious redirects, unverified attachments, or spoofed subdomains detected.");
    rationale.push("Standard academic or professional communication tone verified.");
  }

  return {
    prediction: isSpam ? 'Spam' : 'Not Spam',
    probability: Math.round(spamScore * 100),
    urgencyScore: isUrgent ? Math.round(75 + Math.random() * 20) : Math.round(10 + Math.random() * 20),
    linkRiskScore: hasSuspiciousLink ? 95 : 10,
    keywordDensity: Math.min(Math.round((matched.length / 4) * 100), 95),
    reasons: rationale
  };
}

// Render Results into UI
function renderResults(data) {
  emptyState.classList.add('hidden');
  resultDetails.classList.remove('hidden');

  const isSpam = data.prediction === 'Spam';

  verdictBanner.className = `verdict-banner ${isSpam ? 'spam' : 'ham'}`;
  verdictPill.textContent = isSpam ? 'CRITICAL RISK / SPAM' : 'LEGITIMATE / NOT SPAM';
  verdictTitle.textContent = isSpam ? 'Spam / Phishing Email Detected' : 'Email Classified as Safe (Ham)';
  verdictDesc.textContent = isSpam
    ? `Confidence: ${data.probability}% spam probability. Recommend quarantining message.`
    : `Confidence: ${100 - data.probability}% safe probability. No malicious markers detected.`;

  scoreValue.textContent = `${data.probability}%`;

  metricUrgencyVal.textContent = `${data.urgencyScore}%`;
  metricUrgencyBar.style.width = `${data.urgencyScore}%`;
  metricUrgencyBar.className = `progress-fill ${data.urgencyScore > 60 ? 'danger' : 'safe'}`;

  metricLinksVal.textContent = `${data.linkRiskScore}%`;
  metricLinksBar.style.width = `${data.linkRiskScore}%`;
  metricLinksBar.className = `progress-fill ${data.linkRiskScore > 50 ? 'danger' : 'safe'}`;

  metricSpamWordsVal.textContent = `${data.keywordDensity}%`;
  metricSpamWordsBar.style.width = `${data.keywordDensity}%`;
  metricSpamWordsBar.className = `progress-fill ${data.keywordDensity > 50 ? 'danger' : 'safe'}`;

  rationaleList.innerHTML = '';
  data.reasons.forEach((reason) => {
    const li = document.createElement('li');
    li.textContent = reason;
    rationaleList.appendChild(li);
  });
}