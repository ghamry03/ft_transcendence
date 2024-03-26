tournament = () => {

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


	const WIN_SCORE = 11;

	const playerId = getCookie("uid");
	const lock = new AsyncLock();
	const gameContainer = document.getElementById("gameBox");
	const checkBox = document.querySelector('.form-check-input');
	const checkForm = document.getElementById("readyButton");
	const tournamentStatus = document.getElementById("tournamentStatus");

	var ctx;
	var canvas;
	var leftScore;
	var rightScore;
	var upButton;
    var downButton;
	const paddleHScale = 0.2
	const paddleWScale = 0.015

	var animationId = 0;

	var canvasW;
	var canvasH;

	// Paddles
	var paddleHeight;
	var paddleWidth;
	var leftPaddleYaxis;
	var rightPaddleYaxis;

	var leftPlayerScore = 0;
	var rightPlayerScore = 0;

	var upPressed = false;
	var downPressed = false;

	var leftWPressed = false;
	var leftSPressed = false;
	var rightWPressed = false;
	var rightSPressed = false;

	var gameRunning = false;
	var roundNo = 0;
	var paddleSpeed;
	var ballXaxis;
	var ballYaxis;
	var ballRadius;
	var ballSpeed;
	var ballSpeedXaxis;
	var ballSpeedYaxis;
	var lost = false;

	// This function removes the bracket from view and inserts the game canvas, or vice versa
	async function toggleBracket() {
		await lock.acquire()
		try {
			statusBox = document.getElementById("statusBox");
			bracketContainer = document.getElementById("bracketContainer");
			if (bracketContainer.style.display === "none") {
				if (animationId != 0) {
					cancelAnimationFrame(animationId);
					animationId = 0;
				}
				while (gameContainer.firstChild) {
					gameContainer.firstChild.remove()
				}
				bracketContainer.style.display = "";
				statusBox.style.display = "";
			}
			else {
				bracketContainer.style.display = "none";
				statusBox.style.display = "none";
				await engine('/tourGame');
			}
		} finally {
			lock.release()
		}
	}

	// This function retrieves the value of a cookie by its name from the browser's cookies
	function getCookie(cname) {
		let name = cname + "=";
		let decodedCookie = decodeURIComponent(document.cookie);
		let ca = decodedCookie.split(';');
		for (let i = 0; i < ca.length; i++) {
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
	async function getImage(targetUid) {
		try {
			const response = await fetch('playerInfo/?ownerUid=' + playerId + "&targetUid=" + targetUid);
			const jsonResponse = await response.json();
			return jsonResponse.image;
		} catch (error) {
			console.error("Error fetching image:", error);
		}
	}

	// This function fetches the username of a player given their UID
	async function getUserName(targetUid) {
		try {
			const response = await fetch('playerInfo/?ownerUid=' + playerId + "&targetUid=" + targetUid);
			const jsonResponse = await response.json();
			return jsonResponse.username;
		} catch (error) {
			console.error("Error fetching image:", error);
		}
	}

	// Checks if a socket is open and ready to send/receive info
	function isOpen(ws) { return ws.readyState === ws.OPEN }

	// Adds the image of user to a given image placeholder
	async function addImage(playerId, imgId) {
		const imgUrl = await getImage(playerId);
		const username = await getUserName(playerId);
		var playerImg = document.getElementById("player" + imgId);
		var nameElement = document.getElementById("name" + imgId);
		if (playerImg) {
			playerImg.src = imgUrl;
			playerImg.setAttribute("data-imguid", playerId);
		}
		if (nameElement) {
			nameElement.innerText = username;
			nameElement.setAttribute("data-nameuid", playerId);
		}
	}

	// Adds player images to the bracket one by one, 
	// Called when a player first joins, to load existing players
	async function addPlayerImages(playerList) {
		await lock.acquire()
		try {
			var i = 0;
			for (const playerId of playerList) {
				if (playerId == 0)
					break;
				var imgElement = document.getElementById("player" + i);
				if (imgElement) {
					const imgUrl = await getImage(playerId);
					imgElement.setAttribute("src", imgUrl);
					imgElement.setAttribute("data-imguid", playerId);
				}
				var nameElement = document.getElementById("name" + i);
				if (nameElement) {
					const userName = await getUserName(playerId);
					nameElement.innerText = userName;
					nameElement.setAttribute("data-nameuid", playerId);
				}
				i++;
			}
		} finally {
			lock.release()
		}
	}

	// Removes a player image from the bracket
	// Called when someone leaves the queue 
	async function removePlayer(playerId) {
		await lock.acquire()
		try {
			var disconnectedPlayerImg = document.querySelector('[data-imguid="' + playerId + '"]');
			var disconnectedPlayerName = document.querySelector('[data-nameuid="' + playerId + '"]');
			mediaUrl = location.protocol === "https:" ? "https://localhost:8005/" : "http://localhost:8001/";
			disconnectedPlayerImg.src = mediaUrl + "media/unknownuser.png";
			disconnectedPlayerName.innerText = "Player"
		} catch(error) {
			console.log("Unknown user image not found");
		} finally {
			lock.release()
		}
	}

	// Show final results of the tournament including winner image and username
	async function showWinner(uid) {
		userName = await getUserName(uid);
		const imgUrl = await getImage(uid);
		checkBox.checked = false;
		checkForm.style.display = "none";
		updateTourStatus("Winner of the tournament - " + userName);
		var divElement = document.createElement("div");
		divElement.className = "img-cir round mx-auto";

		var imgElement = document.createElement("img");
		imgElement.src = imgUrl;
		imgElement.alt = "Winner";
		imgElement.id = "winnerImg";

		divElement.appendChild(imgElement);
		statusBox = document.getElementById("statusBox");
		if (statusBox)
			statusBox.appendChild(divElement);
	}

	// Countdown animation that plays before a match starts
	function countdown(parent, callback) {
		var texts = ['Match starting!'];
		
		var paragraph = null;
		
		function count() {
			if (paragraph) {
				paragraph.remove();
			}
			if (texts.length === 0) {
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
		var interval = setInterval( count, 1000 );  
	}

	async function startMatch(leftPlayerId, rightPlayerId) {
		// Hide the bracket
		await toggleBracket();

		// Set key press listeners for paddle movement
		document.addEventListener("keydown", keyDownHandler);
		document.addEventListener("keyup", keyUpHandler);
		
		// Set button press handlers for mobile game
		upButton = document.getElementById("upButton");
		downButton = document.getElementById("downButton");
		upButton.addEventListener("touchstart", upButtonDownHandler);
        upButton.addEventListener("touchend", upButtonUpHandler);
		downButton.addEventListener("touchstart", downButtonDownHandler);
        downButton.addEventListener("touchend", downButtonUpHandler);

		// Display both players images 
		var leftImage = document.getElementById("leftImage");
		var rightImage = document.getElementById("rightImage");
		getImage(leftPlayerId)
			.then(imgUrl => {
				leftImage.src = imgUrl;
			});
		getImage(rightPlayerId)
			.then(imgUrl => {
				rightImage.src = imgUrl;
			});
			
		// ----- Setting all game params to starting values -----

		// Canvas 
		canvas = document.getElementById("gameCanvas");
		leftScore = document.getElementById("leftScore");
		rightScore = document.getElementById("rightScore");
		ctx = canvas.getContext("2d");
		canvasW = canvas.getBoundingClientRect().width;
		canvasH = canvas.getBoundingClientRect().height;
		canvas.width = canvasW;
		canvas.height = canvasH;

		// Paddle
		paddleHeight = Math.floor(canvasH * paddleHScale);
		paddleWidth = Math.floor(canvasW * paddleWScale);
		leftPaddleYaxis = Math.floor(canvasH / 2 - paddleHeight / 2);
		rightPaddleYaxis = Math.floor(canvasH / 2 - paddleHeight / 2);
		paddleSpeed = canvasH * 0.01;

		// Ball
		ballXaxis = Math.floor(canvasW / 2);
		ballYaxis = Math.floor(canvasH / 2);
		ballRadius = paddleWidth;
		ballSpeed = canvasW * 0.006;
		ballSpeedXaxis = ballSpeed;
		ballSpeedYaxis = ballSpeed;

		// Keys
		leftWPressed = false;
		leftSPressed = false;
		rightWPressed = false;
		rightSPressed = false;

		// Scores
		leftPlayerScore = 0;
		rightPlayerScore = 0;

		// Draw the initial screen for the game with start positions of paddles and ball
		draw();

		// Start the match countdown and animation

		// gameRunning = false;
		// animateGame();
		// countdown(document.getElementById("readyGo"));
		sendGameReadyEvent();

		// gameRunning = true;
		// countdown(document.getElementById("readyGo"), animateGame);
	}

	// Handler for checkbox if a user is ready to start their assigned match
	if (checkBox) {
		checkBox.addEventListener('change', function() {
			if (checkBox.checked) {
				checkForm.style.display = "none";
				updateTourStatus("Waiting for opponent...");
				sendReadyEvent();
			}
		});
	}

	// Update the tour status when the next round is ready and let the user confirm 
	function startNextRound() {
		roundNo++;
		updateTourStatus("Round " + roundNo + " starting, get ready!");
		checkBox.checked = false;
		checkForm.style.display = "block";
	}

	// Handler for all websocket messages that come from the server
	const handleWebSocketMessage = (event) => {
		const messageData = JSON.parse(event.data);
		
		switch (messageData.type) {
			case "keyUpdate":
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
				break;
			case "scoreUpdate":
				leftPlayerScore = messageData.leftScore;
				rightPlayerScore = messageData.rightScore;
				reset(ballSpeed * messageData.ballDir).then(() => {
					gameRunning = true;
				});
				break;
			case "matchEnded":
				leftPlayerScore = messageData.leftScore;
				rightPlayerScore = messageData.rightScore;
				reset(ballSpeed).then(() => {
					// gameRunning = true;
					draw();
					requestAnimationFrame(endMatch);
				});
				break;
			case "roundStarting":
				console.log("Round starting... Left = ", messageData.leftPlayer, " Right = ", messageData.rightPlayer);
				leftPlayerId = messageData.leftPlayer;
				rightPlayerId = messageData.rightPlayer;
				startMatch(messageData.leftPlayer, messageData.rightPlayer);
				break;
			case "gameReady":
				gameRunning = false;
				animateGame();
				countdown(document.getElementById("readyGo"));
				break;
			case "tournamentStarted":
				console.log("Tournament starting...");
				if (!lost)
					startNextRound();
				break;
			case "tournamentFound":
				console.log("Tournament found! player list = ", messageData.playerList);
				addPlayerImages(messageData.playerList);
				break;
			case "tournamentEnded":
				console.log("Tournament ended! Winner: ", messageData.winnerId);
				showWinner(messageData.winnerId);
				break;
			case "newPlayerJoined":
				var newPlayerId = messageData.newPlayerId;
				console.log("new player joined: ", newPlayerId);
				addImage(newPlayerId, messageData.imgId);
				break;
			case "inGame":
				ws.close(3001, "Player already in-game");
				alert("You have a tournament running on another session!");
				engine('/cards');
				break;
			case "playerLeftQueue":
				console.log("Player ", messageData.playerId, " has left the queue");
				removePlayer(messageData.playerId);
				break;
			case "disconnected":
				console.log("Opponent has disconnected");
				// add an modal saying the opponent disconnected and they win by default
				if (gameRunning) {
					if (leftPlayerId == playerId) {
						leftPlayerScore = WIN_SCORE;
					}
					else {
						rightPlayerScore = WIN_SCORE;
					}
					reset(ballSpeed).then(() => {
						draw();
						requestAnimationFrame(endMatch);
					});
				}
				else {
					updateTourStatus("Round " + roundNo + " complete! Waiting for players...");
					checkForm.style.display = "none";
				}
				break;
			case "tournamentCanceled":
				alert("Tournament was canceled, not enough players to continue");
				ws.close();
				break;
			default:
				break;
		}
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
		else {
			alert("Lost connection with server");
			cancelAnimationFrame(animationId);
		}
	}

	// Sends a player scored event to the server
	function sendScoredEvent()
	{
		if (isOpen(ws)) {
			ws.send(
				JSON.stringify({
					type: "playerScored",
					playerId: playerId
				})
			);
		}
		else {
			alert("Lost connection with server");
			cancelAnimationFrame(animationId);
		}
	}
	
	// Sends a player ready event to the server
	function sendReadyEvent()
	{
		if (isOpen(ws)) {
			ws.send(
				JSON.stringify({
					type: "playerReady",
					playerId: playerId
				})
			);
		}
		else {
			alert("Lost connection with server");
		}
	}

	// Sends a player ready event to the server
	function sendGameReadyEvent()
	{
		if (isOpen(ws)) {
			ws.send(
				JSON.stringify({
					type: "gameReady",
					playerId: playerId
				})
			);
		}
		else {
			alert("Lost connection with server");
		}
	}

	function updateTourStatus(msg) {
		if (tournamentStatus) {
			tournamentStatus.innerText = msg;
		}
	}

	// Ends the match and updates UI accordingly
	function endMatch() {
		// Checks if the left player or right player wins the match
		if ((leftPlayerScore == WIN_SCORE && leftPlayerId == playerId) || 
			(rightPlayerScore == WIN_SCORE && rightPlayerId == playerId)) {
			// Display victory message and prepare for next round
			setTimeout(function() {
				updateTourStatus("Round " + roundNo + " complete! Waiting for players...");
				alert("You win! Proceed to next round...");
				toggleBracket();
			}, 0);
		} else {
			// Display defeat message and prepare for result display
			setTimeout(function() {
				updateTourStatus("You lost at round " + roundNo);
				alert("You lose. Proceed to results...");
				toggleBracket();
			}, 0);
			lost = true;
		}
		// Marks the game as not running
		gameRunning = false;
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
				// console.log("stuck here");
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
			const response = await fetch("tourUrl/");
			if (!response.ok) {
				alert("Cannot connect to the server. Returning home...");
				engine('/cards');
			}
			else {
				const tourUrl = await response.text();
				ws = new WebSocket(tourUrl +  "ws/tour/?uid=" + playerId);
				console.log("Socket established, ws = ", ws);
				ws.onmessage = handleWebSocketMessage;
			}
		} catch(error) {
			console.log("Error establishing socket");
		}

	}

	const joinQueue = () => {
		console.log("uid = ", playerId);
		establishSocket();
	};
	joinQueue();

	tournament.destroy = () => {
		document.removeEventListener("keydown", keyDownHandler);
		document.removeEventListener("keyup", keyUpHandler);
		if (upButton) {
			upButton.removeEventListener("touchstart", upButtonDownHandler);
			upButton.removeEventListener("touchend", upButtonUpHandler);
		}
		if (downButton) {
			downButton.removeEventListener("touchstart", downButtonDownHandler);
			downButton.removeEventListener("touchend", downButtonUpHandler);
		}
		if (ws) {
			ws.close();
			console.log("Tour: Closing connection with server");
		}
		cancelAnimationFrame(animationId);
		console.log('DESTROYED');
	};
}
tournament();
