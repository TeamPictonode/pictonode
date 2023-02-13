// GNU AGPL v3.0
// Written by John Nunley

import Daemon from "pictodaemon"
import express from "express"
import SqliteDatabase from "./sqlite3"

import { SerializedPipeline } from "libraries/libnode/src"

import * as fs from "fs"
import { join } from "path"

async function main() {
  // Spawn the daemon.
  const tempDir = await mkdtemp("pictodaemon") 
  const daemon = new Daemon(new SqliteDatabase(join(tempDir, "db.sqlite3")))
  await daemon.init()

  await runExpress(tempDir, daemon)

  // Wait for the daemon to exit.
  await daemon.run()
  process.exit(0)
}

async function runExpress(tempDir: string, daemon: Daemon) {
  // Take the first argument as our port 
  const port = parseInt(process.argv[2] || "2407") || 2407

  const app = express()

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

  // TODO: Middleware

  // TODO: Make sure no one steps on our toes.
  app.listen(port)
}

async function mkdtemp(prefix: string): Promise<string> {
  return new Promise((resolve, reject) => {
    fs.mkdtemp(prefix, (err, folder) => {
      if (err) reject(err)
      else resolve(folder)
    })
  })
}

main()
