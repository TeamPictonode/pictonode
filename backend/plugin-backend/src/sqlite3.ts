// GNU AGPL v3.0
// Written by John Nunley

import { Database, User, NewUser, UpdateUser } from "pictodaemon"

import * as sqlite from "sqlite"
import { Database as Sqlite3Database } from "sqlite3"

import * as fs from "fs"

// A database that uses SQLite3.
export default class SqliteDatabase extends Database {
  private sqlitePath: string;
  private inner: sqlite.Database<Sqlite3Database> | undefined;

  public constructor(path: string) {
    super();
    this.sqlitePath = path;
    this.inner = undefined;
  }

  public async init(): Promise<void> {
    const dbExists = await exists(this.sqlitePath);      

    // Open the database.
    this.inner = await sqlite.open({
      filename: this.sqlitePath,
      driver: Sqlite3Database
    })

    // Create the tables if they don't exist.
    if (!dbExists) {
      // Create the users table.
      await this.inner.run(`
        CREATE TABLE users (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          username TEXT NOT NULL UNIQUE,
          realname TEXT NOT NULL
        )
      `);
    }
  }

  public async getUser(id: number): Promise<User> {
    if (!this.inner) throw new Error("Database not initialized.");

    const row = await this.inner.get("SELECT * FROM users WHERE id = ?", id);
    return {
      id: row.id,
      username: row.username,
      realname: row.realname
    };
  }

  public async addUser(user: NewUser): Promise<User> {
    if (!this.inner) throw new Error("Database not initialized.");

    const row = await this.inner.run(`
      INSERT INTO users (username, realname)
      VALUES (?, ?)
    `, user.username, user.realname);

    if (!row.lastID) throw new Error("Failed to add user.");

    return {
      id: row.lastID,
      username: user.username,
      realname: user.realname
    };
  }

  public async updateUser(user: UpdateUser): Promise<void> {
    if (!this.inner) throw new Error("Database not initialized.");

    // Make sure we don't set a row to undefined.
    const row = await this.inner.run(`
      UPDATE users
      SET username = COALESCE(?, username),
          realname = COALESCE(?, realname)
      WHERE id = ?
    `, user.username, user.realname, user.id);

    if (!row.changes) throw new Error("Failed to update user.");
  }
}

function exists(path: string): Promise<boolean> {
  return new Promise((resolve) => {
    fs.access(path, fs.constants.F_OK, (err) => {
      resolve(!err);
    })
  })
}
