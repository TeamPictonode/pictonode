// GNU AGPL v3 License
// Written by John Nunley

import { expect } from 'chai';
import ImageManager, { AddImageVariant } from '../src/imageManager';

import * as fs from 'fs';
import * as os from 'os';
import * as path from 'path';

import sharp from "sharp";

describe("image management", () => {
  // Set PICTONODE_IMAGE_ROOT to a temporary directory.
  const root = path.join(os.tmpdir(), `pictonode${Math.random()}`);
  fs.mkdirSync(root);

  // Create the image manager.
  const im = new ImageManager(1024 * 1024 * 1024, root);

  // Test image is in ../assets/test.png
  const testImage = path.join(__dirname, "..", "assets", "test-image.png");

  it("should add an image", async () => {
    const result = await im.addImage(testImage);
    expect(result.variant).to.equal(AddImageVariant.Success);

    // There should be an image named 0.webp in the root directory.
    const image = path.join(root, "0.webp");
    const data = fs.readFileSync(image);
    expect(data.length).to.be.greaterThan(0);
  });
})

