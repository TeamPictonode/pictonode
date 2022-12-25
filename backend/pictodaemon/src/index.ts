// GNU AGPL v3.0
// Written by John Nunley

import Database from "./database";

export default class Daemon {
  private db: Database;

  public constructor(db: Database) {
    this.db = db;
  }

  public async init(): Promise<void> {
    await this.db.init();
  }
};