import SharedSecret from "./Secret";
import { Client } from "./Client";
import { MessageType } from "./MessageType";
import { catWSMessages, catState } from "./LogConfig";

let num = 0;

export function ClientResponse(type: string, payload: any) {
  return JSON.stringify({
    type,
    payload,
  });
}

export function onAuthentication(payload: any, ws: any, clients: Client[]) {
  if (SharedSecret === payload.secret) {
    //TODO: Change this num
    num = num++;
    catWSMessages.debug("Secret matches. Adding new client.");
    const client = new Client(payload.username, ws);
    clients.push(client);
    clients.forEach((p) => catState.debug(`person name ${p.username}`));
    ws.send(ClientResponse(MessageType.Username, client.username));
    return clients;
  } else {
    ws.send(ClientResponse("error", "Invalid token"));
    ws.close();
    return clients;
  }
}

export function onInput(payload: any, ws: any, clients: Client[]) {
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
    clients.filter((p) => p.client != ws).forEach((p) => p.client.send(message));
  }
}

export function onListening(payload: any, clients: Client[]) {
  catWSMessages.debug("Client is listening");
}

export function onClose(payload: any, clients: Client[]) {
  // Find person and remove them
  catState.debug("Removing user");
  catState.debug("Closing connection");
}
