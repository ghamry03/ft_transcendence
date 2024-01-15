var canvas;
var ctx;
var pauseBtn;
var restartBtn;

var animationId;
// var gameRunning = false;

// Ball
var ballRadius = 10;
var ballXaxis;
var ballYaxis;

// Paddles
var paddleHeight = 80;
var paddleWidth = 10;
var leftPaddleYaxis;
var rightPaddleYaxis;

// Score
var leftPlayerScore = 0;
var rightPlayerScore = 0;
var maxScore = 10;

var wPressed = false;
var sPressed = false;

// socket info 
var ws;
var playerId;

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

function isOpen(ws) { return ws.readyState === ws.OPEN }

const handleWebSocketMessage = (event) => {
	const messageData = JSON.parse(event.data);
	if (messageData.type === "stateUpdate") {
		console.log("status update");
		ballXaxis = messageData.ballX;
		ballYaxis = messageData.ballY;
		leftPaddleYaxis = messageData.leftPaddle;
		rightPaddleYaxis = messageData.rightPaddle;
	} 
	else if (messageData.type === "playerId") {
		playerId = messageData.playerId;
		console.log("your player id is ", playerId);
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
	draw();
	animationId = requestAnimationFrame(animateGame);
};

// Reset ball
const reset = () => {
	ballXaxis = canvas.width / 2;
	ballYaxis = canvas.height / 2;
	// ballSpeedXaxis = -ballSpeedXaxis;
	// ballSpeedYaxis = -ballSpeedYaxis;
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

	// Set up WebSocket connection
	ws = new WebSocket("ws://localhost:2000/ws/game/");
	ws.onmessage = handleWebSocketMessage;

	// Keyboard events
	document.addEventListener("keydown", keyDownHandler);
	document.addEventListener("keyup", keyUpHandler);
};

function setUpGame() {
	
	console.log("hello1");
	// document.addEventListener('DOMContentLoaded', function() {
		canvas = document.getElementById("gameCanvas");
		ctx = canvas.getContext("2d");
	
		console.log("hello");
		// startBtn = document.getElementById("start-btn");
		pauseBtn = document.getElementById("pause-btn");
		restartBtn = document.getElementById("restart-btn");
		ballXaxis = canvas.width / 2;
		ballYaxis = canvas.height / 2;
		leftPaddleYaxis = canvas.height / 2 - paddleHeight / 2;
		rightPaddleYaxis = canvas.height / 2 - paddleHeight / 2;
	
		pauseBtn.addEventListener("click", function()
		{
			ws.close();
			console.log("stopped game");
			// gameRunning = false;
			cancelAnimationFrame(animationId);
		});
		
		restartBtn.addEventListener("click", function()
		{
			ws.close();
			cancelAnimationFrame(animationId);
			document.location.reload();
		});
		draw();
		joinQueue();
	// });
}
