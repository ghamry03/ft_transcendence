	const canvas = document.getElementById("gameCanvas");
	const ctx = canvas.getContext("2d");
	const playerId = canvas.getAttribute("uid");

	const paddleHScale = 0.2
	const paddleWScale = 0.015
	const remoteCanvasH = 510;

	var animationId;
	// var gameRunning = false;

	const canvasW = canvas.getBoundingClientRect().width;
	const canvasH = canvas.getBoundingClientRect().height;

	canvas.width = canvasW;
	canvas.height = canvasH;
	var scaleFactor = canvasH / remoteCanvasH;
	
	// Paddles
	var paddleHeight = canvasH * paddleHScale;
	var paddleWidth = canvasW * paddleWScale;
	var leftPaddleYaxis = canvasH / 2 - paddleHeight / 2;
	var rightPaddleYaxis = canvasH / 2 - paddleHeight / 2;
	
	// Ball
	var ballXaxis = canvasW / 2;
	var ballYaxis = canvasH / 2;
	var ballRadius = paddleWidth;

	console.log("canvas height and width = ", canvasH, canvasW);
	// Score
	var leftPlayerScore = 0;
	var rightPlayerScore = 0;
	var maxScore = 10;

	var wPressed = false;
	var sPressed = false;

	// socket info 
	var ws;
	// var playerId;

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

	// pauseBtn.addEventListener("click", function()
	// {
	// 	ws.close();
	// 	console.log("stopped game");
	// 	// gameRunning = false;
	// 	cancelAnimationFrame(animationId);
	// });
	
	// restartBtn.addEventListener("click", function()
	// {
	// 	ws.close();
	// 	cancelAnimationFrame(animationId);
	// 	document.location.reload();
	// });

	function isOpen(ws) { return ws.readyState === ws.OPEN }

	const handleWebSocketMessage = (event) => {
		const messageData = JSON.parse(event.data);
		if (messageData.type === "stateUpdate") {
			console.log("status update");
			ballXaxis = messageData.ballX * scaleFactor;
			ballYaxis = messageData.ballY * scaleFactor;
			leftPaddleYaxis = messageData.leftPaddle * scaleFactor;
			rightPaddleYaxis = messageData.rightPaddle * scaleFactor;
			leftPlayerScore = messageData.leftScore;
			rightPlayerScore = messageData.rightScore;
		} 
		else if (messageData.type === "inGame") {
			// playerId = messageData.playerId;
			console.log("you're queued or have another ongoing match on another tab or computer", playerId);
			ws.close();
			// show error pop up and redirect them back to home page 
		}
		else if (messageData.type === "matchFound") {
			console.log("match found, first is: ", messageData.first);
			// if (messageData.first == playerId) {
			// 	left = true;
			// 	console.log("i am left");
			// }
			// gameRunning = true;
			countdown(document.getElementById("readyGo"), animateGame);
			// ballSpeedXaxis *= messageData.playerDirection
			if (isOpen(ws)) {
				ws.send(
					JSON.stringify({
						type: "ready",
						playerId: playerId
					})
				);
			}
		}
		else if (messageData.type === "disconnected")
			console.log("opponent has disconnected");
	};

	function sendKeyUpdate(key, keyDown)
	{
		if (isOpen(ws)) {
			ws.send(
				JSON.stringify({
					type: "keypress",
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
		// update();
		draw();
		// Start the animation loop
		// if (gameRunning == true)
			animationId = requestAnimationFrame(animateGame);
	};

	// Reset ball
	const reset = () => {
		ballXaxis = canvasW / 2;
		ballYaxis = canvasH / 2;
		// ballSpeedXaxis = -ballSpeedXaxis;
		// ballSpeedYaxis = -ballSpeedYaxis;
	}

	// Update game state
	const update = () => {
		// // Check if ball goes out of bounds on left or right side of canvas
		if (ballXaxis < 0) 
		{
			rightPlayerScore++;
			// reset();
		}

		else if (ballXaxis > canvasW)
		{
			leftPlayerScore++;
			// reset();
		}

		// Check if a player has won
		// This will be modified to know if you are player one or two and then decide to output win / lose accordingly
		if (leftPlayerScore === maxScore) {
			// gameRunning = false;
			cancelAnimationFrame(animationId);
			alert("Left wins!")
		}
		else if (rightPlayerScore === maxScore) {
			// gameRunning = false;
			cancelAnimationFrame(animationId);
			alert("Right wins!")
		}
	}

	const draw = () => {
		// Clear canvas
		ctx.clearRect(0, 0, canvasW, canvasH);

		//Paddle colors
		ctx.fillStyle = "#0abdc6";
		ctx.font = "30px ps2p";
	
		//Draw middle line
		ctx.beginPath();
		ctx.moveTo(canvasW / 2, 0);
		ctx.lineTo(canvasW / 2, canvasH);
		
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
		ctx.fillRect(canvasW - paddleWidth, rightPaddleYaxis, paddleWidth, paddleHeight);

		//Draw scores
		if (leftPlayerScore < rightPlayerScore) {
			ctx.fillStyle = "#FFB3B3"; // red
			ctx.fillText(leftPlayerScore, canvasW / 2 - 50, 40);
			ctx.fillStyle = "#C5FFC0"; // green
			ctx.fillText(rightPlayerScore, canvasW / 2 + 25, 40);
		}
		else if (leftPlayerScore > rightPlayerScore) {
			ctx.fillStyle = "#C5FFC0";
			ctx.fillText(leftPlayerScore, canvasW / 2 - 50, 40);
			ctx.fillStyle = "#FFB3B3";
			ctx.fillText(rightPlayerScore, canvasW / 2 + 25, 40);
		}
		else {
			ctx.fillStyle = "#C5FFC0";
			ctx.fillText(leftPlayerScore, canvasW / 2 - 50, 40);
			ctx.fillText(rightPlayerScore, canvasW / 2 + 25, 40);
		}
	}
	// Entrypoint
	const joinQueue = () => {
		// Set up WebSocket connection
		ws = new WebSocket("ws://localhost:2000/ws/game/?uid=" + playerId);
		console.log("ws is ", ws);
		ws.onmessage = handleWebSocketMessage;
		console.log("connecting to server with uid ", playerId);
		
		// Keyboard events
		document.addEventListener("keydown", keyDownHandler);
		document.addEventListener("keyup", keyUpHandler);
	};
	draw();
	joinQueue();

