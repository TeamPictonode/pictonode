// No Implied Warranty

import { SourceNode, SinkNode, IdentityNode, Ok, CallbackNode } from "../src";
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
        expect(sinkNode.getValue()).to.deep.equal(Ok(42));
    });

    it("should update after a change", () => {
        srcNode.setValue(43);
        expect(sinkNode.getValue()).to.deep.equal(Ok(43));
    });
});

describe("Transmission Tests", () => {
    let srcNode: SourceNode<number, never>;
    let idNode: IdentityNode<[number], never>;
    let sinkNode: SinkNode<number, never>;

    it("shouldn't throw errors on construction/link", () => {
        srcNode = new SourceNode<number, never>(42);
        idNode = new IdentityNode(1, [0]);
        sinkNode = new SinkNode<number, never>(0);

        sinkNode.link(0, 0, idNode);
        idNode.link(0, 0, srcNode);
    });

    it("should transmit the value", () => {
        expect(sinkNode.getValue()).to.deep.equal(Ok(42));
    });

    it("should update after a change", () => {
        srcNode.setValue(43);
        expect(sinkNode.getValue()).to.deep.equal(Ok(43));
    });
});

describe("Multiple Input Tests", () => {
    let srcNode1: SourceNode<number, never>;
    let srcNode2: SourceNode<number, never>;
    let addNode: CallbackNode<[number, number], [number], never>;
    let sinkNode: SinkNode<number, never>;

    it("shouldn't throw errors on construction/link", () => {
        srcNode1 = new SourceNode<number, never>(42);
        srcNode2 = new SourceNode<number, never>(1);
        addNode = new CallbackNode<[number, number], [number], never>(2, 1, [0, 0], (inputs) => Ok([inputs[0] + inputs[1]]));
        sinkNode = new SinkNode<number, never>(0);

        sinkNode.link(0, 0, addNode);
        addNode.link(0, 0, srcNode1);
        addNode.link(1, 0, srcNode2);
    });

    it("should transmit the value", () => {
        expect(sinkNode.getValue()).to.deep.equal(Ok(43));
    });

    it("should update after a change", () => {
        srcNode1.setValue(43);
        expect(sinkNode.getValue()).to.deep.equal(Ok(44));
    });

    it("should update after a change to the other source", () => {
        srcNode2.setValue(2);
        expect(sinkNode.getValue()).to.deep.equal(Ok(45));
    });
});
