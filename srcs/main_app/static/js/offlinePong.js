offlineGame = () => {
  // Initialize canvas
  var canvas = document.getElementById("canvas");
  var ctx = canvas.getContext("2d");

  var startBtn = document.getElementById("start-btn");
  var pauseBtn = document.getElementById("pause-btn");
  var restartBtn = document.getElementById("restart-btn");
  var animationId;
  var gameRunning = false;

  startBtn.addEventListener("click", function () {
    if (!gameRunning) {
      gameRunning = true;
      loop();
    }
  });

  pauseBtn.addEventListener("click", function () {
    gameRunning = false;
    cancelAnimationFrame(animationId);
  });

  restartBtn.addEventListener("click", function () {
    document.location.reload();
  });

  const paddleHScale = 0.2
	const paddleWScale = 0.015

  const canvasW = canvas.getBoundingClientRect().width;
	const canvasH = canvas.getBoundingClientRect().height;
	canvas.width = canvasW;
	canvas.height = canvasH;
	console.log("canvas w and h = ", canvasW, canvasH)

  // Paddles
  var paddleHeight = Math.floor(canvasH * paddleHScale);
	var paddleWidth = Math.floor(canvasW * paddleWScale);
	var leftPaddleYaxis = Math.floor(canvasH / 2 - paddleHeight / 2);
	var rightPaddleYaxis = Math.floor(canvasH / 2 - paddleHeight / 2);
	var paddleSpeed = canvasH * 0.01;

  // Ball
	var ballXaxis = Math.floor(canvasW / 2);
	var ballYaxis = Math.floor(canvasH / 2);
	var ballRadius = paddleWidth;
	var ballSpeed = canvasW * 0.006;
	var ballSpeedXaxis = ballSpeed;
	var ballSpeedYaxis = ballSpeed;


  // Score
  var leftPlayerScore = 0;
  var rightPlayerScore = 0;
  var maxScore = 3;

  // Keyboard events
  document.addEventListener("keydown", keyDownHandler);
  document.addEventListener("keyup", keyUpHandler);

  // Key press
  var upPressed = false;
  var downPressed = false;
  var wPressed = false;
  var sPressed = false;

  function keyDownHandler(e) {
    if (e.key === "ArrowUp") upPressed = true;
    else if (e.key === "ArrowDown") downPressed = true;
    else if (e.key === "w") wPressed = true;
    else if (e.key === "s") sPressed = true;
  }

  // Key release
  function keyUpHandler(e) {
    if (e.key === "ArrowUp") upPressed = false;
    else if (e.key === "ArrowDown") downPressed = false;
    else if (e.key === "w") wPressed = false;
    else if (e.key === "s") sPressed = false;
  }

  // Update game state
  function update() {
    // Left Paddle movement
    if (wPressed && leftPaddleYaxis > 0) {
      leftPaddleYaxis -= paddleSpeed;
    }
    else if (sPressed && leftPaddleYaxis + paddleHeight < canvasH) {
      leftPaddleYaxis += paddleSpeed;
    }
  
    // Right Paddle movement
    if (upPressed && rightPaddleYaxis > 0) {
      rightPaddleYaxis -= paddleSpeed;
    }
    else if (downPressed && rightPaddleYaxis + paddleHeight < canvasH) {
      rightPaddleYaxis += paddleSpeed;
    }

    // Move ball
    ballXaxis += ballSpeedXaxis;
    ballYaxis += ballSpeedYaxis;

    // Top & bottom collision
    if (ballYaxis - ballRadius <= 0 || 
        ballYaxis + ballRadius >= canvasH) {
          ballSpeedYaxis = -ballSpeedYaxis;
    }

    // Left paddle collision
    if (ballXaxis - ballRadius <= paddleWidth &&
        ballYaxis >= leftPaddleYaxis &&
        ballYaxis <= leftPaddleYaxis + paddleHeight) {
          ballSpeedXaxis = -ballSpeedXaxis;
    }

    // Right paddle collision
    if (ballXaxis + ballRadius >= canvasW - paddleWidth &&
        ballYaxis >= rightPaddleYaxis &&
        ballYaxis <= rightPaddleYaxis + paddleHeight) {
          ballSpeedXaxis = -ballSpeedXaxis;
    }

    // Check if ball goes out of bounds on left or right side of canvas
    if (ballXaxis - ballRadius <= 0) {
      rightPlayerScore++;
      reset();
    } else if (ballXaxis + ballRadius >= canvasW) {
      leftPlayerScore++;
      reset();
    }

    // Check if a player has won
    // This will be modified to know if you are player one or two and then decide to output win / lose accordingly
    if (leftPlayerScore === maxScore || rightPlayerScore === maxScore) gameRunning = false;
  }

  // Reset ball
  function reset() {
    ballXaxis = canvasW / 2;
    ballYaxis = canvasH / 2;
    ballSpeedXaxis = -ballSpeedXaxis;
    ballSpeedYaxis = -ballSpeedYaxis;
  }

  // Draw objects on canvas
  function draw() {
    // Clear canvas
		ctx.clearRect(0, 0, canvasW, canvasH);

		//Draw middle line
		const color2 = "#57f2e5"
		const color1 = "#FFB3CB"

		ctx.strokeStyle = color1;
		ctx.beginPath();
		ctx.moveTo(canvasW / 2, 0);
		ctx.lineTo(canvasW / 2, canvasH);
		
		// ctx.strokeStyle = "#FFB3CB";
		ctx.stroke();
		ctx.closePath();
		
		//Draw ball
		ctx.fillStyle = color2;
		ctx.beginPath();
		ctx.arc(ballXaxis, ballYaxis, ballRadius, 0, Math.PI * 2);
		ctx.fill();
		ctx.closePath();
		
		//Draw left paddle
		ctx.fillStyle = color1;
		ctx.fillRect(0, leftPaddleYaxis, paddleWidth, paddleHeight);

		//Draw right paddle
		ctx.fillRect(canvasW - paddleWidth, rightPaddleYaxis, paddleWidth, paddleHeight);
    //Draw scores
    ctx.fillText("Score: " + leftPlayerScore, 10, 20);
    ctx.fillText("Score: " + rightPlayerScore, canvasW - 70, 20);
  }

  function endGame() {
    cancelAnimationFrame(animationId);
    if (leftPlayerScore === maxScore)
      alert("Left wins!");
    else
      alert("Right wins!");
    engine('/cards');

  }
  //Main loop
  function loop() {
    if (gameRunning) {
      update();
      draw();
      //Set animation for all frames to appear and be visible
        animationId = requestAnimationFrame(loop);
    }
    else {
      endGame();
    }
  }
  draw();

  offlineGame.destroy = () => {
    document.removeEventListener("keydown", keyDownHandler);
    document.removeEventListener("keyup", keyUpHandler);
    cancelAnimationFrame(animationId);
  };
};
offlineGame();
