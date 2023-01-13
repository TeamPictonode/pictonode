// GNU AGPL v3
// Written by John Nunley

import * as crypto from "crypto"

export default class Rng {
  private static RANDOM: Rng | undefined = undefined;

  public constructor() {
    if (Rng.RANDOM !== undefined) {
      return Rng.RANDOM;
    }

    Rng.RANDOM = this;
  }

  // Generate a new random number in the given range.
  public makeNumber(min: number, max: number): Promise<number> {
    return new Promise((resolve, reject) => {
      // Generate the number.
      crypto.randomInt(min, max, (err, num) => {
        if (err) {
          reject(err);
        } else {
          resolve(num);
        }
      })
    })
  }

  // Generate a random string of the given length.
  public makeString(length: number): Promise<string> {
    return new Promise((resolve, reject) => {
      crypto.randomBytes(length, (err, buf) => {
        if (err) {
          reject(err);
        } else {
          resolve(buf.toString("hex"));
        }
      })
    })
  }
};