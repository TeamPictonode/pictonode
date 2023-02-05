// GNU AGPL v3
// Written by John Nunley

import { ID } from "./database";
import { timeout } from "./utils";

import * as fs from "fs";
import * as path from "path";
import * as os from "os";
import sharp from "sharp";

export type AddImageResult =
  | {
      variant: AddImageVariant.Success;
      id: number;
    }
  | {
      variant: AddImageVariant.TooLarge;
    };

export enum AddImageVariant {
  Success = 0,
  TooLarge = 1,
}

export enum ImageInternalType {
  Jpeg = "jpeg",
  Webp = "webp",
  Avif = "avif",
}

export default class ImageManager {
  // The root directory for images.
  private root: string;

  // The maximum size we can reasonably store in disk.
  private maxSize: number;

  // The current size of the image manager.
  private currentSize: number;

  // Map between the numerical ID of an image and the path to the image.
  private imageMap: Map<number, ImageInfo>;

  // The last image ID we used.
  private lastImageId: number;

  // The internal type of the image.
  private internalType: ImageInternalType;

  public constructor(maxSize: number, root: string | undefined) {
    this.maxSize = maxSize;
    this.imageMap = new Map();
    this.lastImageId = 0;
    this.internalType = ImageInternalType.Webp;

    // Root is the tempdir, plus "pictonode{T}" where {T} is a random number.
    if (root !== undefined) {
      this.root = root;
    } else {
      this.root = path.join(
        os.tmpdir(),
        `pictonode${Math.floor(Math.random() * 100000)}`
      );
    }
  }

  // Add the image at the given path to the image manager.
  public async addImage(filePath: string): Promise<AddImageResult> {
    // Check the size of the image.
    const size = await getFileSize(filePath);

    // If the image is too large, return an error.
    if (size + this.currentSize > this.maxSize) {
      return {
        variant: AddImageVariant.TooLarge,
      };
    }

    // Otherwise, copy the image to the image manager.
    // TODO: Make this cryptographically secure
    const id = this.lastImageId++;
    const newPath = path.join(this.root, `${id}.${this.internalType}`);

    await sharp(filePath).toFormat(this.internalType).toFile(newPath);

    // Add the image to the image map.
    this.imageMap.set(
      id,
      new ImageInfo(
        newPath,
        size,
        0, // TODO: Owner
        new Date()
      )
    );

    return {
      variant: AddImageVariant.Success,
      id,
    };
  }

  // Get the path to the image with the given ID.
  public getImagePath(id: number): string | undefined {
    const info = this.imageMap.get(id);
    if (info) {
      return info.getPath();
    } else {
      return undefined;
    }
  }

  // Continually remove old images.
  public async cleanupImages(): Promise<never> {
    while (true) {
      const now = new Date();

      // Remove old images.
      const ids = Array.from(this.imageMap.keys());
      for (const id of ids) {
        const info = this.imageMap.get(id)!;
        const age = now.getTime() - info.getCreated().getTime();
        if (age > 1000 * 60 * 60 * 24) {
          // The image is older than a day, remove it.
          await deleteFile(info.getPath());
          this.imageMap.delete(id);
        }
      }

      // Wait for 15 minutes.
      await timeout(1000 * 60 * 15);
    }
  }
}

class ImageInfo {
  // The path to the image on the disk.
  private path: string;

  // The size of the image in bytes.
  private size: number;

  // The Id of the user who owns the image.
  private owner: ID;

  // The date the image was created.
  private created: Date;

  public constructor(path: string, size: number, owner: ID, created: Date) {
    this.path = path;
    this.size = size;
    this.owner = owner;
    this.created = created;
  }

  public getPath(): string {
    return this.path;
  }

  public getSize(): number {
    return this.size;
  }

  public getOwner(): ID {
    return this.owner;
  }

  public getCreated(): Date {
    return this.created;
  }
}

// Get the size of a file.
function getFileSize(path: string): Promise<number> {
  return new Promise((resolve, reject) => {
    fs.stat(path, (err, stats) => {
      if (err) {
        reject(err);
      } else {
        resolve(stats.size);
      }
    });
  });
}

// Remove an image.
function deleteFile(path: string): Promise<void> {
  return new Promise((resolve, reject) => {
    fs.unlink(path, (err) => {
      if (err) {
        reject(err);
      } else {
        resolve();
      }
    });
  });
}
