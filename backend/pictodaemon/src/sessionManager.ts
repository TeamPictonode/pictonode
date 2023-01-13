// GNU AGPL v3 License
// Written by John Nunley

import { ID } from "./database";
import { timeout } from "./utils";
import Rng from "./rng";

// Default cleanup interval (2 hours).
const DEFAULT_CLEANUP_INTERVAL = 1000 * 60 * 60 * 2;

// Manages active user sessions.
export default class SessionManager {
  private rng: Rng;

  // The list of active sessions.
  private sessions: Map<string, UserSession>;

  // Number of milliseconds to wait until we clean up old sessions.
  private cleanup: number;

  public constructor(rng: Rng, cleanup?: number) {
    this.rng = rng;
    this.sessions = new Map();
    this.cleanup = cleanup ?? DEFAULT_CLEANUP_INTERVAL;
  }

  // Create a new session for the given user.
  public async createSession(id: ID): Promise<UserSession> {
    const session = new UserSession(this.rng, id);
    const key = await session.getKey();
    this.sessions.set(key, session);
    return session;
  }

  // Get a session by its key.
  public getSession(key: string): UserSession | undefined {
    return this.sessions.get(key);
  }

  // Routinely clean up old sessions.
  public async cleanupSessions(): Promise<never> {
    while (true) {
      const now = new Date();

      // Remove old sessions.
      for (const [key, session] of this.sessions.entries()) {
        const created = session.getCreated();
        const diff = now.getTime() - created.getTime();
        if (diff > this.cleanup) {
          this.sessions.delete(key);
        }
      }

      // Wait for the next cleanup.
      await timeout(this.cleanup);
    }
  }
}

// A user session.
class UserSession {
  // The ID of the user.
  private id: ID;

  // The session key.
  private key: string | undefined;

  // The time the session was created.
  private created: Date;

  private rng: Rng;

  public constructor(rng: Rng, id: ID) {
    this.rng = rng;
    this.id = id;
    this.created = new Date();
    this.key = undefined;
  }

  // Get the ID of the user.
  public getId(): ID {
    return this.id;
  }

  // Get the session key.
  public async getKey(): Promise<string> {
    if (this.key === undefined) {
      this.key = await this.rng.makeString(32);
    }

    return this.key;
  }

  // Get the time the session was created.
  public getCreated(): Date {
    return this.created;
  }
}
