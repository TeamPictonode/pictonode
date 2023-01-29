// GNU AGPL v3.0
// Written by John Nunley

import { Database, User, NewUser, UpdateUser } from "pictodaemon";

import { Pool } from "pg";

// Database that uses PostgreSQL.
export default class PostgresDatabase extends Database {
  private pq: Pool;

  public constructor() {
    super();

    const cfg = {
      user: process.env.POSTGRES_USER,
      host: process.env.POSTGRES_HOST,
      database: process.env.POSTGRES_DB,
      password: process.env.POSTGRES_PASSWORD,
      port: parseInt(process.env.POSTGRES_PORT ?? "5432")
    };

    console.log(JSON.stringify(cfg))

    this.pq = new Pool(cfg) 
  }

  public async init(): Promise<void> {
    // Create the users table if it doesn't exist.
    await this.pq.query(`
      CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        username VARCHAR(255) UNIQUE NOT NULL,
        realname VARCHAR(255) UNIQUE NOT NULL
      )
    `);
  }

  public async getUser(id: number): Promise<User> {
    const row = await this.pq.query(`
      SELECT * FROM users WHERE id = $1
    `, [id]);

    if (row === undefined) throw new Error("User not found.");
    
    const entry = row.rows[0];
    if (entry === undefined) throw new Error("User not found.");

    return {
      id: entry.id,
      username: entry.username,
      realname: entry.realname
    };
  }

  public async addUser(user: NewUser): Promise<User> {
    const row = await this.pq.query(`
      INSERT INTO users (username, realname)
      VALUES ($1, $2)
      RETURNING *
    `, [user.username, user.realname]);

    if (row === undefined) throw new Error("User not added.");

    const entry = row.rows[0];
    if (entry === undefined) throw new Error("User not added.");

    return {
      id: entry.id,
      username: entry.username,
      realname: entry.realname
    };
  }

  public async updateUser(user: UpdateUser): Promise<void> {
    // user.username and user.realname may be undefined, don't set it if it is.
    const row = await this.pq.query(`
      UPDATE users
      SET username = COALESCE($1, username),
          realname = COALESCE($2, realname)
      WHERE id = $3
      RETURNING *
    `, [user.username, user.realname, user.id]);

    if (row === undefined) throw new Error("User not updated.");

    const entry = row.rows[0];
    if (entry === undefined) throw new Error("User not updated.");
  }
}
