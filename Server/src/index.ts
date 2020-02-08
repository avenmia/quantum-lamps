import express from "express";
import * as WebSocket from "ws";
import * as http from "http";
// import * as Clients from "./Clients";

const app = express();
const port = 8081; // default port to listen

// define a route handler for the default home page
app.get("/", (req, res) => {
  res.send("Hello world!");
});

const server = http.createServer(app);

const AddClient = (message: string) => {
  console.log(message);
  // Add client
};

const ParseMessage = (message: string) => {
  // Change this to handle the different messages sent by the websocket
  message.includes("username") ? AddClient(message) : null;
};

//initialize the WebSocket server instance
const wss = new WebSocket.Server({ port: 8080, server });

wss.on("connection", (ws: WebSocket) => {
  //connection is up, let's add a simple simple event
  ws.on("message", (message: string) => {
    ParseMessage(message);
    //log the received message and send it back to the client
    console.log("received: %s", message);
    ws.send(`Hello, you sent -> ${message}`);
  });

  //send immediatly a feedback to the incoming connection
  ws.send("Hi there, I am a WebSocket server");
  console.log(ws);
});

// start the Express server
app.listen(port, () => {
  console.log(`server started at http://localhost:${port}`);
});
