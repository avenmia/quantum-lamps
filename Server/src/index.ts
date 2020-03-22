import express from "express";
import * as WebSocket from "ws";
import * as http from "http";
import { Client } from "./Clients";
import * as Event from "./EventHandlers";
import { MessageType } from "./MessageType";
import { Message } from "./Message";

const port = parseInt(process.env.PORT) || 8081;
const app = express();

let people: Client[] = [];

// define a route handler for the default home page
app.get("/", (req, res) => {
  res.send("Hello world!");
});

const server = http.createServer(app);

//initialize the WebSocket server instance
const wss = new WebSocket.Server({ port, server });
console.log("Starting Websocket server");

wss.on("connection", (ws: WebSocket) => {
  //send immediately a feedback to the incoming connection
  //ws.send("Hi there, I am a WebSocket server");
  ws.on("message", (message: string) => {
    try {
      const event: Message = JSON.parse(message);
      console.log("Received a message %o", message);
      console.log("type: %o, payload: %o", event.type, event.payload);
      ws.emit(event.type, event.payload);
    } catch (err) {
      console.error("JSON Parse Failed");
    }
  })
    .on(
      MessageType.Auth,
      payload => (people = Event.onAuthentication(payload, ws, people))
    )
    .on(MessageType.Input, payload => Event.onInput(payload, people))
    .on(MessageType.Listening, payload => Event.onListening(payload, people))
    .on(MessageType.Close, payload => Event.onClose(payload, people));
});

// Every 2 seconds check state of connections
// Todo
setInterval(() => {
  people = people.filter(p => p.client.readyState != WebSocket.CLOSED);
  console.log("Current people");
  people.forEach(p => console.log(p.username));
}, 2000);
