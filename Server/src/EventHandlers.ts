import SharedSecret from "./Secret";
import { Client } from "./Clients";
import { MessageType } from "./MessageType";

var num = 0

export function onAuthencation(payload:any, ws:any, people: Client[]) {
    if (SharedSecret === payload.secret) {
      //TODO: Change this num
      num = num++;
      console.log("Secret matches")
      const client = new Client(payload.username, ws);
      people.push(client);
      people.forEach(p => console.log(`person name ${p.username}`));
      ws.send(ClientResponse(MessageType.Username, client.username));
      return people;
    } else {
      ws.send(ClientResponse("error", "Invalid token"));
      ws.close();
      return people;
    }
}

export function onInput(payload:any, people: Client[]){
  console.log("Input received");
  //if (payload !== 0 && typeof payload !== 'undefined'){
  console.log("Sending message")
  const replacer = (key : any, value:any) => typeof value === 'undefined' ? "0" : value;
  let message = JSON.stringify({"type": "Input", "payload": payload }, replacer)
  people.forEach(p => p.client.send(message))
  //}
}

export function onListening(payload: any){
  console.log("Client is listening");
}

export function onClose(payload:any, people: Client[]){
  // Find person and remove them
  console.log("Closing connection");
}

export function ClientResponse(type: string, payload: any){
    return JSON.stringify({
      type,
      payload
    });
  };