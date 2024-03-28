onlineGame = () => {
	// Class for managing asynchronous locks
	class AsyncLock {
		constructor() {
			// Indicates whether the lock is currently acquired
			this.locked = false;
			// Queue to hold pending requests for the lock
			this.queue = [];
		}

		// Method to acquire the lock asynchronously
		async acquire() {
			return new Promise((resolve, reject) => {
				if (!this.locked) {
					this.locked = true;
					resolve();
				} else {
					// If locked, add resolver function to the queue
					this.queue.push(resolve);
				}
			});
		}

		// Method to release the lock
		release() {
			if (this.queue.length > 0) {
				// If queue is not empty, release to the next waiting task
				const resolve = this.queue.shift();
				resolve();
			} else {
				// If no pending tasks, release the lock
				this.locked = false;
			}
		}
	}

	// Initialize all game variables
	const canvas = document.getElementById("gameCanvas");
	const leftScore = document.getElementById("leftScore");
	const rightScore = document.getElementById("rightScore");
	var upButton = document.getElementById("upButton");
    var downButton = document.getElementById("downButton");

	
	const ctx = canvas.getContext("2d");
	const playerId = getCookie("uid");
	const lock = new AsyncLock();
	
	const paddleHScale = 0.2
	const paddleWScale = 0.015
	
	var animationId;

	const canvasW = canvas.getBoundingClientRect().width;
	const canvasH = canvas.getBoundingClientRect().height;
	canvas.width = canvasW;
	canvas.height = canvasH;
	console.log("canvas w and h = ", canvas.width, canvas.height)
	
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
	const WIN_SCORE = 11;

	// Keys
	var leftWPressed = false;
	var leftSPressed = false;
	var rightWPressed = false;
	var rightSPressed = false;
	var upPressed = false;
	var downPressed = false;
	var gameRunning = false;
	var leftPlayerId;
	var rightPlayerId;
	
	// Checks if a socket is open and ready to send/receive info
	function isOpen(ws) { return ws.readyState === ws.OPEN }

	function disconnectInactivePlayer() {
		if (document.visibilityState == "visible") {
			console.log("tab is active")
		  } else {
			console.log("tab is inactive")
			  if (isOpen(ws)) {
				  ws.close();
				  engine('/cards');
			  }
		  }
	}

	document.addEventListener("visibilitychange", disconnectInactivePlayer);

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
	function countdown(parent) {
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
				gameRunning = true;
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

	// Reset ball position to the center of the canvas and set the new ball direction 
	async function reset (newBallSpeed) {
		await lock.acquire()
		try {
			ballXaxis = canvasW / 2;
			ballYaxis = canvasH / 2;
			ballSpeedXaxis = newBallSpeed;
			ballSpeedYaxis = newBallSpeed;
		} finally {
			lock.release()
		}
	}
	
	// Handler for all websocket messages that come from the server
	const handleWebSocketMessage = (event) => {
		const messageData = JSON.parse(event.data);
		if (messageData.type === "keyUpdate") {
			if (messageData.isLeft) {
				if (messageData.key == "w") {
					leftWPressed = messageData.keyDown;
				}
				else {
					leftSPressed = messageData.keyDown;
				}
			}
			else {
				if (messageData.key == "w") {
					rightWPressed = messageData.keyDown;
				}
				else {
					rightSPressed = messageData.keyDown;
				}
			}
		}
		if (messageData.type === "scoreUpdate") {
			leftPlayerScore = messageData.leftScore;
			rightPlayerScore = messageData.rightScore;
			reset(ballSpeed * messageData.ballDir).then(() => {
				gameRunning = true;
			});
		}
		else if (messageData.type === "matchEnded") {
			leftPlayerScore = messageData.leftScore;
			rightPlayerScore = messageData.rightScore;
			reset(ballSpeed).then(() => {
				draw();
				requestAnimationFrame(endMatch);
			});
		}
		else if (messageData.type === "inGame") {
			ws.close(3001, "Player already in-game");
			alert("You have a game running on another session!");
			engine('/cards');
		}
		else if (messageData.type === "matchFound") {
			leftPlayerId = messageData.left;
			rightPlayerId = messageData.right;
			console.log("Match found, left = ", leftPlayerId, " right = ", rightPlayerId);
			gameRunning = false;
			animateGame();
			countdown(document.getElementById("readyGo"));
			var leftImage = document.getElementById("leftImage");
			var rightImage = document.getElementById("rightImage");
			getImage(playerId, leftPlayerId)
				.then(imgUrl => {
					leftImage.src = imgUrl;
				});
			getImage(playerId, rightPlayerId)
				.then(imgUrl => {
					rightImage.src = imgUrl;
				});
		}
		else if (messageData.type === "disconnected") {
			reset(ballSpeed).then(() => {
				alert("Opponent disconnected from the game");
				cancelAnimationFrame(animationId);
				engine('/cards');
			});
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
				alert("You win! Returning to home screen...");
				cancelAnimationFrame(animationId);
				engine('/cards');
			  }, 0)
		}
		else {
			// Display defeat message and prepare for result display
			setTimeout(function() {
				alert("You lose. Returning to home screen...");
				cancelAnimationFrame(animationId);
				engine('/cards');
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

	// Up Button down handler
	function upButtonDownHandler(e)
	{
		if (!upPressed)
		{
			upPressed = true;
			sendKeyUpdate("w", true);
		}
	}
	
	// Up Button up handler
	function upButtonUpHandler(e)
	{
		if (upPressed)
		{
			upPressed = false;
			sendKeyUpdate("w", false);
		}
	}
	
	// down Button down handler
	function downButtonDownHandler(e)
	{
		if (!downPressed)
		{
			downPressed = true;
			sendKeyUpdate("s", true);
		}
	}
	
	// down Button up handler
	function downButtonUpHandler(e)
	{
		if (downPressed)
		{
			downPressed = false;
			sendKeyUpdate("s", false);
		}
	}

	// Key down handler
	function keyDownHandler(e)
	{
		if (e.key === "w" && !upPressed)
		{
			upPressed = true;
			sendKeyUpdate(e.key, true);
		}
		else if (e.key === "s" && !downPressed)
		{
			downPressed = true;
			sendKeyUpdate(e.key, true);
		}
	}

	// Key up handler
	function keyUpHandler(e)
	{
		if (e.key === "w" && upPressed)
		{
			upPressed = false;
			sendKeyUpdate(e.key, false);
		}
		else if (e.key === "s" && downPressed)
		{
			downPressed = false;
			sendKeyUpdate(e.key, false);
		}
	}

	// sidePlayerId - pass in either the rightPlayerId or leftPlayerId
	function checkScoreSide(sidePlayerId, ballHitRight) {
		if (playerId == sidePlayerId) {
			ballXaxis = canvasW / 2;
			ballYaxis = canvasH / 2;
			gameRunning = false;
			sendScoredEvent();
		}
		else {
			if (ballHitRight == true) {
				ballSpeedXaxis = -ballSpeed;
			}
			else {
				ballSpeedXaxis = ballSpeed;
			}
		}
	}

	// This function is called in the animation loop for every frame update
	// The paddle positions and ball positions are updated here
	async function update()
	{
		await lock.acquire()
		try {
			if (gameRunning == false) {
				return ;
			}
			// Left paddle movement
			if (leftWPressed && leftPaddleYaxis > 0) {
				leftPaddleYaxis -= paddleSpeed;
			}
			else if (leftSPressed && leftPaddleYaxis + paddleHeight < canvasH) {
				leftPaddleYaxis += paddleSpeed;
			}
			
			// Right paddle movement
			if (rightWPressed && rightPaddleYaxis > 0) {
				rightPaddleYaxis -= paddleSpeed;
			}
			else if (rightSPressed && rightPaddleYaxis + paddleHeight < canvasH) {
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
				if (ballSpeedXaxis < 0) {
					ballSpeedXaxis = -ballSpeedXaxis;
				}
			}
	
			// Right paddle collision
			if (ballXaxis + ballRadius >= canvasW - paddleWidth &&
				ballYaxis >= rightPaddleYaxis &&
				ballYaxis <= rightPaddleYaxis + paddleHeight) {
				if (ballSpeedXaxis > 0) {
					ballSpeedXaxis = -ballSpeedXaxis;
				}
			}
	
			// Check if ball goes out of bounds on left or right side of canvas
			if (ballXaxis - ballRadius <= 0) {
				// Check if this player is the right player and forward score info to server accordingly
				checkScoreSide(rightPlayerId, false);
			}
			else if (ballXaxis + ballRadius >= canvasW) {
				// Check if this player is the left player and forward score info to server accordingly
				checkScoreSide(leftPlayerId, true);
			}
		} finally {
			lock.release()
		}
	}

	// Animation loop that keeps the game animation running
	const animateGame = (time) => {
		update().then(() => {
			// Draw the updated frame on the canvas
			draw();
			// Start the animation loop
			animationId = requestAnimationFrame(animateGame);
		});
	};


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

	async function establishSocket() {
		try {
			const response = await fetch("gameUrl/");
			if (!response.ok) {
				alert("Cannot connect to the server. Returning home...");
				engine('/cards');
			}
			else {
				const gameUrl = await response.text();
				ws = new WebSocket(gameUrl +  "ws/game/?uid=" + playerId);
				console.log("Socket established, ws = ", ws);
				ws.onmessage = handleWebSocketMessage;
			}
		} catch(error) {
			console.log("Error establishing socket");
		}

	}

	// Entrypoint
	const joinQueue = () => {
		// Set up WebSocket connection
		console.log("uid = ", playerId);
		
		establishSocket();

		// Set key handlers for the game 
		document.addEventListener("keydown", keyDownHandler);
		document.addEventListener("keyup", keyUpHandler);
		
		// Set button press handlers for mobile game
		upButton.addEventListener("touchstart", upButtonDownHandler);
        upButton.addEventListener("touchend", upButtonUpHandler);
		downButton.addEventListener("touchstart", downButtonDownHandler);
        downButton.addEventListener("touchend", downButtonUpHandler);
	};

	draw();
	joinQueue();

	onlineGame.destroy = () => {
		document.removeEventListener("keydown", keyDownHandler);
		document.removeEventListener("keyup", keyUpHandler);
		upButton.removeEventListener("touchstart", upButtonDownHandler);
        upButton.removeEventListener("touchend", upButtonUpHandler);
		downButton.removeEventListener("touchstart", downButtonDownHandler);
        downButton.removeEventListener("touchend", downButtonUpHandler);
		document.removeEventListener("visibilitychange", disconnectInactivePlayer);
		if (ws) {
			ws.close();
			console.log("Closing connection with server");
		}
		cancelAnimationFrame(animationId);
		console.log('DESTROYED');
	};
}
onlineGame();