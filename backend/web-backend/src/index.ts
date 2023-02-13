// GNU AGPL v3.0
// Written by John Nunley

import Daemon from "pictodaemon";
import * as dotenv from "dotenv";
import * as express from "express";
import PostgresDatabase from "./postgres";

import { SerializedPipeline } from "libnode";

import * as fs from "fs";
import { join } from "path";

async function main() {
  dotenv.config({
    path: join(__dirname, ".env"),
  });

  // Spawn the daemon.
  const tempDir = await mkdtemp("pictodaemon");
  const daemon = new Daemon(new PostgresDatabase());
  await daemon.init();

  await runExpress(tempDir, daemon)


  // Wait for the daemon to exit.
  await daemon.run()
  process.exit(0)
}

async function runExpress(tempDir: string, daemon: Daemon) {
  const app = express();

  // Handle the /api/upload_image endpoint.
  app.post("/api/upload_image", async (req, res) => {
    // The request body in its entirety is the image; save it to a file on disk.
    const imagePath = join(tempDir, "image.png")
    const writeStream = fs.createWriteStream(imagePath)
    req.pipe(writeStream)

    // Wait for the write to finish.
    await new Promise((resolve, reject) => {
      writeStream.on("finish", resolve)
      writeStream.on("error", reject)
    })

    // Add the image to the daemon.
    const result = await daemon.addImage(imagePath)

    // Send the result.
    res.json(result)
  })

  // Handle the /api/process_image endpoint.
  app.post("/api/process_image", async (req, res) => {
    // The request body is a JSON object that contains the serialized pipeline.
    const body = await new Promise<string>((resolve, reject) => {
      let body = ""
      req.on("data", (chunk) => body += chunk)
      req.on("end", () => resolve(body))
      req.on("error", reject)
    })

    // Parse the JSON.
    const pipeline: SerializedPipeline<any> = JSON.parse(body)

    // Process the image.
    const imageBuffer = await daemon.processImage(pipeline)

    // Send the result as the response body.
    res.send(imageBuffer)
  })

  // Host the public directory.
  app.use(express.static(join(__dirname, "public")))

  // Host HTTP and HTTPS servers.
  const http_port = parseInt(process.env.HTTP_PORT || "80") || 80
  const https_port = parseInt(process.env.HTTPS_PORT || "443") || 443

  app.listen(http_port)
  app.listen(https_port)
}

async function mkdtemp(prefix: string): Promise<string> {
  return new Promise((resolve, reject) => {
    fs.mkdtemp(prefix, (err, folder) => {
      if (err) reject(err);
      else resolve(folder);
    });
  })
}

main()
