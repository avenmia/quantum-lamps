import express from "express";
import * as WebSocket from "ws";
import * as http from "http";
import { Client } from "./Clients";
import * as Event from "./EventHandlers";
import { MessageType } from "./MessageType";
import { Message } from "./Message";
import { catService, catWSMessages, catState } from "./LogConfig";


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
catService.info("Starting Websocket server");

wss.on("connection", (ws: WebSocket) => {

  ws.on("message", (message: string) => {
    try {
      const event: Message = JSON.parse(message);
      catWSMessages.debug(() => `Received a message: ${message}`);
      catWSMessages.debug(() => `type: ${event.type}, payload: ${event.payload}`);
      ws.emit(event.type, event.payload);
    } catch (err) {
      catWSMessages.error("Invalid Message. Message parsed failed.", SyntaxError);
    }
  })
    .on(
      MessageType.Auth,
      payload => (people = Event.onAuthentication(payload, ws, people))
    )
    .on(MessageType.Input, payload => Event.onInput(payload, ws, people))
    .on(MessageType.Listening, payload => Event.onListening(payload, people))
    .on(MessageType.Close, payload => Event.onClose(payload, people));
});

// Every 2 seconds check state of connections
// Todo
setInterval(() => {
  people = people.filter(p => p.client.readyState != WebSocket.CLOSED);
  catState.debug("Current people:");
  people.forEach(p => catState.debug(p.username));
}, 2000);
