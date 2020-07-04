import * as WebSocket from "ws";
import {
  onAuthentication,
  onInput,
  onListening,
  onClose,
} from "./EventHandlers";
import { MessageType } from "./MessageType";
import { Message } from "./Message";
import { catService, catWSMessages, catState } from "./LogConfig";
import { Client } from "./Client";
import { Server } from "http";

export class LampsServer {
  private _server: Server;
  private _port: number;
  private _clients: Client[] = [];
  private _wss: WebSocket.Server;

  constructor(server: Server, port: number) {
    this._server = server;
    this._port = port;
    this._wss = new WebSocket.Server({ port, server });
    catService.info("Starting Websocket server");

    this._registerEventHandlers();

    // Every 2 seconds check state of connections
    // Todo
    setInterval(() => {
      this._clients = this._clients.filter((p) => p.client.readyState != WebSocket.CLOSED);
      catState.debug("Connected Clients:");
      this._clients.forEach((p) => catState.debug(p.username));
    }, 2000);
  }

  private _registerEventHandlers() {
    this._wss.on("connection", (ws: WebSocket) => {
      ws.on("message", (message: string) => {
        try {
          const { type, payload }: Message = JSON.parse(message);
          catWSMessages.debug(() => `Received a message: ${message}`);
          catWSMessages.debug(() => `type: ${type}, payload: ${payload}`);
          ws.emit(type, payload);
        } catch (err) {
          catWSMessages.error(
            "Invalid Message. Message parsed failed.",
            SyntaxError
          );
        }
      })
        .on(
          MessageType.Auth,
          (payload) => (this._clients = onAuthentication(payload, ws, this._clients))
        )
        .on(MessageType.Input, (payload) => onInput(payload, ws, this._clients))
        .on(MessageType.Listening, (payload) => onListening(payload, this._clients))
        .on(MessageType.Close, (payload) => onClose(payload, this._clients));
    });
  }
}

export default LampsServer;
