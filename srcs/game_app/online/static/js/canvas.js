document.addEventListener("DOMContentLoaded", function () {
	const canvas = document.getElementById("gameCanvas");
	const ctx = canvas.getContext("2d");
	
	// const startBtn = document.getElementById("start-btn");
	const pauseBtn = document.getElementById("pause-btn");
	const restartBtn = document.getElementById("restart-btn");

	var animationId;
	var gameRunning = false;

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

	var wPressed = false;
	var sPressed = false;
	var opponentWPressed = false;
	var opponentSPressed = false;

	// socket info 
	var ws;
	var playerId;
	var playerDirection; // will be 1 or -1, this will be multiplied with ballSpeedXaxis 

	function countdown(parent, callback) {
		var texts = ['Match found!', '3', '2', '1', 'GO'];
		
		// This will store the paragraph we are currently displaying
		var paragraph = null;
		
		// This is the function we will call every 1000 ms using setInterval
		function count() {
			if (paragraph) {
				paragraph.remove();
			}
			if (texts.length === 0) {
				// If we ran out of text, use the callback to get started
				clearInterval(interval);
				callback();
				return;
			}
			// Trim array
			var text = texts.shift();
			
			// Create a paragraph to add to the DOM
			// This new paragraph will trigger an animation
			paragraph = document.createElement("div");
			paragraph.textContent = text;
			paragraph.className = text + " nums";
			parent.appendChild(paragraph);
		}
		// Initiate an interval, but store it in a variable so we can remove it later.
		var interval = setInterval( count, 1000 );  
	}
	
	function startGame() {
		countdown( document.getElementById("readyGo"), animateGame);
		// {
			// document.getElementById("readyGo").innerHTML = '<p class="nums">GO</p>';
			// console.log("game started");
			// if (!gameRunning) {
			// 	gameRunning = true;
			// 	animateGame();
			// }
		// });	
	}

	// startBtn.addEventListener("click", function()
	// {
	// 	if (!gameRunning) {
	// 		gameRunning = true;
	// 		initializeGame();
	// 	}
	// });

	pauseBtn.addEventListener("click", function()
	{
		ws.close();
		console.log("stopped game");
		gameRunning = false;
		cancelAnimationFrame(animationId);
	});
	
	restartBtn.addEventListener("click", function()
	{
		ws.close();
		cancelAnimationFrame(animationId);
		document.location.reload();
	});

	function isOpen(ws) { return ws.readyState === ws.OPEN }

	const handleWebSocketMessage = (event) => {
		const messageData = JSON.parse(event.data);
		if (messageData.type === "stateUpdate") {
			console.log("status update");
			opponentWPressed = messageData.objects.movingUp;
			opponentSPressed = messageData.objects.movingDown;
		} 
		else if (messageData.type === "playerId") {
			playerId = messageData.playerId;
			console.log("your player id is ", playerId);
		}
		else if (messageData.type === "matchStatus") {
			console.log("match status received: ", messageData.status);
			if (messageData.status)
			{
				countdown( document.getElementById("readyGo"), animateGame);
				ballSpeedXaxis *= messageData.playerDirection
			}
		}		
	};


	function sendKeyUpdate(key, keyDown)
	{
		if (isOpen(ws)) {
			ws.send(
				JSON.stringify({ 
					key: key,
					keyDown: keyDown,
					playerId: playerId
				})
			);
		}
	}

	function keyDownHandler(e)
	{
		if (e.key === "w" && !wPressed)
		{
			wPressed = true;
			sendKeyUpdate(e.key, true);
		}
		else if (e.key === "s" && !sPressed)
		{
			sPressed = true;
			sendKeyUpdate(e.key, true);
		}
	}

	// Key release
	function keyUpHandler(e)
	{
		if (e.key === "w" && wPressed)
		{
			wPressed = false;
			sendKeyUpdate(e.key, false);
		}
		else if (e.key === "s" && sPressed)
		{
			sPressed = false;
			sendKeyUpdate(e.key, false);
		}
	}

	const animateGame = (time) => {
		update();
		draw();
		// Start the animation loop
		animationId = requestAnimationFrame(animateGame);
	};

	// Reset ball
	const reset = () => {
		ballXaxis = canvas.width / 2;
		ballYaxis = canvas.height / 2;
		// ballSpeedXaxis = -ballSpeedXaxis;
		// ballSpeedYaxis = -ballSpeedYaxis;
	}

	// Update game state
	const update = () => {
		// Opponent paddle movement
		if (opponentWPressed && rightPaddleYaxis > 0)
			rightPaddleYaxis -= paddleSpeed;
		else if (opponentSPressed && rightPaddleYaxis + paddleHeight < canvas.height)
			rightPaddleYaxis += paddleSpeed;

		// Move right paddle based on "w" and "s" keys
		if (wPressed && leftPaddleYaxis > 0)
			leftPaddleYaxis -= paddleSpeed;
		else if (sPressed && leftPaddleYaxis + paddleHeight < canvas.height)
			leftPaddleYaxis += paddleSpeed;

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
			alert("Left wins!")
		else if (rightPlayerScore === maxScore)
			alert("Right wins!")
	}

	const draw = () => {
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
	// Entrypoint
	const joinQueue = () => {
		// Implement the initialization logic...

		// Set up WebSocket connection
		ws = new WebSocket("ws://localhost:2000/ws/game/");
		ws.onmessage = handleWebSocketMessage;

		// Keyboard events
		document.addEventListener("keydown", keyDownHandler);
		document.addEventListener("keyup", keyUpHandler);
		// animateGame();
		// Resize canvas on load and window resize
		// resizeCanvas();
		// window.addEventListener("resize", resizeCanvas);
	};
	draw();
	joinQueue();
});
