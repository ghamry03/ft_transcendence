onlineGame = () => {	
	const canvas = document.getElementById("gameCanvas");
	const leftScore = document.getElementById("leftScore");
	const rightScore = document.getElementById("rightScore");
	const ctx = canvas.getContext("2d");
	const playerId = getCookie("uid");
	const token = getCookie("token");
	
	const paddleHScale = 0.2
	const paddleWScale = 0.015
	const remoteCanvasH = 510;
	const padding = 20;
	
	var animationId;

	const canvasW = canvas.getBoundingClientRect().width;
	const canvasH = canvas.getBoundingClientRect().height;

	canvas.width = canvasW;
	canvas.height = canvasH;
	var scaleFactor = canvasH / remoteCanvasH;
	
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
	var maxScore = 10;

	var wPressed = false;
	var sPressed = false;

	// socket info 
	// var ws;
	var leftPlayerId;
	var rightPlayerId;
	var leftPlayerImg;
	var rightPlayerImg;
	var leftWPressed = false;
	var leftSPressed = false;
	var rightWPressed = false;
	var rightSPressed = false;

	function getCookie(cname) {
		let name = cname + "=";
		let decodedCookie = decodeURIComponent(document.cookie);
		let ca = decodedCookie.split(';');
		for(let i = 0; i < ca.length; i++) {
		  let c = ca[i];
		  while (c.charAt(0) == ' ') {
			c = c.substring(1);
		  }
		  if (c.indexOf(name) == 0) {
			return c.substring(name.length, c.length);
		  }
		}
		return "";
	}
	
	async function getImage(ownerUid, targetUid, token) {
		try {
			const response = await fetch('playerInfo/?ownerUid=' + ownerUid + "&targetUid=" + targetUid + "&token=" + token);
			const jsonResponse = await response.json();
			return jsonResponse.image;
		} catch (error) {
			console.error("Error fetching image:", error);
		}
	}
	
	function countdown(parent, callback) {
		var texts = ['Match found!', '3', '2', '1', 'GO'];
		// var texts = ['Match found!'];
		
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

	function isOpen(ws) { return ws.readyState === ws.OPEN }
	
	const handleWebSocketMessage = (event) => {
		const messageData = JSON.parse(event.data);
		if (messageData.type === "keyUpdate") {
			if (messageData.isLeft) {
				if (messageData.key == "w")
					leftWPressed = messageData.keyDown;
				else
					leftSPressed = messageData.keyDown;
			}
			else {
				if (messageData.key == "w")
					rightWPressed = messageData.keyDown;
				else
					rightSPressed = messageData.keyDown;
			}
		}
		if (messageData.type === "scoreUpdate") {
			leftPlayerScore = messageData.leftScore;
			rightPlayerScore = messageData.rightScore;
			reset(ballSpeed * messageData.ballDir);
		}
		else if (messageData.type === "inGame") {
			// console.log("you're queued or have another ongoing match on another tab or computer", playerId);
			ws.close(3001, "Player already in-game");
			alert("You have a game running on another session!");
			// show error pop up and redirect them back to home page 
		}
		else if (messageData.type === "matchFound") {
			leftPlayerId = messageData.left;
			rightPlayerId = messageData.right;
			console.log("Match found, left = ", leftPlayerId, " right = ", rightPlayerId);
			
			countdown(document.getElementById("readyGo"), animateGame);
			var leftImage = document.getElementById("leftImage");
			var rightImage = document.getElementById("rightImage");
			getImage(playerId, leftPlayerId, token)
				.then(imgUrl => {
					leftImage.src = "http://localhost:3000" + imgUrl;
				});
			getImage(playerId, rightPlayerId, token)
				.then(imgUrl => {
					rightImage.src = "http://localhost:3000" + imgUrl;
				});
		}
		else if (messageData.type === "disconnected") {
			reset();
			alert("Opponent disconnected from the game");
			cancelAnimationFrame(animationId);
			// show error pop up and redirect them back to home page 
		}
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
	
	function sendScoredEvent(key, keyDown)
	{
		if (isOpen(ws)) {
			ws.send(
				JSON.stringify({
					type: "playerScored",
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

	function update()
	{
		// Left paddle movement
		if (leftWPressed && leftPaddleYaxis > 0)
			leftPaddleYaxis -= paddleSpeed;
		else if (leftSPressed && leftPaddleYaxis + paddleHeight < canvasH)
			leftPaddleYaxis += paddleSpeed;
		
		// Right paddle movement
		if (rightWPressed && rightPaddleYaxis > 0)
			rightPaddleYaxis -= paddleSpeed;
		else if (rightSPressed && rightPaddleYaxis + paddleHeight < canvasH)
			rightPaddleYaxis += paddleSpeed;

		// Move ball
		ballXaxis += ballSpeedXaxis;
		ballYaxis += ballSpeedYaxis;

		// Top & bottom collision
		if (ballYaxis - ballRadius <= 0 ||
			ballYaxis + ballRadius >= canvasH)
			ballSpeedYaxis = -ballSpeedYaxis;

		// Left paddle collision
		if (ballXaxis - ballRadius <= paddleWidth &&
			ballYaxis >= leftPaddleYaxis &&
			ballYaxis <= leftPaddleYaxis + paddleHeight)
			if (ballSpeedXaxis < 0)
				ballSpeedXaxis = -ballSpeedXaxis;

		// Right paddle collision
		if (ballXaxis + ballRadius >= canvasW - paddleWidth &&
			ballYaxis >= rightPaddleYaxis &&
			ballYaxis <= rightPaddleYaxis + paddleHeight)
			if (ballSpeedXaxis > 0)
				ballSpeedXaxis = -ballSpeedXaxis;

		// Check if ball goes out of bounds on left or right side of canvas
		if (ballXaxis - ballRadius <= 0) {
			if (playerId == rightPlayerId)
				sendScoredEvent();
		}
		else if (ballXaxis + ballRadius >= canvasW) {
			if (playerId == leftPlayerId)
				sendScoredEvent();
		}
	}

	const animateGame = (time) => {
		update();
		draw();
		// Start the animation loop
		animationId = requestAnimationFrame(animateGame);
	};

	// Reset ball
	const reset = (newBallSpeed) => {
		ballXaxis = canvasW / 2;
		ballYaxis = canvasH / 2;
		ballSpeedXaxis = newBallSpeed;
		ballSpeedYaxis = newBallSpeed;
	}

	const draw = () => {
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
		// right is winning
		leftScore.innerText = leftPlayerScore;
		rightScore.innerText = rightPlayerScore;
		if (leftPlayerScore < rightPlayerScore) {
			leftScore.style.color = "#FFB3B3";
		}
		if (rightPlayerScore < leftPlayerScore) {
			rightScore.style.color = "#FFB3B3";
		}
		if (leftPlayerScore == rightPlayerScore) {
			leftScore.style.color = "#C5FFC0";
			rightScore.style.color = "#C5FFC0";
		}
	}
	// Entrypoint
	const joinQueue = () => {
		// Set up WebSocket connection
		console.log("uid = ", playerId, " token = ", token);
		ws = new WebSocket("ws://localhost:2000/ws/game/?uid=" + playerId);
		ws.onmessage = handleWebSocketMessage;
		// Keyboard events
		document.addEventListener("keydown", keyDownHandler);
		document.addEventListener("keyup", keyUpHandler);
	};
	draw();
	joinQueue();

	onlineGame.destroy = () => {
		document.removeEventListener("keydown", keyDownHandler);
		document.removeEventListener("keyup", keyUpHandler);
		if (ws) {
			ws.close();
			console.log("Closing connection with server");
		}
		cancelAnimationFrame(animationId);
		console.log('DESTROYED');
	};
}
onlineGame();