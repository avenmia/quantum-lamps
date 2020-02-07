import * as http from 'http';
import * as WebSocket from "ws";
 
const req = http.request(
  {
    host: 'localhost',
    port: 8080,
    method: 'POST',
  },
  response => {
    console.log(response.statusCode); // 200
  }
);

req.write(JSON.stringify({
    light:'first value'
}));
 
req.end();

// remove this hardcode
var clientSocket = new WebSocket.default("ws://localhost:8080");

clientSocket.on("open", () => {
    console.log("Client connection open");
    clientSocket.send("Hello from client");
})

clientSocket.on("message", (message: string) => {
    console.log("client received: %s", message)
})
