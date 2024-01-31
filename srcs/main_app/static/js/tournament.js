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
	// var playerImage = document.createElement('img');
	// playerImage.setAttribute('src', 'http://localhost:3000' + imgUrl);
	// playerImage.setAttribute('id', playerId);
	// document.querySelector("#queue").appendChild(playerImage);
}

async function addPlayerImages(playerList) {
	await lock.acquire()
	try {
		var i = 0;
		var playerImages = document.getElementById("queue").children;
		for (const playerId of playerList) {
			// await addImage(playerId);
			if (playerId == 0)
				break
			const imgUrl = await getImage(playerId);
			playerImages[i].setAttribute("src", 'http://localhost:3000' + imgUrl);
			playerImages[i].setAttribute("data-uid", playerId);
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

const handleWebSocketMessage = (event) => {
	const messageData = JSON.parse(event.data);
	
	switch (messageData.type) {
		case "tournamentStarted":
			console.log("Tournament starting... Player list = ");
			printNames(messageData.playerList);
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
			console.log("you're queued or have another ongoing tournament on another tab or computer", playerId);
			ws.close(3001, "Player already in-game");
			// show error pop up and redirect them back to home page 
			break;
		case "playerLeftQueue":
			console.log("Player ", messageData.playerId, " has left the queue");
			removePlayer(messageData.playerId);
			break;
		default:
			// Handle default case if needed
			break;
	}
}

// Entrypoint``1q	
const joinQueue = () => {
	// Set up WebSocket connection
	console.log("uid = ", playerId, " token = ", token);
	ws = new WebSocket("ws://localhost:4000/ws/tour/?uid=" + playerId);
	ws.onmessage = handleWebSocketMessage;
	console.log("ws is ", ws);
	console.log("connecting to server with uid ", playerId);
};

joinQueue();

