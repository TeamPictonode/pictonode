import { getPipeline } from "../src/components/nodes/getPipeline";
import { expect } from "chai";

describe("Smoke Test", () => {
  it("should return a node pipeline", () => {
    const pipeline = getPipeline;

    expect(pipeline).to.not.eq(undefined);
  });
});
