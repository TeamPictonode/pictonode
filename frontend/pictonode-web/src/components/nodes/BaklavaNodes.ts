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

export const DisplayNode = new NodeBuilder("DisplayNode")
    .setName("Display")
    .addInputInterface("Value")
    .addOption("ValueText", "TextOption")
    .addOption("Test", "InputOption")
    .onCalculate(n => {
        let value = n.getInterface("Value").value;
        if (typeof value === "number") {
            value = value.toFixed(3);
        }
        n.setOptionValue("ValueText", value);
    })
    .build();

export const ImageNode = new NodeBuilder("InputImage")
    .setName("Input Image")
    .addOption("Upload image", "ButtonOption")
    .addOutputInterface("Result")
    .onCalculate(n => {
        let img = n.getOptionValue("Upload image")
        n.getInterface("Result").value = img
    })
    .build();

export const RenderedNode = new NodeBuilder("RenderedImage")
    .setName("Rendered Image")
    .addInputInterface("Image")
    .onCalculate (n => {
        console.log(n.getInterface("Image").value)
    })
    .build();