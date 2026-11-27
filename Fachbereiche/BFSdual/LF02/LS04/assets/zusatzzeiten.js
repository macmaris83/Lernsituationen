(() => {
  "use strict";

  const additionalPages = new Set(["index.html", "handlungssituation.html", "begriffstraining.html"]);

  function setup() {
    const page = location.pathname.split("/").pop() || "index.html";
    if (!additionalPages.has(page) || document.body.hasAttribute("data-teacher")) return;
    if (document.body.dataset.bfsdualZusatzzeiten === "true") return;
    document.body.dataset.bfsdualZusatzzeiten = "true";

    const anchors = document.querySelectorAll(".assignment-time[data-task-id][data-task-minutes]");
    const seenIds = new Set();
    let active = null;
    let interval = null;
    let audio = null;

    function save(task) {
      try {
        sessionStorage.setItem(task.key, JSON.stringify({
          total: task.total,
          remaining: task.remaining,
          started: task.started,
          sound: task.sound.checked
        }));
      } catch {
        // The timer also works when browser storage is unavailable.
      }
    }

    function read(key, total) {
      try {
        const state = JSON.parse(sessionStorage.getItem(key));
        if (state?.total === total && Number.isInteger(state.remaining)
            && state.remaining >= 0 && state.remaining <= total) {
          return {remaining: state.remaining, started: state.started === true, sound: state.sound !== false};
        }
      } catch {
        // Ignore unavailable or invalid saved state.
      }
      return {remaining: total, started: false, sound: true};
    }

    function prepareAudio() {
      try {
        const Audio = window.AudioContext || window.webkitAudioContext;
        if (!Audio) return;
        audio ||= new Audio();
        if (audio.state === "suspended") audio.resume().catch(() => {});
      } catch {
        // The visible notice is always available.
      }
    }

    function chime(task) {
      if (!task.sound.checked || audio?.state !== "running") return;
      try {
        for (const delay of [0, 0.38, 0.76]) {
          const time = audio.currentTime + delay;
          const tone = audio.createOscillator();
          const volume = audio.createGain();
          tone.frequency.value = 880;
          volume.gain.setValueAtTime(0.001, time);
          volume.gain.exponentialRampToValueAtTime(0.12, time + 0.025);
          volume.gain.exponentialRampToValueAtTime(0.001, time + 0.30);
          tone.connect(volume);
          volume.connect(audio.destination);
          tone.start(time);
          tone.stop(time + 0.32);
        }
      } catch {
        // A failed sound never interrupts the task.
      }
    }

    function draw(task) {
      const minutes = String(Math.floor(task.remaining / 60)).padStart(2, "0");
      const seconds = String(task.remaining % 60).padStart(2, "0");
      task.clock.textContent = minutes + ":" + seconds;
      task.button.disabled = task.remaining === 0;
      if (task.remaining === 0) {
        task.button.textContent = "Zeit abgelaufen";
        task.status.textContent = "Orientierungszeit erreicht. Ihr könnt weiterarbeiten.";
      } else if (active === task) {
        task.button.textContent = "Pause";
      } else if (task.started) {
        task.button.textContent = "Fortsetzen";
      } else {
        task.button.textContent = "Start";
      }
    }

    function clearActive() {
      clearInterval(interval);
      interval = null;
      active = null;
    }

    function update(task) {
      const remaining = Math.max(0, Math.ceil((task.deadline - Date.now()) / 1000));
      if (remaining === task.remaining) return;
      task.remaining = remaining;
      if (remaining === 0) {
        clearActive();
        chime(task);
      }
      save(task);
      draw(task);
    }

    function pause() {
      if (!active) return;
      const task = active;
      update(task);
      clearActive();
      save(task);
      draw(task);
    }

    function start(task) {
      if (active === task) {
        pause();
        return;
      }
      if (!task.remaining) return;
      pause();
      if (task.sound.checked) prepareAudio();
      active = task;
      task.started = true;
      task.deadline = Date.now() + task.remaining * 1000;
      draw(task);
      interval = setInterval(() => update(task), 200);
    }

    for (const anchor of anchors) {
      const id = anchor.dataset.taskId.trim();
      const total = Math.round(Number(anchor.dataset.taskMinutes) * 60);
      if (!id || seenIds.has(id) || !Number.isSafeInteger(total) || total < 1) continue;
      seenIds.add(id);
      const folder = location.pathname.slice(0, location.pathname.lastIndexOf("/") + 1);
      const key = "bfsdual-zusatzzeit:" + folder + ":" + id;
      const saved = read(key, total);
      const controls = document.createElement("span");
      controls.className = "bfsdual-zusatzzeit";
      controls.setAttribute("role", "group");
      controls.setAttribute("aria-label", "Aufgabenzeit");
      const clock = document.createElement("span");
      clock.setAttribute("role", "timer");
      clock.setAttribute("aria-label", "Verbleibende Orientierungszeit");
      const button = document.createElement("button");
      button.type = "button";
      const soundLabel = document.createElement("label");
      const sound = document.createElement("input");
      sound.type = "checkbox";
      sound.checked = saved.sound;
      soundLabel.append(sound, " Signalton bei Zeitablauf");
      const status = document.createElement("span");
      status.setAttribute("role", "status");
      const task = {key, total, remaining: saved.remaining, started: saved.started, deadline: 0, clock, button, sound, status};
      button.addEventListener("click", () => start(task));
      sound.addEventListener("change", () => {
        if (sound.checked) prepareAudio();
        save(task);
      });
      controls.append(" · ", clock, " ", button, " ", soundLabel, " ", status);
      anchor.after(controls);
      draw(task);
    }

    document.addEventListener("visibilitychange", () => {
      if (document.visibilityState === "hidden") pause();
    });
    window.addEventListener("pagehide", pause);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", setup, {once: true});
  } else {
    setup();
  }
})();
