// GNU AGPL v3.0
// Written by John Nunley

import sharp, { Sharp } from "sharp";
import {
  SerializedPipeline,
  deserializePipeline,
  TemplateTable,
} from "libnode";
import ImageManager from "./imageManager";

export type ProcessingResult = ProcessingMidResult<Buffer>;

type ProcessingMidResult<T> =
  | {
      type: ProcessingResultType.Success;
      image: T;
    }
  | {
      type: ProcessingResultType.ImageNotFound;
      missing: Array<number>;
    }
  | {
      type: ProcessingResultType.Error;
      error: string;
    };

export enum ProcessingResultType {
  Success,
  ImageNotFound,
  Error,
}

export default async function process(
  pipeline: SerializedPipeline<any>,
  images: ImageManager
): Promise<ProcessingResult> {
  // Deserialize the pipeline.
  const deserialized = deserializePipeline<ProcessingMidResult<Sharp>, any>(
    pipeline,
    templateTable()
  );

  // Set the metadata of all nodes to the image manager.
  for (const node of deserialized.getNodes()) {
    node.setMetadata(images);
  }

  // TODO: Add outputs to the pipeline serialization format.
  const outputId = -1;
  const outputNode = deserialized.getNode(outputId);
  if (outputNode === undefined) {
    return {
      type: ProcessingResultType.Error,
      error: "Output node not found",
    };
  }

  // Get the first output of the output node.
  const outputLink = outputNode.getInputs()[0];
  if (outputLink === undefined) {
    return {
      type: ProcessingResultType.Error,
      error: "Output not found",
    };
  }

  // Get the final output.
  const finalOutput = outputLink.get();
  let imageDescription;
  if (finalOutput.type !== ProcessingResultType.Success) {
    return finalOutput;
  } else {
    imageDescription = finalOutput.image;
  }

  // Process the pipeline.
  const result = await imageDescription.webp().toBuffer();

  return {
    type: ProcessingResultType.Success,
    image: result,
  };
}

function templateTable(): TemplateTable<ProcessingMidResult<Sharp>, any> {
  const table = new TemplateTable<ProcessingMidResult<Sharp>, any>();

  // TODO: Add all the templates here.

  return table;
}
