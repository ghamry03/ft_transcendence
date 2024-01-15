import React, { useRef, useEffect, useState } from "react";

const calculateAngle = (playerX, playerY, mouseX, mouseY) => {
  const dx = mouseX - playerX;
  const dy = mouseY - playerY;
  return Math.atan2(dy, dx);
};

const CanvasComponent = () => {
  const canvasRef = useRef(null);
  const [containerSize, setContainerSize] = useState({ width: 0, height: 0 });
  const [gameObjects, setGameObjects] = useState([]);
  const [playerId, setPlayerId] = useState(null);
  const gameObjectsRef = useRef(gameObjects);
  const playerIdRef = useRef(playerId);
  const requestRef = useRef(null);
  const moveSpriteRef = useRef(null);
  const idleSpriteRef = useRef(null);
  const wsRef = useRef(null);

  const coordinateWidth = 1000;
  const coordinateHeight = 1000;

  // Load the idle and move sprites that are used to render the players.
  useEffect(() => {
    const idleImage = new Image();
    idleImage.onload = () => (idleSpriteRef.current = idleImage);
    idleImage.src = "../images/sprite1.jpg";

    const moveImage = new Image();
    moveImage.onload = () => (moveSpriteRef.current = moveImage);
    moveImage.src = "../images/sprite1.jpg";
  }, []);

  // Resize the canvas to fit the width and height of the parent
  // container.  The "logical" canvas is always 1000/1000
  // pixels, so a transform is needed when the physical canvas
  // size does not match.
  const resizeCanvas = () => {
    const canvas = canvasRef.current;
    const ctx = canvas.getContext("2d");
    const boundingRect = canvas.parentNode.getBoundingClientRect();

    const pixelRatio = window.devicePixelRatio || 1;

    canvas.width = boundingRect.width;
    canvas.height = boundingRect.height;

    ctx.setTransform(
      (canvas.width / coordinateWidth) * pixelRatio,
      0,
      0,
      (canvas.height / coordinateHeight) * pixelRatio,
      0,
      0
    );
  };

  // Render each player sprite.  Use context save/restore to apply transforms
  // for that sprite specifically without affecting anything else.
  const drawGameObject = (ctx, obj) => {
    if (!moveSpriteRef.current) return;

    const spriteWidth = 187;
    const spriteHeight = 94;

    ctx.save();
    ctx.translate(obj.x, obj.y);
    ctx.rotate(obj.facing);

    const sprite = obj.thrusting
      ? moveSpriteRef.current
      : idleSpriteRef.current;

    ctx.drawImage(
      sprite,
      0,
      0,
      spriteWidth,
      spriteHeight,
      -spriteWidth / 4,
      -spriteHeight / 4,
      spriteWidth / 3,
      spriteHeight / 3
    );
    ctx.restore();
  };

  // Server messages are either game state updates or the initial
  // assignment of a unique playerId for this client.
  const handleWebSocketMessage = (event) => {
    const messageData = JSON.parse(event.data);
    if (messageData.type === "stateUpdate") {
      setGameObjects(messageData.objects);
    } else if (messageData.type === "playerId") {
      setPlayerId(messageData.playerId);
    }
  };

  // Notify game server of mouse down.
  const handleMouseDown = (event) => {
    if (event.button !== 0 || !playerIdRef.current) return;
    wsRef.current.send(
      JSON.stringify({ type: "mouseDown", playerId: playerIdRef.current })
    );
  };

  // Notify game server of mouse release.
  const handleMouseUp = (event) => {
    if (event.button !== 0 || !playerIdRef.current) return;
    wsRef.current.send(
      JSON.stringify({ type: "mouseUp", playerId: playerIdRef.current })
    );
  };

  // Callback for requestAnimationFrame. Clears the canvas and renders the
  // black background before rendering each individual player sprite.
  const animate = (time) => {
    requestRef.current = requestAnimationFrame(animate);

    const canvas = canvasRef.current;
    const ctx = canvas.getContext("2d");

    ctx.clearRect(0, 0, coordinateWidth, coordinateHeight);

    ctx.fillStyle = "black";
    ctx.fillRect(0, 0, coordinateWidth, coordinateHeight);

    gameObjectsRef.current.forEach((obj) => drawGameObject(ctx, obj));
  };

  // Refresh the gameObjectsRef when gameObjects is updated.  This is necessary
  // because the animate callback triggers the "stale closure" problem.
  useEffect(() => {
    gameObjectsRef.current = gameObjects;
  }, [gameObjects]);

  // Refresh the playerIdRef when playerId is updated.  This is necessary
  // because the animate callback triggers the "stale closure" problem.
  useEffect(() => {
    playerIdRef.current = playerId;
  }, [playerId]);

  // Sets up an interval that calculates the angle between the mouse cursor
  // and the player sprite.  Sends that angle to the game server on a 50ms
  // interval.
  useEffect(() => {
    let mousePosition = { x: 0, y: 0 };

    const updateMousePosition = (event) => {
      const canvas = canvasRef.current;
      const boundingRect = canvas.getBoundingClientRect();
      const scaleX = canvas.width / boundingRect.width;
      const scaleY = canvas.height / boundingRect.height;

      mousePosition.x = (event.clientX - boundingRect.left) * scaleX;
      mousePosition.y = (event.clientY - boundingRect.top) * scaleY;
    };

    window.addEventListener("mousemove", updateMousePosition);

    const intervalId = setInterval(() => {
      const playerId = playerIdRef.current;
      const gameObjects = gameObjectsRef.current;

      if (!playerId) return;
      const playerObj = gameObjects.find((obj) => obj.id === playerId);

      if (playerObj) {
        const facing = calculateAngle(
          playerObj.x,
          playerObj.y,
          mousePosition.x * (coordinateWidth / canvasRef.current.width),
          mousePosition.y * (coordinateHeight / canvasRef.current.height)
        );

        wsRef.current.send(
          JSON.stringify({
            type: "facing",
            playerId,
            facing,
          })
        );
      }
    }, 50);

    return () => {
      clearInterval(intervalId);
      window.removeEventListener("mousemove", updateMousePosition);
    };
  }, []);

  // Entrypoint.  Establish websocket, register input callbacks, and start
  // the animation frame cycle.
  useEffect(() => {
    const canvas = canvasRef.current;

    wsRef.current = new WebSocket("ws://localhost:8000/ws/game/");
    wsRef.current.onmessage = handleWebSocketMessage;

    canvas.addEventListener("mousedown", handleMouseDown);
    canvas.addEventListener("mouseup", handleMouseUp);

    requestRef.current = requestAnimationFrame(animate);
    return () => {
      cancelAnimationFrame(requestRef.current);
      canvas.removeEventListener("mousedown", handleMouseDown);
      canvas.removeEventListener("mouseup", handleMouseUp);
      wsRef.current.close();
    };
  }, []);

  // Call resizeCanvas on initial load and also whenever browser is resized.
  useEffect(() => {
    resizeCanvas();
    window.addEventListener("resize", resizeCanvas);

    return () => {
      window.removeEventListener("resize", resizeCanvas);
    };
  }, [containerSize]);

  return <canvas ref={canvasRef} />;
};

export default CanvasComponent;
console.log("hi");