// GNU AGPL v3.0
// Written by John Nunley

import express from "express"

async function main() {
  // Take the first argument as our port 
  const port = parseInt(process.argv[2] || "2407") || 2407

  const app = express()

  // TODO: Middleware

  // TODO: Make sure no one steps on our toes.
  app.listen(port)
}

main()
