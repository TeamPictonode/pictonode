// No Implied Warranty

import { SourceNode, SinkNode } from "../src";

import { expect } from "chai";

describe("Basic Tests", () => {
    let srcNode: SourceNode<number, never>;
    let sinkNode: SinkNode<number, never>;

    it("shouldn't throw errors on construction", () => {
        srcNode = new SourceNode<number, never>(42);
        sinkNode = new SinkNode<number, never>(0);
    });

    it("should be able to form a link", () => {
        sinkNode.link(0, 0, srcNode);
    });

    it("should transmit the value", () => {
        expect(sinkNode.getValue()).to.deep.equal(42);
    });
});
