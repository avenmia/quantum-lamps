import express from "express";
import * as WebSocket from "ws";
import * as http from "http";
//import * as dotenv from "dotenv";
import { Client } from "./Clients";
import SharedSecret from "./Secret";
import * as Event from "./EventHandlers";
import { MessageType } from "./MessageType";
import { Message } from "./Message";

const port = parseInt(process.env.PORT) || 8081;
const app = express();

const clients: WebSocket[] = [];
let people: Client[] = [];

// define a route handler for the default home page
app.get("/", (req, res) => {
  res.send("Hello world!");
});

const server = http.createServer(app);

//initialize the WebSocket server instance
const wss = new WebSocket.Server({ port, server });
console.log("Starting Websocket server");
let num = 0;

wss.on("connection", (ws: WebSocket) => {
  //send immediately a feedback to the incoming connection
  //ws.send("Hi there, I am a WebSocket server");
  ws.on("message", (message: string) => {
    try {
      const event : Message = JSON.parse(message);
      console.log("Received a message %o", message);
      console.log("type: %o, payload: %o",event.type, event.payload);
      ws.emit(event.type, event.payload);
    } catch (err) {
      console.error("JSON Parse Failed");
    }
  })
  .on(MessageType.Auth, payload => people = Event.onAuthencation(payload, ws, people))
  .on(MessageType.Input, payload => Event.onInput(payload, people))
  .on(MessageType.Close, payload => Event.onClose(payload, people))

});

function parseMessage(message: string, ws: WebSocket, client: Client) {
  const incomingMessage: Message = JSON.parse(message);
  console.log("incoming message: %o", incomingMessage);
  switch (incomingMessage.type) {
    case MessageType.Auth:
      console.log(`Init received from: ${client.username}`);
      const clientInfoMessage: Message = {
        type: MessageType.Username,
        payload: client.username
      };
      console.log("Sending: %o", clientInfoMessage);
      ws.send(JSON.stringify(clientInfoMessage));
      break;
    case MessageType.Input:
      console.log(`Input message received`);
      BroadcastMessage(message, client);
      break;
    case MessageType.Closing:
      const closingMessage: Message = {
        type: MessageType.Close,
        payload: "closing connection"
      };
      console.log("Closing message received");
      ws.send(JSON.stringify(closingMessage));
    case MessageType.Close:
      // Close out message will contain username to delete
      console.log("Removing", incomingMessage.payload);
      people = people.filter(p => p.username != incomingMessage.payload);
      ws.close();
  }
}

function BroadcastMessage(message: string, client: Client) {
  let parsedMessage = JSON.parse(message);
  console.log("broadcasting info message: %o", parsedMessage);
  const outgoingMessage: Message = {
    type: MessageType.Input,
    payload: "new info"
  };
  console.log(`Broadcasting to clients ${outgoingMessage}`);
  console.log("All people");
  people.forEach(p => console.log(p.username));
  people
    .filter(p => p.username != client.username)
    .forEach(c => c.client.send(JSON.stringify(outgoingMessage)));
}

clients.forEach(c => c.close());
