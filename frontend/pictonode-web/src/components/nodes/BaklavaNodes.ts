// GNU AGPL v3 License
// Written by Grace Meredith, modified by John Nunley

import { NodeBuilder } from "@baklavajs/core";

export const ImageNode = new NodeBuilder("ImgSrc")
  .setName("Input Image")
  .addOption("Upload image", "UploadOption")
  .addOutputInterface("Result", { index: 0 })
  .build();

export const RenderedNode = new NodeBuilder("ImgOut")
  .setName("Rendered Image")
  .addInputInterface("Image", undefined, undefined, { index: 0 })
  .build();

export const InvertNode = new NodeBuilder("Invert")
  .setName("Invert")
  .addInputInterface("Image", undefined, undefined, { index: 0 })
  .addOutputInterface("Result", { index: 0 })
  .build();

export const CompositeNode = new NodeBuilder("CompOver")
  .setName("Composite")
  .addInputInterface("Top Image", undefined, undefined, { index: 0 })
  .addInputInterface("Bottom Image", undefined, undefined, { index: 1 })
  .addOutputInterface("Result", { index: 0 })
  .build();

export const BriCon = new NodeBuilder("BrightCont")
  .setName("Brightness/Contrast")
  .addInputInterface("Image", undefined, undefined, { index: 0 })
  .addOption("Brightness", "NumberOption", 0)
  .addOption("Contrast", "NumberOption", 0)
  .addOutputInterface("Result", { index: 0 })
  .build();

export const GaussBlur = new NodeBuilder("GaussBlur")
  .setName("Gauss Blur")
  .addInputInterface("Image", undefined, undefined, { index: 0 })
  .addOption("X", "NumberOption", 0)
  .addOption("Y", "NumberOption", 0)
  .addOutputInterface("Result", { index: 0 })
  .build();
