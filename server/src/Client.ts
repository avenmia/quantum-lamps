import * as WebSocket from "ws";

export class Client {
  private _username: string;
  private _client: WebSocket;

  constructor(userName: string, ws: WebSocket) {
    this._username = userName;
    this._client = ws;
  }

  get username() {
    return this._username;
  }

  get client() {
    return this._client;
  }
}

export default Client;
