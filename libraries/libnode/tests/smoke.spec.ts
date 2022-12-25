// GNU AGPL v3 License
// Written by John Nunley

import {
  TemplateTable,
  NodeTemplate,
  LinkTemplate,
  Link,
  Pipeline,
} from "../src";
import { expect } from "chai";

type Unit = Record<never, string>;

describe("Smoke Test", () => {
  // We will create a basic pipeline for arithmetic operations.
  const templates = new TemplateTable<number, Unit>();

  it("should create a template table", () => {
    function munchTwoNumbers(
      link: Array<Link<number, Unit>>
    ): [number, number] {
      if (link.length !== 2) throw new Error("Expected two numbers");
      if (link[0] === undefined) throw new Error("Expected first number");
      if (link[1] === undefined) throw new Error("Expected second number");

      return [link[0].get(), link[1].get()];
    }

    // Add input and output templates.
    templates.addTemplate(
      "input",
      new NodeTemplate((_) => [-2], [], [new LinkTemplate({}, -1)], {})
    );
    templates.addTemplate(
      "output",
      new NodeTemplate((_) => [], [new LinkTemplate({}, 0)], [], {})
    );

    // Add add, subtract, multiply, and divide templates.
    templates.addTemplate(
      "add",
      new NodeTemplate(
        (arr) => {
          const [a, b] = munchTwoNumbers(arr);
          return [a + b];
        },
        [new LinkTemplate({}, 0), new LinkTemplate({}, 0)],
        [new LinkTemplate({}, -1)],
        {}
      )
    );
    templates.addTemplate(
      "subtract",
      new NodeTemplate(
        (arr) => {
          const [a, b] = munchTwoNumbers(arr);
          return [a - b];
        },
        [new LinkTemplate({}, 0), new LinkTemplate({}, 0)],
        [new LinkTemplate({}, -1)],
        {}
      )
    );
  });

  let pipeline;
  let input1;
  let input2;
  let output;
  it("should create a pipeline", () => {
    pipeline = new Pipeline(templates);

    input1 = pipeline.createNode("input", {});

    input2 = pipeline.createNode("input", {});

    output = pipeline.createNode("output", {});

    expect(input1).not.to.eq(undefined);
    expect(input2).not.to.eq(undefined);
    expect(output).not.to.eq(undefined);
  });
});
