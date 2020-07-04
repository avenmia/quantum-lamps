import express, { Request, Response } from "express";
import { createServer } from "http";
import "dotenv-defaults/config";
import LampsServer from "./LampsServer";
const app = express();

// define a route handler for the default home page
app.get("/", (_: Request, res: Response) => {
  res.send("Hello world!");
});

const server = createServer(app);
const port = parseInt(process.env.PORT);

new LampsServer(server, port);
