import SharedSecret from "./Secret";
import { Client } from "./Clients";

export function onAuthencation(payload:any, num:number, ws:any, people: Client[]) {
    console.log(payload);
    console.log(SharedSecret);
    if (SharedSecret === payload.secret) {
      const client = new Client("client" + num.toString(), ws);
      num = num++;
      people.push(client);
      people.forEach(p => console.log(`person name ${p.username}`));
    } else {
      ws.send(ClientResponse("error", "Invalid token"));
      ws.close();
    }
}

export function onInput(payload:any){
  console.log("Init received")
}

export function onClose(payload:any){
  
}

export function ClientResponse(type: string, message: any){
    return JSON.stringify({
      type,
      message
    });
  };