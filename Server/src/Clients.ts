import * as WebSocket from "ws";
export class Client {
  constructor(userName: string, ws: WebSocket) {
    this.username = userName;
    this.client = ws;
  }
  username: string;
  client: WebSocket;
}
