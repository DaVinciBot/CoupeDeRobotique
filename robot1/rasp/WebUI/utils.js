class WebSocketManager {
  #status = "disconnected";

  constructor(host = "localhost", port = "8080", user = "ui") {
    this.websockets = {};
    this.host = host;
    this.port = port;
    this.user = user;

    const ws_status = document.getElementById("websocket_status");
    const website = document.getElementById("website");
    if (ws_status && website) {
      ws_status.style.display = "flex";
      website.style.display = "none";
    }
  }

  get status() {
    return this.#status;
  }
  set status(newStatus) {
    this.#status = newStatus;
    const ws_status = document.getElementById("websocket_status");
    const website = document.getElementById("website");
    if (!ws_status || !website) return;
    if (newStatus === "connected") {
      init_page();
      ws_status.style.display = "none";
      website.style.display = "grid";
    } else {
      ws_status.style.display = "flex";
      website.style.display = "none";
    }
  }

  #create_trame(msg, data, usr = this.user) {
    let ts = Date.now();
    return JSON.stringify({ usr, msg, data, ts });
  }

  #ws_connect(route) {
    return new WebSocket(
      `ws://${this.host}:${this.port}/${route}?sender=${this.user}`
    );
  }

  add_ws(route, { onopen, onmessage, onclose, onerror } = {}) {
    const ws = this.#ws_connect(route);

    if (onopen) ws.addEventListener("open", onopen);
    if (onmessage) ws.addEventListener("message", onmessage);
    if (onclose) ws.addEventListener("close", onclose);
    if (onerror) ws.addEventListener("error", onerror);

    ws.addEventListener("open", () => {
      console.log(`${route} connected !`);
      ws.send(this.#create_trame("hello", {}, "ui"));
    });
    ws.addEventListener("close", (e) => {
      console.log(`${route} closed`, e.code, e.reason);
      this.status = "disconnected";
    });
    ws.addEventListener("error", (e) => console.error(`${route} error`, e));

    this.websockets[route] = ws;
    return ws;
  }

  add_handler(route, handler) {
    this.websockets[route]?.addEventListener("message", handler);
  }

  on_ws_close(route, handler) {
    this.websockets[route]?.addEventListener("close", handler);
  }

  on_ws_error(route, handler) {
    this.websockets[route]?.addEventListener("error", handler);
  }

  update_status(status) {
    this.status = status;
  }

  send(route, msg, data) {
    const ws = this.websockets[route];
    if (!ws) throw new Error(`WS ${route} inexistante`);
    if (ws.readyState !== WebSocket.OPEN) {
      throw new Error(`WS ${route} non ouverte (readyState=${ws.readyState})`);
    }
    ws.send(this.#create_trame(msg, data));
  }
}

// change background color of button during .05s when clicked
function button_click_effect(button, server) {
  let originalColor = button.style.backgroundColor;
  button.style.backgroundColor = "#0232FF";
  setTimeout(() => {
    button.style.backgroundColor = originalColor;
  }, 50);
  if (button.id.includes("_team")) {
    button.style.backgroundColor = "#FFFFFF";
    let team = "other";
    if (button.id === "blue_team") {
      team = "blue";
    } else if (button.id === "yellow_team") {
      team = "yellow";
    }
    config_data.team = team;
    server.send("ui", "team change", { team: team });
  }
  if (button.id.includes("_mode")) {
    button.style.backgroundColor = "#FFFFFF";
    let mode = "unknown";
    if (button.id === "normal_mode") {
      mode = "normal";
    } else if (button.id === "iihm_mode") {
      mode = "iihm";
    }
    server.send("ui", "mode change", { mode: mode });
  }
  if (button.id.includes("send_coords")) {
    let x = parseFloat(
      document.getElementById("x_coord").querySelector(".value").innerText
    );
    let y = parseFloat(
      document.getElementById("y_coord").querySelector(".value").innerText
    );
    let theta = parseFloat(
      document.getElementById("theta_coord").querySelector(".value").innerText
    );
    theta = (theta * Math.PI) / 180.0; // convert to radians
    while (theta > Math.PI) theta -= 2 * Math.PI; // normalize between -pi and pi
    while (theta < -Math.PI) theta += 2 * Math.PI; // normalize between -pi and pi
    server.send("ui", "action", {
      type: "go to point",
      data: { x: x, y: y, theta: theta },
    });
  }
  if (button.id.includes("_pid")) {
    let kp = parseFloat(
      document.getElementById("kp").querySelector(".value").innerText
    );
    let ki = parseFloat(
      document.getElementById("ki").querySelector(".value").innerText
    );
    let kd = parseFloat(
      document.getElementById("kd").querySelector(".value").innerText
    );
    if (button.id.includes("linear")) {
      server.send("ui", "pid update", {
        type: "linear_position",
        data: { kp: kp, ki: ki, kd: kd },
      });
    } else if (button.id.includes("angular")) {
      server.send("ui", "pid update", {
        type: "angular_position",
        data: { kp: kp, ki: ki, kd: kd },
      });
    } else if (button.id.includes("left_wheel")) {
      server.send("ui", "pid update", {
        type: "left_wheel_position",
        data: { kp: kp, ki: ki, kd: kd },
      });
    } else if (button.id.includes("right_wheel")) {
      server.send("ui", "pid update", {
        type: "right_wheel_position",
        data: { kp: kp, ki: ki, kd: kd },
      });
    }
  }
  if (button.id.includes("send_action")) {
    let action = document.querySelector('input[name="action"]:checked').value;
    let actionName = document.querySelector('input[name="action"]:checked')
      .nextElementSibling.innerText;
    server.send("ui", "action", { type: action, name: actionName });
  }
}

let currentPage = "main";
function set_page(page_id) {
  hide_all_pages();
  document.getElementById(page_id).style.display = "grid";
  document.getElementById(page_id + "_menu").classList.add("active");
  currentPage = page_id;
  if (typeof drawPidCharts === "function") {
    drawPidCharts();
  }
}
function hide_all_pages() {
  let pagesButton = document.querySelectorAll(".item_menu");
  let pages = document.querySelectorAll(".content");
  pagesButton.forEach((pageButton) => {
    pageButton.classList.remove("active");
  });
  pages.forEach((page) => {
    page.style.display = "none";
  });
}
function init_page() {
  currentPage = "main";
  set_page("main");
}
document.onload = init_page();
