import SharedSecret from "./Secret";
import { Client } from "./Clients";

let num = 0

export function onAuthencation(payload:any, ws:any, people: Client[]) {
    if (SharedSecret === payload.secret) {
      num = people.length + 1;
      console.log("Secret matches")
      const client = new Client("client" + num.toString(), ws);
      people.push(client);
      people.forEach(p => console.log(`person name ${p.username}`));
      ws.send(ClientResponse("UserName", client.username));
      return people;
    } else {
      ws.send(ClientResponse("error", "Invalid token"));
      ws.close();
      return people;
    }
}

export function onInput(payload:any, people: Client[]){
  console.log("Input received");
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