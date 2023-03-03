import { getPipeline } from "../src/components/nodes/getPipeline";
import { expect } from "chai";

describe("Smoke Test", () => {
  it("should create a pipeline", () => {
    const pipeline = getPipeline;

    expect(pipeline).to.not.eq(undefined)
  });
})