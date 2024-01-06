// Initialize canvas
var canvas = document.getElementById("canvas");
var ctx = canvas.getContext("2d");

var startBtn = document.getElementById("start-btn");
var pauseBtn = document.getElementById("pause-btn");
var restartBtn = document.getElementById("restart-btn");
var animationId;
var gameRunning = false;

startBtn.addEventListener("click", function()
{
  if (!gameRunning) {
    gameRunning = true;
    loop();
  }
});

pauseBtn.addEventListener("click", function()
{
  gameRunning = false;
  cancelAnimationFrame(animationId);
});

restartBtn.addEventListener("click", function()
{
  document.location.reload();
});

addEventListener("load", (event) => {
  draw();
});

// Canvas
var padding = 30;
// var canvasHeight = canvas.height - padding;
// var canvasWidth = canvas.width - padding;

// Ball
var ballRadius = 10;
var ballXaxis = canvas.width / 2;
var ballYaxis = canvas.height / 2;
var ballSpeedXaxis = 5;
var ballSpeedYaxis = 5;

// Paddles
var paddleHeight = 80;
var paddleWidth = 10;
var leftPaddleYaxis = canvas.height / 2 - paddleHeight / 2;
var rightPaddleYaxis = canvas.height / 2 - paddleHeight / 2;
var paddleSpeed = 5;

// Score
var leftPlayerScore = 0;
var rightPlayerScore = 0;
var maxScore = 10;

// Keyboard events
document.addEventListener("keydown", keyDownHandler);
document.addEventListener("keyup", keyUpHandler);

// Key press
var upPressed = false;
var downPressed = false;
var wPressed = false;
var sPressed = false;

function keyDownHandler(e)
{
  if (e.key === "ArrowUp")
    upPressed = true;
  else if (e.key === "ArrowDown")
    downPressed = true;
  else if (e.key === "w")
    wPressed = true;
  else if (e.key === "s")
    sPressed = true;
}

// Key release
function keyUpHandler(e)
{
  if (e.key === "ArrowUp")
      upPressed = false;
  else if (e.key === "ArrowDown")
      downPressed = false;
  else if (e.key === "w")
      wPressed = false;
  else if (e.key === "s")
      sPressed = false;
}

// Update game state
function update()
{
  // Paddle movement
  if (upPressed && rightPaddleYaxis > 0)
    rightPaddleYaxis -= paddleSpeed;
  else if (downPressed && rightPaddleYaxis + paddleHeight < canvas.height)
    rightPaddleYaxis += paddleSpeed;

  // Move right paddle based on "w" and "s" keys
  if (wPressed && leftPaddleYaxis > 0)
    leftPaddleYaxis -= paddleSpeed;
  else if (sPressed && leftPaddleYaxis + paddleHeight < canvas.height)
    leftPaddleYaxis += paddleSpeed;

  // Move right paddle automatically based on ball position
  if (ballYaxis > rightPaddleYaxis + paddleHeight / 2)
    rightPaddleYaxis += paddleSpeed;
  else if (ballYaxis < rightPaddleYaxis + paddleHeight / 2)
    rightPaddleYaxis -= paddleSpeed;

  // Move ball
  ballXaxis += ballSpeedXaxis;
  ballYaxis += ballSpeedYaxis;

  // Top & bottom collision
  if (ballYaxis - ballRadius < 0 ||
      ballYaxis + ballRadius > canvas.height)
    ballSpeedYaxis = -ballSpeedYaxis;

  // Left paddle collision
  if (ballXaxis - ballRadius < paddleWidth &&
      ballYaxis > leftPaddleYaxis &&
      ballYaxis < leftPaddleYaxis + paddleHeight)
    ballSpeedXaxis = -ballSpeedXaxis;

  // Right paddle collision
  if (ballXaxis + ballRadius > canvas.width - paddleWidth &&
      ballYaxis > rightPaddleYaxis &&
      ballYaxis < rightPaddleYaxis + paddleHeight)
    ballSpeedXaxis = -ballSpeedXaxis;

  // Check if ball goes out of bounds on left or right side of canvas
  if (ballXaxis < 0) 
  {
    rightPlayerScore++;
    reset();
  }

  else if (ballXaxis > canvas.width)
  {
    leftPlayerScore++;
    reset();
  }

  // Check if a player has won
  // This will be modified to know if you are player one or two and then decide to output win / lose accordingly
  if (leftPlayerScore === maxScore)
    playerWin("Left player");
  else if (rightPlayerScore === maxScore)
    playerWin("Right player");
}

// Reset ball
function reset()
{
  ballXaxis = canvas.width / 2;
  ballYaxis = canvas.height / 2;
  ballSpeedXaxis = -ballSpeedXaxis;
  // ballSpeedYaxis = Math.random();

  ballSpeedYaxis = -ballSpeedYaxis;
}

// Draw objects on canvas
function draw()
{
  // Clear canvas
  ctx.clearRect(0, 0, canvas.width, canvas.height);

  //Paddle colors
  ctx.fillStyle = "#0abdc6";
  ctx.font = "15px Arial";

  //Draw middle line
  ctx.beginPath();
  ctx.moveTo(canvas.width / 2, 0);
  ctx.lineTo(canvas.width / 2, canvas.height);
  
  //Set middle line color
  ctx.strokeStyle = "#0abdc6";
  ctx.stroke();
  ctx.closePath();

  //Draw ball
  ctx.beginPath();
  ctx.arc(ballXaxis, ballYaxis, ballRadius, 0, Math.PI * 2);
  ctx.fill();
  ctx.closePath();

  //Draw left paddle
  ctx.fillRect(0, leftPaddleYaxis, paddleWidth, paddleHeight);

  //Draw right paddle
  ctx.fillRect(canvas.width - paddleWidth, rightPaddleYaxis, paddleWidth, paddleHeight);

  //Draw scores
  ctx.fillText("Score: " + leftPlayerScore, 10, 20);
  ctx.fillText("Score: " + rightPlayerScore, canvas.width - 70, 20);
}

//Main loop
function loop()
{
  update();
  draw();
  //Set animation for all frames to appear and be visible
  animationId = requestAnimationFrame(loop);
}
