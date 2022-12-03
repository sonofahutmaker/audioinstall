let windchimes = [];
let machines = [];
let currentSound;
let drawI = 0;
let machineSound;
let devProximity = 100;

function preload() {
  // getAudioContext().resume();
  soundFormats('mp3', 'wav');
  
  let chimePath = "static/sounds/nature/0.mp3";
  windchimes[0] = loadSound(chimePath)
  currentSound = windchimes[0]
  
  let machinePath = "static/sounds/machines/2.mp3"
  machines[0] = loadSound(machinePath)
  machineSound = machines[0]
}

function setup() {
  // getAudioContext().resume();
  let cnv = createCanvas(windowWidth, windowHeight);
  background(200, 25, 50);
  cnv.mousePressed(canvasPressed);

}

function touchStarted() {
  getAudioContext().resume();
}

function draw() {
  // let glitchPerc = getXPerc();
  let glitchPerc = getProximityFromDevice();
  
  console.log("glitchPerc: ", glitchPerc)
  let division = floor(100/glitchPerc);
  if (drawI%division==0 && glitchPerc < 51) {
     console.log("called glitch at: ", drawI);
     soundJump(currentSound);
  } else if (glitchPerc > 50) {
    let glitchPercNew = glitchPerc - 50;
    let divisionNew = 2*floor(100/glitchPercNew);
    if (drawI%divisionNew==0) { 
    //   console.log("called machine glitch at: ", drawI);
      playMachineSound(glitchPercNew);
    }
  }
  
  drawI++;
  drawI = drawI%100;
}

function soundJump(mySound) {
  machineSound.pause();
  mySound.play();
  let soundLen = mySound.duration();
  let start = random(0, soundLen);
  let duration = soundLen - start;
  mySound.jump(start, duration);
}

function soundJumpWithDuration(mySound, duration) {
  mySound.play();
  mySound.loop();
  let soundLen = mySound.duration();
  let start = random(0, soundLen);
  if (start+duration >= soundLen) {
    duration = soundLen - start;
  }
  mySound.jump(start, duration); 
}

function playMachineSound(glitchPerc) { 
  currentSound.pause();
  let soundLen = currentSound.duration();
  let start = random(0, soundLen);
  let duration = soundLen - start;
  
  machineDuration = duration * (glitchPerc * 0.01);
  chimesDuration = duration - machineDuration;
  
  soundJumpWithDuration(machineSound, machineDuration);
  
  soundJumpWithDuration(currentSound, chimesDuration);
  
  // setTimeout(() => {
  //   soundJumpWithDuration(currentSound, chimesDuration);
  // }, machineDuration*1000)
}

function getXPerc() {
  return ceil(mouseX*100/windowWidth);
}

function canvasPressed() {
  getAudioContext().resume();
  currentSound.play();
  currentSound.setLoop(true);
}

function getProximityFromDevice() {
  devProximity = localStorage.getItem("proximity"); 
  if (devProximity > 100) {
    return 0;
  } else {
    return 100 - devProximity;
  }
}