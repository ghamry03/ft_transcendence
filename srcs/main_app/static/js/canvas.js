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
  var leftPlayerId;
  var rightPlayerId;
  var leftPlayerImg;
  var rightPlayerImg;

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

  // function getImage(uid, token) {
  // 	var imgUrl;
  // 	fetch('http://127.0.0.1:8000/playerInfo/?uid=' + uid + "&token=" + token)
  // 		.then(response => {
  // 			return response.json();
  // 		})
  // 		.then(jsonResponse => {
  // 			imgUrl = jsonResponse.image;
  // 		});
  // 	return imgUrl;
  // }

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

  function getPlayerImages(uid) {
	fetch('http://localhost:3000/users/api/' + uid, {
	  headers: {
		'X-UID': uid,
		'X-TOKEN': token
	  }
	  })
	  .then(response => response.json())
	  .then(data => console.log(JSON.stringify(data)))
  }

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
	  console.log("you're queued or have another ongoing match on another tab or computer", playerId);
	  ws.close(3001, "Player already in-game");
	  // show error pop up and redirect them back to home page 
	}
	else if (messageData.type === "matchFound") {
	  leftPlayerId = messageData.left;
	  rightPlayerId = messageData.right;
	  console.log("match found, left = ", leftPlayerId, " right = ", rightPlayerId);

	  countdown(document.getElementById("readyGo"), animateGame);
	  var leftImage = document.getElementById("leftImage");
	  var rightImage = document.getElementById("rightImage");
	  getImage(playerId, leftPlayerId, token)
		.then(imgUrl => {
		  console.log("Image URL:", imgUrl);
		  leftImage.src = "http://localhost:3000" + imgUrl;
	  });
	  getImage(playerId, rightPlayerId, token)
		.then(imgUrl => {
		  console.log("Image URL:", imgUrl);
		  rightImage.src = "http://localhost:3000" + imgUrl;
	  });
	  if (isOpen(ws)) {
		ws.send(
		  JSON.stringify({
			type: "ready",
			playerId: playerId,
		  })
		);
	  }
	}
	// else if (messageData.type === "playerImages") {
	// 	leftImage = document.getElementById("leftImage");
	// 	rightImage = document.getElementById("rightImage");
	// 	leftImage.src = "http://localhost:3000/" + messageData.leftImage;
	// 	rightImage.src = "http://localhost:3000/" + messageData.rightImage;
	// }

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
	console.log("ws is ", ws);
	ws.onmessage = handleWebSocketMessage;
	console.log("connecting to server with uid ", playerId);
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
	}
	cancelAnimationFrame(animationId);
	console.log('DESTROYED');
  };
}
onlineGame();
