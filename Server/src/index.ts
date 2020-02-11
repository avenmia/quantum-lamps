import express from "express";
import * as WebSocket from "ws";
import * as http from "http";
import { Client }from "./Clients";

const app = express();
//const port = 8081; // default port to listen

const clients: WebSocket[] = [];
let people: Client[] = [];

// define a route handler for the default home page
app.get("/", (req, res) => {
  res.send("Hello world!");
});

const server = http.createServer(app);

//initialize the WebSocket server instance
const wss = new WebSocket.Server({ port: 8081, server });

var num = 0;

wss.on("connection", (ws: WebSocket) => {
  //send immediatly a feedback to the incoming connection
  //ws.send("Hi there, I am a WebSocket server");
  var client = new Client("client" + num.toString(), ws);
  num = num + 1;
  people.push(client);
  people.forEach(p => console.log(`person name ${p.username}`));

  //connection is up, let's add a simple simple event
  ws.on("message", (message: string) => {
      parseMessage(message, ws, client);
    //log the received message and send it back to the client

    ws.on("close", (message:string) => {
        ws.send("closing socket");
    })
  });


});

function parseMessage(message:string, ws: WebSocket, client: Client){
    
    var incomingMessage : Message = JSON.parse(message);
    switch(incomingMessage.type){
        case MessageType.Init:
            var clientInfoMessage: Message = {
                type : MessageType.Username,
                message : client.username
            }
            ws.send(JSON.stringify(clientInfoMessage)); break;
        case MessageType.Input: BroadcastMessage(message, client); break;
        case MessageType.Close: ws.close();
    }
}

function BroadcastMessage(message:string, client: Client){
    
    var outgoingMessage: Message = {
        type: MessageType.Input,
        message: "new info"
    };
    console.log(`Broadcasting to clients ${outgoingMessage}`);
    console.log("All people")
    people.forEach(p => console.log(p.username));
    people.filter(p => p.username != client.username).forEach(c => c.client.send(JSON.stringify(outgoingMessage)));
}

enum MessageType {
    Close,
    Init,
    Input,
    Username
}

interface Message
{
    type: MessageType,
    message: string
}

clients.forEach(c => c.close());