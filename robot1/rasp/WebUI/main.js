// let console_div = document.getElementById('log');

let config_data = {
  mode: null,
  team: null,
};

const pidDebugState = {
  maxPoints: 240,
  lastSampleCount: -1,
  timeline: [],
  linearTarget: [],
  linearActual: [],
  angularTarget: [],
  angularActual: [],
  linearError: [],
  angularError: [],
};

let log = new WebSocketManager();
log.add_ws("ui");
function on_ws_close() {
  log.on_ws_close("ui", async () => {
    resetPage();
    log.update_status("disconnected");
    console.log("Websocket closed, attempting to reconnect...");
    const intervalId = setInterval(async () => {
      try {
        if (log.status === "connected") {
          clearInterval(intervalId);
          on_ws_close();
        } else {
          log.add_ws("ui");
          add_handler();
          console.log("Reconnection attempt failed. Attempting again...");
        }
      } catch (error) {
        console.log("Reconnection attempt failed. Attempting again...");
      }
    }, 2000); // Retry every 2000 milliseconds
  });
}
on_ws_close();
function add_handler() {
  log.add_handler("ui", (event) => {
    // Parse the JSON message and display the console data
    let data = JSON.parse(event.data);
    if (data.msg === "update ui data") {
      // show_console_data(JSON.stringify(data.data), true);

      const jack_state = document.getElementById("jack_state");
      if (jack_state) {
        jack_state.style.backgroundColor = data.data["jack_state"]
          ? "limegreen"
          : "red";
        if (data.data["jack_state"]) {
          jack_state.innerText = "Ready";
        } else if (jack_state.innerText == "Ready") {
          jack_state.innerText = "Not Ready";
        }
      }

      const info_coords = document.getElementById("info_coords");
      if (info_coords) {
        info_coords.innerText = `${data.data["odometrie"].x.toFixed(
          2
        )}, ${data.data["odometrie"].y.toFixed(2)}, ${(
          (normalize_angle(data.data["odometrie"].theta) * 180) /
          Math.PI
        ).toFixed(2)}°`;
      }

      const bau_state = document.getElementById("bau_state");
      if (bau_state) {
        bau_state.style.backgroundColor = data.data["BAU"]
          ? "limegreen"
          : "red";
        bau_state.innerText = data.data["BAU"] ? "ON" : "ACTIVATED";
      }

      const score = document.getElementById("score");
      if (score) {
        score.innerText = data.data["score"] ? data.data["score"] : "0";
      }

      const pamis_states = document.getElementById("pami_states");
      if (pamis_states) {
        pamis_states.innerHTML = "";
        for (let pami in data.data["pamis_states"]) {
          const card = document.createElement("div");
          card.dataset.id = `${pami}_state`;
          card.style.backgroundColor = data.data["pamis_states"][pami]
            ? "limegreen"
            : "red";
          card.style.padding = "10px";
          card.style.borderRadius = "20px";
          card.style.color = "white";
          card.style.fontWeight = "bold";
          card.innerHTML = pami;
          pamis_states.append(card);
        }
      }

      const rob = document.querySelector(".rob");
      if (rob) {
        let x = data.data["odometrie"].x;
        let y = data.data["odometrie"].y;
        let theta = data.data["odometrie"].theta;
        let width = data.data["arena_info"].width;
        let height = data.data["arena_info"].height;

        [x, y, theta] = parse_pos(x, y, theta, width, height);

        rob.style.transform = `translate(${x}px, ${y}px) rotate(${theta}deg)`;
      }

      const bad = document.querySelector(".bad");
      if (bad) {
        let x = data.data["enemy_odometrie"].x;
        let y = data.data["enemy_odometrie"].y;
        let theta = data.data["enemy_odometrie"].theta;
        let width = data.data["arena_info"].width;
        let height = data.data["arena_info"].height;

        [x, y, theta] = parse_pos(x, y, theta, width, height);

        bad.style.transform = `translate(${x}px, ${y}px) rotate(${theta}deg)`;
      }

      updatePidDebugPanel(data.data["pid_debug"]);
    } else if (data.msg === "starting") {
      startTimer();
      const timer = document.getElementById("timer");
      timer.style.backgroundColor = "limegreen";
      set_configuration("finished");
    } else if (data.msg === "initializing") {
      const timer = document.getElementById("timer");
      timer.style.backgroundColor = "grey";
      timer.innerHTML = "Init...";
      set_configuration("finished");
    } else if (data.msg === "status") {
      let status = data.data.status;
      let info = data.data.data;
      log.update_status("connected");

      if (status === "starting") {
        startTimer();
        const timer = document.getElementById("timer");
        timer.style.backgroundColor = "limegreen";
        config_data.mode = info.mode;
        config_data.team = info.team;
        set_configuration("finished");
      } else if (status === "initializing") {
        const timer = document.getElementById("timer");
        timer.style.backgroundColor = "grey";
        timer.innerHTML = "Init...";
        config_data.mode = info.mode;
        config_data.team = info.team;
        set_configuration("finished");
      } else if (status === "waiting for mode") {
        set_configuration("mode");
      } else if (status === "waiting for team color") {
        set_configuration("team");
        config_data.mode = info.mode;
      }
    } else if (data.msg === "mode set") {
      set_configuration("team");
      config_data.mode = data.data.mode;
    }
  });
}
add_handler();

function normalize_angle(angle) {
  angle = (angle + Math.PI) % (2 * Math.PI);
  if (angle < 0) {
    angle += 2 * Math.PI;
  }
  return angle - Math.PI;
}

function parse_pos(x, y, theta, width, height) {
  const mapWidth = document.querySelector(".map").clientWidth;
  const mapHeight = document.querySelector(".map").clientHeight;

  x = (x / width) * mapWidth;
  y = -((y / height) * mapHeight);
  theta = -(normalize_angle(theta - Math.PI / 2) * 180) / Math.PI;
  return [x, y, theta];
}

function addPidValue(bufferName, value) {
  const buffer = pidDebugState[bufferName];
  buffer.push(value);
  if (buffer.length > pidDebugState.maxPoints) {
    buffer.shift();
  }
}

function resetPidDebugData() {
  pidDebugState.lastSampleCount = -1;
  pidDebugState.timeline = [];
  pidDebugState.linearTarget = [];
  pidDebugState.linearActual = [];
  pidDebugState.angularTarget = [];
  pidDebugState.angularActual = [];
  pidDebugState.linearError = [];
  pidDebugState.angularError = [];

  const sampleCount = document.getElementById("pid_sample_count");
  if (sampleCount) sampleCount.innerText = "0";
  const lastEvent = document.getElementById("pid_last_event");
  if (lastEvent) lastEvent.innerText = "init";
  const timeS = document.getElementById("pid_time_s");
  if (timeS) timeS.innerText = "0.00s";

  drawPidCharts();
}

function updatePidDebugPanel(pidDebug) {
  if (!pidDebug || pidDebug.enabled !== 1) {
    return;
  }

  const sampleCount = Number(pidDebug.sample_count ?? 0);
  const currentTime = Number(pidDebug.time_s ?? 0);
  const lastEvent = String(pidDebug.last_event ?? "unknown");

  const countNode = document.getElementById("pid_sample_count");
  if (countNode) countNode.innerText = `${sampleCount}`;
  const eventNode = document.getElementById("pid_last_event");
  if (eventNode) eventNode.innerText = lastEvent;
  const timeNode = document.getElementById("pid_time_s");
  if (timeNode) timeNode.innerText = `${currentTime.toFixed(2)}s`;

  if (sampleCount < pidDebugState.lastSampleCount) {
    resetPidDebugData();
  }

  if (sampleCount === pidDebugState.lastSampleCount) {
    return;
  }

  pidDebugState.lastSampleCount = sampleCount;
  addPidValue("timeline", currentTime);
  addPidValue("linearTarget", pidDebug.target_linear_cm_s);
  addPidValue("linearActual", pidDebug.actual_linear_cm_s);
  addPidValue("angularTarget", pidDebug.target_angular_rad_s);
  addPidValue("angularActual", pidDebug.actual_angular_rad_s);
  addPidValue("linearError", pidDebug.linear_error_cm_s);
  addPidValue("angularError", pidDebug.angular_error_rad_s);

  drawPidCharts();
}

function drawPidCharts() {
  drawLineChart("pid_linear_chart", [
    { data: pidDebugState.linearTarget, color: "#1d7afc" },
    { data: pidDebugState.linearActual, color: "#ff6a00" },
  ]);
  drawLineChart("pid_angular_chart", [
    { data: pidDebugState.angularTarget, color: "#1d7afc" },
    { data: pidDebugState.angularActual, color: "#ff6a00" },
  ]);
  drawLineChart("pid_error_chart", [
    { data: pidDebugState.linearError, color: "#00a86b" },
    { data: pidDebugState.angularError, color: "#c84bff" },
  ]);
}

function drawLineChart(canvasId, seriesList) {
  const canvas = document.getElementById(canvasId);
  if (!canvas) return;

  const rect = canvas.getBoundingClientRect();
  if (rect.width <= 0 || rect.height <= 0) return;

  const dpr = window.devicePixelRatio || 1;
  const width = Math.floor(rect.width * dpr);
  const height = Math.floor(rect.height * dpr);
  if (canvas.width !== width || canvas.height !== height) {
    canvas.width = width;
    canvas.height = height;
  }

  const ctx = canvas.getContext("2d");
  if (!ctx) return;
  ctx.setTransform(1, 0, 0, 1, 0, 0);
  ctx.scale(dpr, dpr);

  const chartWidth = rect.width;
  const chartHeight = rect.height;
  ctx.clearRect(0, 0, chartWidth, chartHeight);

  const padding = { top: 12, right: 14, bottom: 16, left: 14 };
  const x0 = padding.left;
  const y0 = padding.top;
  const x1 = chartWidth - padding.right;
  const y1 = chartHeight - padding.bottom;
  const innerW = Math.max(1, x1 - x0);
  const innerH = Math.max(1, y1 - y0);

  ctx.strokeStyle = "#dce3ff";
  ctx.lineWidth = 1;
  for (let i = 0; i <= 4; i++) {
    const y = y0 + (innerH * i) / 4;
    ctx.beginPath();
    ctx.moveTo(x0, y);
    ctx.lineTo(x1, y);
    ctx.stroke();
  }

  const allValues = [];
  seriesList.forEach((series) => {
    series.data.forEach((value) => {
      if (typeof value === "number" && Number.isFinite(value)) {
        allValues.push(value);
      }
    });
  });

  let minY = -1;
  let maxY = 1;
  if (allValues.length > 0) {
    minY = Math.min(...allValues);
    maxY = Math.max(...allValues);
    if (Math.abs(maxY - minY) < 1e-6) {
      minY -= 1;
      maxY += 1;
    } else {
      const margin = (maxY - minY) * 0.1;
      minY -= margin;
      maxY += margin;
    }
  }

  const pointCount = Math.max(2, pidDebugState.timeline.length);

  function mapX(index) {
    return x0 + (innerW * index) / (pointCount - 1);
  }

  function mapY(value) {
    return y1 - ((value - minY) / (maxY - minY)) * innerH;
  }

  seriesList.forEach((series) => {
    ctx.strokeStyle = series.color;
    ctx.lineWidth = 2;
    ctx.beginPath();
    let hasStarted = false;

    for (let i = 0; i < series.data.length; i++) {
      const value = series.data[i];
      if (typeof value !== "number" || !Number.isFinite(value)) {
        hasStarted = false;
        continue;
      }

      const x = mapX(i);
      const y = mapY(value);
      if (!hasStarted) {
        ctx.moveTo(x, y);
        hasStarted = true;
      } else {
        ctx.lineTo(x, y);
      }
    }

    ctx.stroke();
  });
}

let buttons = document.querySelectorAll(".button");
buttons.forEach((button) => {
  button.addEventListener("click", () => {
    button_click_effect(button, log);
  });
});

function resetPage() {
  resetTimer();
  const jack_state = document.getElementById("jack_state");
  if (jack_state) {
    jack_state.style.backgroundColor = "limegreen";
    jack_state.innerText = "Ready";
  }

  const bau_state = document.getElementById("bau_state");
  if (bau_state) {
    bau_state.style.backgroundColor = "red";
    bau_state.innerText = "ACTIVATED";
  }

  const score = document.getElementById("score");
  if (score) {
    score.innerText = "0";
  }

  const pamis_states = document.getElementById("pami_states");
  if (pamis_states) {
    pamis_states.innerHTML = "";
  }

  const rob = document.querySelector(".rob");
  if (rob) {
    rob.style.transform = `translate(200px, calc(-100vh / 2 + 30px)) rotate(0deg)`;
  }

  const bad = document.querySelector(".bad");
  if (bad) {
    bad.style.transform = `translate(450px, calc(-100vh / 2 + 30px)) rotate(0deg)`;
  }

  init_page();
  resetPidDebugData();
  set_configuration("mode");
  config_data.mode = null;
  config_data.team = null;
}

let x = null;

function resetTimer() {
  const timer = document.getElementById("timer");
  timer.style.backgroundColor = "limegreen";
  timer.innerHTML = "1:40";

  if (x) {
    clearInterval(x);
    x = null;
  }
}

function startTimer() {
  const timer = document.getElementById("timer");
  let countdown = new Date().getTime() + 1000 * 60 + 1000 * 40;

  if (x) {
    clearInterval(x);
    x = null;
  }

  x = setInterval(function () {
    let now = new Date().getTime();
    let distance = countdown - now;

    let minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
    let seconds = Math.floor((distance % (1000 * 60)) / 1000);

    timer.innerHTML = minutes + ":" + seconds;

    if (distance < 0) {
      clearInterval(x);
      x = null;
      timer.innerHTML = "FINISHED";
    } else if (distance < 1000 * 15) {
      timer.style.backgroundColor = "orange";
    }
  }, 1000);
}

function show_console_data(data, add = false) {
  if (add) {
    console_div.innerHTML += data + "<br>";
  } else {
    console_div.innerHTML = data;
  }
  // scroll to bottom if the user is not scrolling up
  if (
    console_div.scrollTop >=
    console_div.scrollHeight - console_div.offsetHeight - 1000
  ) {
    console_div.scrollTop = console_div.scrollHeight;
  }
}
console.scrollTop = console.scrollHeight;

let maki = document.querySelectorAll(".maki");
let plus = document.querySelector("#plus");
let minus = document.querySelector("#minus");
let input = document.querySelector("#input");
let range = document.querySelector("#power");
let current_maki = null;

for (let i = 0; i < maki.length; i++) {
  maki[i].addEventListener("click", () => {
    focus_maki(maki[i]);
  });
}

function focus_maki(c_maki) {
  for (let i = 0; i < maki.length; i++) {
    maki[i].classList.remove("active");
  }
  c_maki.classList.add("active");
  current_maki = c_maki;
  input.value = c_maki.children[0].innerText;
}

input.addEventListener("input", () => {
  if (current_maki != null) {
    let value = parseFloat(input.value);
    value = Math.round(value * 100) / 100;
    if (isNaN(value)) {
      value = 0;
    }
    input.value = value;
    current_maki.children[0].innerText = value;
  } else {
    input.value = "";
  }
});

plus.addEventListener("click", () => {
  if (current_maki != null) {
    let value = parseFloat(input.value);
    value += parseFloat(range.value);
    value = Math.round(value * 100) / 100;
    if (isNaN(value)) {
      value = 0;
    }
    input.value = value;
    current_maki.children[0].innerText = value;
  }
});

minus.addEventListener("click", () => {
  if (current_maki != null) {
    let value = parseFloat(input.value);
    value -= parseFloat(range.value);
    value = Math.round(value * 100) / 100;
    if (isNaN(value)) {
      value = 0;
    }
    input.value = value;
    current_maki.children[0].innerText = value;
  }
});

function set_configuration(step) {
  if (step === "mode") {
    document.getElementById("mode_selection").style.display = "grid";
    document.getElementById("team_selection").style.display = "none";
    document.getElementById("configuration_finished").style.display = "none";
  } else if (step === "team") {
    document.getElementById("mode_selection").style.display = "none";
    document.getElementById("team_selection").style.display = "grid";
    document.getElementById("configuration_finished").style.display = "none";
  } else {
    document.getElementById("mode_selection").style.display = "none";
    document.getElementById("team_selection").style.display = "none";
    document.getElementById("configuration_finished").style.display = "grid";
    document.getElementById("config_mode").innerText = config_data.mode;
    document.getElementById("config_team").innerText = config_data.team;
  }
}

window.addEventListener("resize", drawPidCharts);
resetPidDebugData();
