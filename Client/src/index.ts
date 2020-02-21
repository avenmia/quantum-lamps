import * as http from "http";
import * as WebSocket from "ws";
import { Client } from "./Client";
 
const req = http.request(
  {
    host: "localhost",
    port: 8081,
    method: "POST",
  },
  response => {
    console.log(response.statusCode); // 200
  }
);

req.write(JSON.stringify({
    light:"first value"
}));
 
req.end();

// remove this hardcode
const clientSocket = new WebSocket.default("ws://localhost:8081");

var client: Client;

clientSocket.on("open", () => {
    console.log("Client connection open");
    var message: Message = {
        type : MessageType.Init,
        message: "Init"
    }
    clientSocket.send(JSON.stringify(message));
});

clientSocket.on("message", (message: string) => {
    console.log("client received: %s", message);
    var returnMessage: string = parseMessage(message);
    clientSocket.send(returnMessage);
});

function parseMessage(message:string){
    console.log(`parsing message ${message}`);
    var serverMessage : Message = JSON.parse(message);
    console.log(serverMessage);
    console.log("Sending initial data");
    switch(serverMessage.type){
        case MessageType.Username: 
            client = new Client(serverMessage.message); 
            console.log(`setting up client: ${client.username}`);
            
            var dataMessage: Message = {
                type : MessageType.Input,
                message: "255,255,255"
            }
            return JSON.stringify(dataMessage);
        case MessageType.Init: return JSON.stringify({type: MessageType.Input, message: "init"});
        case MessageType.Input: return JSON.stringify({type: MessageType.Close, message: "setting data then closing connection"});
        case MessageType.Close: clientSocket.close();
    }
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
