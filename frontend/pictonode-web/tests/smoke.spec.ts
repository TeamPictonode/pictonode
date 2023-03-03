import { DataType } from "../src/components/nodes/NodeTypes"
import { expect } from "chai";

describe("Smoke Test", () => {
  it("should return a DataType", () => {
   const color = DataType.Color
   const image = DataType.Image

   expect(color).to.eq("color")
   expect(image).to.eq("image")
  });
})