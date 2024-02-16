class AsyncLock {
    constructor() {
        this.locked = false;
        this.queue = [];
    }

    async acquire() {
        return new Promise((resolve, reject) => {
            if (!this.locked) {
                this.locked = true;
                resolve();
            } else {
                this.queue.push(resolve);
            }
        });
    }

    release() {
        if (this.queue.length > 0) {
            const resolve = this.queue.shift();
            resolve();
        } else {
            this.locked = false;
        }
    }
}

const playerId = getCookie("uid");
const token = getCookie("token");
const lock = new AsyncLock();
const bracket = document.getElementById("queue");
const gameContainer = document.getElementById("gameBox");
var ctx;
var canvas;
var leftScore;
var rightScore;
const paddleHScale = 0.2
const paddleWScale = 0.015
const remoteCanvasH = 510;

var animationId = 0;

var canvasW;
var canvasH;
var scaleFactor;

// Paddles
var paddleHeight;
var paddleWidth;
var leftPaddleYaxis;
var rightPaddleYaxis;

var leftPlayerScore = 0;
var rightPlayerScore = 0;
var maxScore = 10;

var wPressed = false;
var sPressed = false;

var leftWPressed = false;
var leftSPressed = false;
var rightWPressed = false;
var rightSPressed = false;

async function toggleBracket() {
	bracketContainer = document.getElementById("bracketContainer");
	if (bracketContainer.style.display === "none") {
		bracketContainer.style.display = "flex";
		while (gameContainer.firstChild) {
			gameContainer.firstChild.remove()
		}
	}
	else {
		bracketContainer.style.display = "none";
		await engine('/tourGame');
		console.log("fetched tour game template");
	}
}

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

async function getImage(targetUid) {
	try {
		const response = await fetch('playerInfo/?ownerUid=' + playerId + "&targetUid=" + targetUid + "&token=" + token);
		const jsonResponse = await response.json();
		return jsonResponse.image;
	} catch (error) {
		console.error("Error fetching image:", error);
	}
}

async function getUserName(targetUid) {
	try {
		const response = await fetch('playerInfo/?ownerUid=' + playerId + "&targetUid=" + targetUid + "&token=" + token);
		const jsonResponse = await response.json();
		return jsonResponse.first_name;
	} catch (error) {
		console.error("Error fetching image:", error);
	}
}


function isOpen(ws) { return ws.readyState === ws.OPEN }

async function addImage(playerId, imgId) {
	const imgUrl = await getImage(playerId);
	var playerImg = document.getElementById(imgId)
	playerImg.src = 'http://localhost:3000' + imgUrl;
	playerImg.setAttribute("data-uid", playerId);
}

async function addPlayerImages(playerList) {
	await lock.acquire()
	try {
		var i = 0;
		var playerImages = bracket.children;
		for (const playerId of playerList) {
			// await addImage(playerId);
			if (playerId == 0)
				break
			const imgUrl = await getImage(playerId);
			playerImages[i].firstElementChild.setAttribute("src", 'http://localhost:3000' + imgUrl);
			playerImages[i].firstElementChild.setAttribute("data-uid", playerId);
			i++;
		}
	} finally {
		lock.release()
	}
}

async function removePlayer(playerId) {
	await lock.acquire()
	try {
		// disconnectedPlayer = document.getElementById(playerId)
		var disconnectedPlayer = document.querySelector('[data-uid="' + playerId + '"]');
		disconnectedPlayer.src = "https://i.imgur.com/BPukfZQ.png";
		// document.querySelector("#queue").removeChild(disconnectedPlayer);
	} finally {
		lock.release()
	}
}

async function printNames(playerList) {
	for (uid of playerList) {
		var name = await getUserName(uid);
		console.log(name);
	}
}

function countdown(parent, callback) {
	var texts = ['Match found!'];
	// var texts = ['Match found!', '3', '2', '1', 'GO'];
	
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

async function setUpMatch(leftPlayerId, rightPlayerId) {
	await toggleBracket();
	countdown(document.getElementById("readyGo"), animateGame);
	var leftImage = document.getElementById("leftImage");
	var rightImage = document.getElementById("rightImage");
	document.addEventListener("keydown", keyDownHandler);
	document.addEventListener("keyup", keyUpHandler);
	getImage(leftPlayerId)
		.then(imgUrl => {
			console.log("Image URL:", imgUrl);
			leftImage.src = "http://localhost:3000" + imgUrl;
		});
	getImage(rightPlayerId)
		.then(imgUrl => {
			console.log("Image URL:", imgUrl);
			rightImage.src = "http://localhost:3000" + imgUrl;
		});
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
	leftWPressed = false;
	leftSPressed = false;
	rightWPressed = false;
	rightSPressed = false;
	draw();
}

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
			reset(ballSpeed * messageData.ballDir);
			if (leftPlayerScore == 11 || rightPlayerScore == 11) {
				endMatch();
			}
			break;
		case "roundStarting":
			console.log("Round starting... Left = ", messageData.leftPlayer, " Right = ", messageData.rightPlayer);
			leftPlayerId = messageData.leftPlayer;
			rightPlayerId = messageData.rightPlayer;
			setUpMatch(messageData.leftPlayer, messageData.rightPlayer);
			break;
		case "tournamentStarted":
			console.log("Tournament starting... Player list = ");
			break;
		case "tournamentFound":
			console.log("tournament found! player list = ", messageData.playerList);
			addPlayerImages(messageData.playerList);
			break;
		case "newPlayerJoined":
			var newPlayerId = messageData.newPlayerId;
			console.log("new player joined: ", newPlayerId);
			addImage(newPlayerId, messageData.imgId);
			break;
		case "inGame":
			console.log("You're queued or have another ongoing tournament on another tab or computer", playerId);
			ws.close(3001, "Player already in-game");
			// show error pop up and redirect them back to home page 
			break;
		case "playerLeftQueue":
			console.log("Player ", messageData.playerId, " has left the queue");
			removePlayer(messageData.playerId);
			break;
		case "disconnected":
			console.log("Opponent has disconnected");

		default:
			// Handle default case if needed
			break;
	}
}

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

function endMatch()
{
	if (animationId != 0) {
		cancelAnimationFrame(animationId);
		animationId = 0;
	}
	toggleBracket()
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

// Reset ball
const reset = (newBallSpeed) => {
	ballXaxis = canvasW / 2;
	ballYaxis = canvasH / 2;
	ballSpeedXaxis = newBallSpeed;
	ballSpeedYaxis = newBallSpeed;
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
	animationId = requestAnimationFrame(animateGame);
};

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

const joinQueue = () => {
	// Set up WebSocket connection
	console.log("uid = ", playerId, " token = ", token);
	ws = new WebSocket("ws://localhost:4000/ws/tour/?uid=" + playerId);
	ws.onmessage = handleWebSocketMessage;
};

joinQueue();

