// No Implied Warranty

import { Node } from "libnode";
import { Result } from "pictotypes";

/**
 * A node that can be serialized to and from JSON.
 */
export abstract class SerializableNode<Input extends [...any[]], Output extends [...any[]], E> extends Node<Input, Output, E> {
    public constructor(inputCount: number, outputCount: number, defaults: Input) {
        super(inputCount, outputCount, defaults);
    }

    /**
     * The name of the node.
     */
    public abstract readonly name: string;

    /**
     * Serialize this node's values to a JSON object.
     */
    public abstract serialize(): Result<any, E>;

    /**
     * Deserialize this node's values from a JSON object.
     */
    public abstract deserialize(json: any): Result<void, E>;
};

/**
 * A wrapper around a function that creates an empty version of a node.
 */
export interface NodeFactory<Input extends [...any[]], Output extends [...any[]], E> {
    (): SerializableNode<Input, Output, E>;
};

/**
 * A set of functions that can be used to serialize and deserialize a node.
 */
export class Serializer<E> {
    /**
     * A map of node names to node factories.
     */
    private readonly factories: Map<string, NodeFactory<any[], any[], E>>;
}
