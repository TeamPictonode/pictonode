// GNU AGPL v3.0
// Written by John Nunley

import Database from "./database";
import ImageManager, { AddImageResult } from "./imageManager";
import Rng from "./rng";
import SessionManager from "./sessionManager";

// The background daemon for Pictonode.
export default class Daemon {
  private db: Database;
  private cancelFunc: () => void;
  private rng: Rng;
  private imManager: ImageManager;
  private smManager: SessionManager;

  public constructor(db: Database) {
    this.db = db;
    this.cancelFunc = () => {};
    this.rng = new Rng();
    this.imManager = new ImageManager(1024 * 1024 * 1024);
    this.smManager = new SessionManager(this.rng);
  }

  // Initialize the daemon.
  public async init(): Promise<void> {
    await this.db.init();
  }

  // A runner for background tasks in the daemon.
  public async run(): Promise<void> {
    let running = true;

    // This promise waits for the cancel function to be called.
    const cancelPromise = new Promise<void>((resolve) => {
      this.cancelFunc = () => {
        running = false;
        resolve();
      };
    });

    while (running) {
      // Race the promises against eachother.
      const promises = [cancelPromise, this.smManager.cleanupSessions(), this.imManager.cleanupImages()];
      await Promise.race(promises);
    }
  }

  // Add an image to the daemon.
  public async addImage(image: string): Promise<AddImageResult> {
    return this.imManager.addImage(image);
  }

  // Get an image from the daemon.
  public async getImage(id: number): Promise<string | undefined> {
    return this.imManager.getImagePath(id);
  }


  // Cancel the daemon.
  // 
  // If the daemon is `run()`ing, this will cause it to stop.
  public cancel(): void {
    this.cancelFunc();
  }
};
