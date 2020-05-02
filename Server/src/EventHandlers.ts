import SharedSecret from "./Secret";
import { Client } from "./Clients";
import { MessageType } from "./MessageType";
import { catWSMessages, catState } from "./LogConfig";

let num = 0;

export function ClientResponse(type: string, payload: any) {
  return JSON.stringify({
    type,
    payload
  });
}

export function onAuthentication(payload: any, ws: any, people: Client[]) {
  if (SharedSecret === payload.secret) {
    //TODO: Change this num
    num = num++;
    catWSMessages.debug("Secret matches. Adding new client.");
    const client = new Client(payload.username, ws);
    people.push(client);
    people.forEach(p => catState.debug(`person name ${p.username}`));
    ws.send(ClientResponse(MessageType.Username, client.username));
    return people;
  } else {
    ws.send(ClientResponse("error", "Invalid token"));
    ws.close();
    return people;
  }
}

export function onInput(payload: any, ws: any, people: Client[]) {
  catWSMessages.debug("Input received");
  if (payload !== 0 && typeof payload !== "undefined") {
    catWSMessages.debug("Sending message");
    const replacer = (key: any, value: any) =>
      typeof value === "undefined" ? "0" : value;
    const message = JSON.stringify(
      { type: "Input", payload: payload },
      replacer
    );
    // TODO: Finish this
    people.filter(p => p.client != ws).forEach(p => p.client.send(message));
  }
}

export function onListening(payload: any, people: Client[]) {
  catWSMessages.debug("Client is listening");
}

export function onClose(payload: any, people: Client[]) {
  // Find person and remove them
  catState.debug("Removing user");
  catState.debug("Closing connection");
}
