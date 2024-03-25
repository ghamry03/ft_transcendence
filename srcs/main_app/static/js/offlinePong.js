offlineGame = () => {
  // Initialize canvas
  const canvas = document.getElementById("canvas");
  const ctx = canvas.getContext("2d");

  const startBtn = document.getElementById("start-btn");
  const pauseBtn = document.getElementById("pause-btn");
  const leftUpButton = document.getElementById("leftUpButton");
  const leftDownButton = document.getElementById("leftDownButton");
  const rightUpButton = document.getElementById("rightUpButton");
  const rightDownButton = document.getElementById("rightDownButton");
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

  const paddleHScale = 0.2
	const paddleWScale = 0.015

  const canvasW = canvas.getBoundingClientRect().width;
	const canvasH = canvas.getBoundingClientRect().height;
	canvas.width = canvasW;
	canvas.height = canvasH;

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
  var maxScore = 8;

  // Keyboard events
  document.addEventListener("keydown", keyDownHandler);
  document.addEventListener("keyup", keyUpHandler);

  // Key press
  var rightUpPressed = false;
  var rightDownPressed = false;
  var leftUpPressed = false;
  var leftDownPressed = false;

  // Handler function for left up button touch start
  function handleLeftUpTouchStart() {
    leftUpPressed = true;
  }

  // Handler function for left up button touch end
  function handleLeftUpTouchEnd() {
    leftUpPressed = false;
  }

  // Handler function for left down button touch start
  function handleLeftDownTouchStart() {
    leftDownPressed = true;
  }

  // Handler function for left down button touch end
  function handleLeftDownTouchEnd() {
    leftDownPressed = false;
  }

  // Handler function for right up button touch start
  function handleRightUpTouchStart() {
    rightUpPressed = true;
  }

  // Handler function for right up button touch end
  function handleRightUpTouchEnd() {
    rightUpPressed = false;
  }

  // Handler function for right down button touch start
  function handleRightDownTouchStart() {
    rightDownPressed = true;
  }

  // Handler function for right down button touch end
  function handleRightDownTouchEnd() {
    rightDownPressed = false;
  }

  // Adding event listeners with the handler functions
  leftUpButton.addEventListener("touchstart", handleLeftUpTouchStart);
  leftUpButton.addEventListener("touchend", handleLeftUpTouchEnd);

  leftDownButton.addEventListener("touchstart", handleLeftDownTouchStart);
  leftDownButton.addEventListener("touchend", handleLeftDownTouchEnd);

  rightUpButton.addEventListener("touchstart", handleRightUpTouchStart);
  rightUpButton.addEventListener("touchend", handleRightUpTouchEnd);

  rightDownButton.addEventListener("touchstart", handleRightDownTouchStart);
  rightDownButton.addEventListener("touchend", handleRightDownTouchEnd);


  function keyDownHandler(e) {
    if (e.key === "ArrowUp") rightUpPressed = true;
    else if (e.key === "ArrowDown") rightDownPressed = true;
    else if (e.key === "w") leftUpPressed = true;
    else if (e.key === "s") leftDownPressed = true;
  }

  // Key release
  function keyUpHandler(e) {
    if (e.key === "ArrowUp") rightUpPressed = false;
    else if (e.key === "ArrowDown") rightDownPressed = false;
    else if (e.key === "w") leftUpPressed = false;
    else if (e.key === "s") leftDownPressed = false;
  }

  // Update game state
  function update() {
    // Left Paddle movement
    if (leftUpPressed && leftPaddleYaxis > 0) {
      leftPaddleYaxis -= paddleSpeed;
    }
    else if (leftDownPressed && leftPaddleYaxis + paddleHeight < canvasH) {
      leftPaddleYaxis += paddleSpeed;
    }
  
    // Right Paddle movement
    if (rightUpPressed && rightPaddleYaxis > 0) {
      rightPaddleYaxis -= paddleSpeed;
    }
    else if (rightDownPressed && rightPaddleYaxis + paddleHeight < canvasH) {
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
    leftUpButton.removeEventListener("touchstart", handleLeftUpTouchStart);
    leftUpButton.removeEventListener("touchend", handleLeftUpTouchEnd);
    leftDownButton.removeEventListener("touchstart", handleLeftDownTouchStart);
    leftDownButton.removeEventListener("touchend", handleLeftDownTouchEnd);
    rightUpButton.removeEventListener("touchstart", handleRightUpTouchStart);
    rightUpButton.removeEventListener("touchend", handleRightUpTouchEnd);
    rightDownButton.removeEventListener("touchstart", handleRightDownTouchStart);
    rightDownButton.removeEventListener("touchend", handleRightDownTouchEnd);

    cancelAnimationFrame(animationId);
  };
};
offlineGame();
