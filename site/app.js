const tabs = Array.from(document.querySelectorAll(".tab"));
const panels = Array.from(document.querySelectorAll(".panel"));
const copyButtons = Array.from(document.querySelectorAll(".copy"));
const demoRoot = document.querySelector("[data-demo-root]");

tabs.forEach((tab) => {
  tab.addEventListener("click", () => {
    const target = tab.dataset.tab;
    tabs.forEach((item) => {
      item.classList.toggle("active", item === tab);
      item.setAttribute("aria-selected", item === tab ? "true" : "false");
    });
    panels.forEach((panel) => {
      panel.classList.toggle("active", panel.dataset.panel === target);
    });
  });
});

copyButtons.forEach((button) => {
  button.addEventListener("click", async () => {
    const original = button.textContent;
    try {
      await navigator.clipboard.writeText(button.dataset.copy || "");
      button.textContent = "Copied";
      setTimeout(() => {
        button.textContent = original;
      }, 1400);
    } catch (_error) {
      button.textContent = "Copy failed";
      setTimeout(() => {
        button.textContent = original;
      }, 1400);
    }
  });
});

if (demoRoot) {
  initializeDemo().catch(() => {
    const support = demoRoot.querySelector(".demo-support");
    if (support) {
      support.textContent = "The sample scan could not load. You can still install the free CLI below.";
    }
  });
}

async function initializeDemo() {
  const response = await fetch("./demo-scan.json");
  if (!response.ok) {
    throw new Error("Unable to load demo data");
  }

  const demo = await response.json();
  const screens = Array.from(demoRoot.querySelectorAll("[data-demo-screen]"));
  const startButton = demoRoot.querySelector("[data-demo-start]");
  const progressBar = demoRoot.querySelector("[data-demo-progress]");
  const totalEl = demoRoot.querySelector("[data-demo-total]");
  const statusEl = demoRoot.querySelector("[data-demo-status]");
  const eventsEl = demoRoot.querySelector("[data-demo-events]");
  const resultsTitle = demoRoot.querySelector("[data-demo-results-title]");
  const resultsSummary = demoRoot.querySelector("[data-demo-results-summary]");
  const breakdownEl = demoRoot.querySelector("[data-demo-breakdown]");
  const firstWinTitle = demoRoot.querySelector("[data-demo-first-win-title]");
  const firstWinCopy = demoRoot.querySelector("[data-demo-first-win-copy]");
  const firstWinAmount = demoRoot.querySelector("[data-demo-first-win-amount]");
  const firstWinProtected = demoRoot.querySelector("[data-demo-first-win-protected]");
  const upgradeTitle = demoRoot.querySelector("[data-demo-upgrade-title]");
  const upgradeCopy = demoRoot.querySelector("[data-demo-upgrade-copy]");
  const nextButtons = Array.from(demoRoot.querySelectorAll("[data-demo-next]"));

  const showScreen = (screenName) => {
    screens.forEach((screen) => {
      screen.classList.toggle("active", screen.dataset.demoScreen === screenName);
    });
  };

  const animateCounter = (from, to, durationMs) =>
    new Promise((resolve) => {
      const startedAt = performance.now();

      const tick = (timestamp) => {
        const elapsed = timestamp - startedAt;
        const ratio = Math.min(elapsed / durationMs, 1);
        const value = from + (to - from) * ratio;
        totalEl.textContent = `${value.toFixed(1)}GB`;
        if (ratio < 1) {
          requestAnimationFrame(tick);
        } else {
          resolve();
        }
      };

      requestAnimationFrame(tick);
    });

  const renderResults = () => {
    resultsTitle.textContent = demo.results.title;
    resultsSummary.textContent = demo.results.summary;
    breakdownEl.innerHTML = "";

    demo.results.breakdown.forEach((item) => {
      const article = document.createElement("article");
      article.className = "demo-breakdown-card";
      article.innerHTML = `
        <small>${item.label}</small>
        <strong>${item.value}</strong>
        <p>${item.note}</p>
      `;
      breakdownEl.appendChild(article);
    });

    firstWinTitle.textContent = demo.firstWin.title;
    firstWinCopy.textContent = demo.firstWin.copy;
    firstWinAmount.textContent = demo.firstWin.amount;
    firstWinProtected.textContent = demo.firstWin.protected;
    upgradeTitle.textContent = demo.upgrade.title;
    upgradeCopy.textContent = demo.upgrade.copy;
  };

  nextButtons.forEach((button) => {
    button.addEventListener("click", () => {
      showScreen(button.dataset.demoNext || "hook");
    });
  });

  let running = false;

  startButton?.addEventListener("click", async () => {
    if (running) {
      return;
    }

    running = true;
    showScreen("scan");
    eventsEl.innerHTML = "";
    progressBar.style.width = "0%";
    totalEl.textContent = "0.0GB";

    let surfaced = 0;

    for (let index = 0; index < demo.scanSteps.length; index += 1) {
      const step = demo.scanSteps[index];
      statusEl.textContent = step.detail;

      const event = document.createElement("li");
      event.className = step.protected ? "protected" : "";
      event.innerHTML = `
        <span>${step.label}</span>
        <strong>${step.amount.toFixed(1)}GB</strong>
      `;
      eventsEl.appendChild(event);

      const nextSurfaced = surfaced + step.amount;
      progressBar.style.width = `${((index + 1) / demo.scanSteps.length) * 100}%`;
      await animateCounter(surfaced, nextSurfaced, 700);
      surfaced = nextSurfaced;
      await wait(220);
    }

    renderResults();
    showScreen("results");
    running = false;
  });
}

function wait(durationMs) {
  return new Promise((resolve) => {
    window.setTimeout(resolve, durationMs);
  });
}
