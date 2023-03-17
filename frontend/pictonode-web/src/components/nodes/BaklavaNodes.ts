import { NodeBuilder } from "@baklavajs/core";

export const MathNode = new NodeBuilder("MathNode")
    .setName("Math Node")
    .addInputInterface("Number 1", "NumberOption", 1)
    .addInputInterface("Number 2", "NumberOption", 10)
    .addOption("Operation", "SelectOption", "Add", undefined, { items: ["Add", "Subtract"] })
    .addOutputInterface("Result")
    .onCalculate(n => {
        let value1 = n.getInterface("Number 1").value;
        let value2 = n.getInterface("Number 2").value;
        let operation = n.getOptionValue("Operation");
        let result
        if (operation === "Add") {
          result = value1 + value2;
      } else if (operation === "Subtract") {
          result = value1 - value2;
      }
        n.getInterface("Result").value = result;
    })
    .build();

export const ImageNode = new NodeBuilder("InputImage")
    .setName("Input Image")
    .addOption("Upload image", "ButtonOption")
    .addOutputInterface("Result")
    .build();

export const RenderedNode = new NodeBuilder("RenderedImage")
    .setName("Rendered Image")
    .addInputInterface("Image")
    .onCalculate (n => {
        
    })
    .build();