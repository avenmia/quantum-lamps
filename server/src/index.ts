import express, { Request, Response } from "express";
import { createServer } from "http";
import "dotenv-defaults/config";
import LampsServer from "./LampsServer";
import { catService } from "./LogConfig";

catService.info("Starting quantum lamps client ");
catService.info(`Version ${process.env.VERSION}`);

const app = express();

// define a route handler for the default home page
app.get("/", (_: Request, res: Response) => {
  res.send("Hello world!");
});

const server = createServer(app);
const port = parseInt(process.env.PORT);

new LampsServer(server, port);
