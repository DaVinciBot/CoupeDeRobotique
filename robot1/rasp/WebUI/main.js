// let console_div = document.getElementById('log');

let config_data = {
  mode: null,
  team: null,
}

let log = new WebSocketManager();
log.add_ws("ui");
function on_ws_close() {
  log.on_ws_close("ui", async () => {
    resetPage();
    log.update_status("disconnected");
    console.log("Websocket closed, attempting to reconnect...");
    const intervalId = setInterval(async () => {
      try {
        if(log.status === "connected"){
          clearInterval(intervalId);
          on_ws_close();
        }else{
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
      if(jack_state){
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
      if(info_coords){
        info_coords.innerText = `${data.data["odometrie"].x.toFixed(2)}, ${data.data["odometrie"].y.toFixed(2)}, ${((normalize_angle(data.data["odometrie"].theta) * 180) / Math.PI).toFixed(2)}°`;
      }

      const bau_state = document.getElementById("bau_state");
      if(bau_state){
        bau_state.style.backgroundColor = data.data["BAU"] ? "limegreen" : "red";
        bau_state.innerText = data.data["BAU"] ? "ON" : "ACTIVATED";
      }

      const score = document.getElementById("score");
      if(score){
        score.innerText = data.data["score"] ? data.data["score"] : "0";
      }

      const pamis_states = document.getElementById("pami_states");
      if(pamis_states){
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
      if(rob){
        let x = data.data["odometrie"].x;
        let y = data.data["odometrie"].y;
        let theta = data.data["odometrie"].theta;
        let width = data.data["arena_info"].width;
        let height = data.data["arena_info"].height;

        [x, y, theta] = parse_pos(x, y, theta, width, height);

        rob.style.transform = `translate(${x}px, ${y}px) rotate(${theta}deg)`;
      }

      const bad = document.querySelector(".bad");
      if(bad){
        let x = data.data["enemy_odometrie"].x;
        let y = data.data["enemy_odometrie"].y;
        let theta = data.data["enemy_odometrie"].theta;
        let width = data.data["arena_info"].width;
        let height = data.data["arena_info"].height;

        [x, y, theta] = parse_pos(x, y, theta, width, height);

        bad.style.transform = `translate(${x}px, ${y}px) rotate(${theta}deg)`;
      }
    }else if(data.msg === "starting"){
      startTimer();
      const timer = document.getElementById("timer");
      timer.style.backgroundColor = "limegreen";
      set_configuration("finished");
    }else if(data.msg === "initializing"){
      const timer = document.getElementById("timer");
      timer.style.backgroundColor = "grey";
      timer.innerHTML = "Init...";
      set_configuration("finished");
    }else if(data.msg === "status"){
      let status = data.data.status;
      let info = data.data.data;
      log.update_status("connected");

      if(status === "starting"){
        startTimer();
        const timer = document.getElementById("timer");
        timer.style.backgroundColor = "limegreen";
        config_data.mode = info.mode;
        config_data.team = info.team;
        set_configuration("finished");
      }else if(status === "initializing"){
        const timer = document.getElementById("timer");
        timer.style.backgroundColor = "grey";
        timer.innerHTML = "Init...";
        config_data.mode = info.mode;
        config_data.team = info.team;
        set_configuration("finished");
      }else if(status === "waiting for mode"){
        set_configuration("mode");
      }else if(status === "waiting for team color"){
        set_configuration("team");
        config_data.mode = info.mode;
      }
    }else if(data.msg === "mode set"){
      set_configuration("team");
      config_data.mode = data.data.mode;
    }
  })
};
add_handler();

function normalize_angle(angle) {
  angle = (angle + Math.PI) % (2 * Math.PI);
  if (angle < 0) {
    angle += 2 * Math.PI;
  }
  return angle - Math.PI;
}

function parse_pos(x, y, theta, width, height) {
  const mapWidth = document.querySelector('.map').clientWidth;
  const mapHeight = document.querySelector('.map').clientHeight;

  x = x / width * mapWidth;
  y =  -(y / height * mapHeight);
  theta = -(normalize_angle(theta - Math.PI / 2) * 180) / Math.PI;
  return [x, y, theta];
}

let buttons = document.querySelectorAll(".button");
buttons.forEach((button) => {
  button.addEventListener("click", () => {
    button_click_effect(button, log);
  });
});

function resetPage(){
  resetTimer();
  const jack_state = document.getElementById("jack_state");
  if(jack_state){
    jack_state.style.backgroundColor = "limegreen";
    jack_state.innerText = "Ready";
  }

  const bau_state = document.getElementById("bau_state");
  if(bau_state){
    bau_state.style.backgroundColor = "red";
    bau_state.innerText = "ACTIVATED";
  }

  const score = document.getElementById("score");
  if(score){
    score.innerText = "0";
  }

  const pamis_states = document.getElementById("pami_states");
  if(pamis_states){
    pamis_states.innerHTML = "";
  }

  const rob = document.querySelector(".rob");
  if(rob){
    rob.style.transform = `translate(200px, calc(-100vh / 2 + 30px)) rotate(0deg)`;
  }
  
  const bad = document.querySelector(".bad");
  if(bad){
    bad.style.transform = `translate(450px, calc(-100vh / 2 + 30px)) rotate(0deg)`;
  }

  init_page();
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
    if(isNaN(value)){
      value = 0;
    }
    input.value = value;
    current_maki.children[0].innerText = value;
  }else{
    input.value = "";
  }
})

plus.addEventListener("click", () => {
  if (current_maki != null) {
    let value = parseFloat(input.value);
    value += parseFloat(range.value);
    value = Math.round(value * 100) / 100;
    if(isNaN(value)){
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
    if(isNaN(value)){
      value = 0;
    }
    input.value = value;
    current_maki.children[0].innerText = value;
  }
});

function set_configuration(step){
  if(step === "mode"){
    document.getElementById("mode_selection").style.display = "grid";
    document.getElementById("team_selection").style.display = "none";
    document.getElementById("configuration_finished").style.display = "none";
  }else if(step === "team"){
    document.getElementById("mode_selection").style.display = "none";
    document.getElementById("team_selection").style.display = "grid";
    document.getElementById("configuration_finished").style.display = "none";
  }else{
    document.getElementById("mode_selection").style.display = "none";
    document.getElementById("team_selection").style.display = "none";
    document.getElementById("configuration_finished").style.display = "grid";
    document.getElementById("config_mode").innerText = config_data.mode;
    document.getElementById("config_team").innerText = config_data.team;
  }
}