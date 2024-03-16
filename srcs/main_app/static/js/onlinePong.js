onlineGame = () => {

	// Initialize all game variables
	const canvas = document.getElementById("gameCanvas");
	const leftScore = document.getElementById("leftScore");
	const rightScore = document.getElementById("rightScore");
	const ctx = canvas.getContext("2d");
	const playerId = getCookie("uid");
	
	const paddleHScale = 0.2
	const paddleWScale = 0.015
	
	var animationId;

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
	const WIN_SCORE = 6;

	// Keys
	var leftWPressed = false;
	var leftSPressed = false;
	var rightWPressed = false;
	var rightSPressed = false;
	var wPressed = false;
	var sPressed = false;
	var gameRunning = false;
	var leftPlayerId;
	var rightPlayerId;
	
	// This function retrieves the value of a cookie by its name from the browser's cookies
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
	
	// This function fetches a player image given their UID
	async function getImage(ownerUid, targetUid) {
		try {
			const response = await fetch('playerInfo/?ownerUid=' + ownerUid + "&targetUid=" + targetUid);
			const jsonResponse = await response.json();
			return jsonResponse.image;
		} catch (error) {
			console.error("Error fetching image:", error);
		}
	}
	
	// Countdown animation that plays before a match starts
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
			
			// This new paragraph will trigger an animation
			paragraph = document.createElement("div");
			paragraph.textContent = text;
			paragraph.className = text + " nums";
			parent.appendChild(paragraph);
		}
		// Initiate an interval, but store it in a variable so we can remove it later.
		var interval = setInterval( count, 1000 );  
	}

	// Checks if a socket is open and ready to send/receive info
	function isOpen(ws) { return ws.readyState === ws.OPEN }

	// Handler for all websocket messages that come from the server
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
			console.log("score reset received, ", messageData.ballDir);
			leftPlayerScore = messageData.leftScore;
			rightPlayerScore = messageData.rightScore;
			reset(ballSpeed * messageData.ballDir);
			gameRunning = true;
		}
		else if (messageData.type === "matchEnded") {
			leftPlayerScore = messageData.leftScore;
			rightPlayerScore = messageData.rightScore;
			reset(ballSpeed);
			// gameRunning = true;
			// scoreChanged = true;
			draw();
			requestAnimationFrame(endMatch);
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
			gameRunning = true;
			countdown(document.getElementById("readyGo"), animateGame);
			var leftImage = document.getElementById("leftImage");
			var rightImage = document.getElementById("rightImage");
			getImage(playerId, leftPlayerId)
				.then(imgUrl => {
					console.log("left image found: ", imgUrl);
					leftImage.src = imgUrl;
				});
			getImage(playerId, rightPlayerId)
				.then(imgUrl => {
					console.log("right image found: ", imgUrl);
					rightImage.src = imgUrl;
				});
		}
		else if (messageData.type === "disconnected") {
			reset();
			alert("Opponent disconnected from the game");
			cancelAnimationFrame(animationId);
			// show error pop up and redirect them back to home page 
		}
	};

	// Ends the match and updates UI accordingly
	function endMatch()
	{
		// Checks if the left player or right player wins the match
		if (leftPlayerScore == WIN_SCORE && leftPlayerId == playerId 
			|| rightPlayerScore == WIN_SCORE && rightPlayerId == playerId) {
			// Display victory message and prepare for next round
			setTimeout(function() {
				alert("You win!");
				cancelAnimationFrame(animationId);
			  }, 0)
		}
		else {
			// Display defeat message and prepare for result display
			setTimeout(function() {
				alert("You lose.");
				cancelAnimationFrame(animationId);
			  }, 0)
		}
		// Marks the game as not running
		gameRunning = false;
	}

	// Sends a key update to the server
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
	
	// Sends a player scored event to the server
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

	// Key down handler
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

	// Key up handler
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

	// This function is called in the animation loop for every frame update
	// The paddle positions and ball positions are updated here
	function update()
	{
		if (gameRunning == false) {
			console.log("stuck here");
			return ;
		}
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
			if (playerId == rightPlayerId) {
				console.log("i scored on left");
				ballXaxis = canvasW / 2;
				ballYaxis = canvasH / 2;
				gameRunning = false;
				sendScoredEvent();
			}
			else {
				console.log("opponent scored on left")
				ballSpeedXaxis = -ballSpeedXaxis;
			}
		}
		else if (ballXaxis + ballRadius >= canvasW) {
			if (playerId == leftPlayerId) {
				console.log("i scored on right");
				ballXaxis = canvasW / 2;
				ballYaxis = canvasH / 2;
				gameRunning = false;
				sendScoredEvent();
			}
			else {
				console.log("opponent scored on right")
				ballSpeedXaxis = -ballSpeedXaxis;
			}
		}
	}

	// Animation loop that keeps the game animation running
	const animateGame = (time) => {
		update();
		draw();
		// Start the animation loop
		animationId = requestAnimationFrame(animateGame);
	};

	// Reset ball position to the center of the canvas and set the new ball direction 
	const reset = (newBallSpeed) => {
		ballXaxis = canvasW / 2;
		ballYaxis = canvasH / 2;
		ballSpeedXaxis = newBallSpeed;
		ballSpeedYaxis = newBallSpeed;
	}

	// Draws all updated paddle positions, ball position the canvas. Also updates the score elements
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
		console.log("uid = ", playerId);
		// prod version
		// ws = new WebSocket("wss://localhost:2000/ws/game/?uid=" + playerId);
		
		// dev version
		ws = new WebSocket("ws://localhost:2000/ws/game/?uid=" + playerId);
		
		console.log("Socket established, ws = ", ws);
		ws.onmessage = handleWebSocketMessage;
		
		// Set key handlers for the game 
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