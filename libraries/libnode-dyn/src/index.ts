// No Implied Warranty

import { Result, Unit } from "pictotypes";
import { Node, Link } from "libnode";

type Names<T extends [...any[]]> = {
    [K in keyof T]: string;
} & { "length": T["length"] };

export abstract class DynamicNode<Input extends [...any[]], Output extends [...any[]], E> extends Node<Input, Output, E> {
    public constructor(inputCount: number, outputCount: number, defaults: Input) {
        super(inputCount, outputCount, defaults);
    }

    /**
     * The names of the input types for the nodes.
     */
    public abstract readonly inputTypes: Names<Input>;

    /**
     * The names of the output types for the nodes.
     */
    public abstract readonly outputTypes: Names<Output>;
};

/**
 * A wrapper around a `DynamicNode` that erases the type information.
 */
export class NodeDyn<E> {
    /**
     * The node that this wrapper is wrapping.
     */
    private readonly node: DynamicNode<any[], any[], E>;

    /**
     * A caster that casts the inputs to the correct types.
     */
    private caster: Caster<E>;

    /**
     * Create a new `NodeDyn` from a `DynamicNode`.
     */
    public constructor(node: DynamicNode<any[], any[], E>, caster: Caster<E>) {
        this.node = node;
        this.caster = caster;
    } 

    /**
     * Get the names of the input types for the nodes.
     */
    public inputTypes(): string[] {
        return this.node.inputTypes;
    }

    /**
     * Get the names of the output types for the nodes.
     */
    public outputTypes(): string[] {
        return this.node.outputTypes;
    }

    /**
     * Get the inputs for the node.
     */
    public getInputs(): Link<any, E>[] {
        return this.node.getInputs(); 
    }

    /**
     * Get the outputs for the node.
     */
    public getOutputs(): Link<any, E>[] {
        return this.node.getOutputs();
    }

    /**
     * Link to another node.
     */
    public link(thisKey: number, otherKey: number, other: NodeDyn<E>): Result<boolean, E> {
        // Check the output type and input type to ensure they can be cast properly.
        if (!this.caster.canCast(other.outputTypes()[otherKey], this.inputTypes()[thisKey])) {
            return Result.ok(false);
        }

        return this.node.link(thisKey, otherKey, other.node).map(_ => {
            // Set the caster callback to cast the output to the input type.
            this.getInputs()[thisKey].setCallback((value: any) => {
                return this.caster.cast(other.outputTypes()[otherKey], this.inputTypes()[thisKey], value);
            });

            return true;
        });
    }
}

/**
 * It may be possible to cast one type to another type through a "cast".
 */
export class Caster<E> {
    /**
     * Map a value from one type to another type.
     */
    private castMap: Map<[string, string], (value: any) => Result<any, E>> = new Map();

    public constructor() {}
    
    /**
     * Register a cast from one type to another type.
     */
    public registerCast(from: string, to: string, cast: (value: any) => Result<any, E>): void {
        this.castMap.set([from, to], cast);
    }

    /**
     * Tell if we can cast from one type to another type.
     */
    public canCast(from: string, to: string): boolean {
        return this.castMap.has([from, to]);
    }

    /**
     * Cast a value from one type to another type.
     */
    public cast(from: string, to: string, value: any): Result<any, E> {
        if (from.toLowerCase() === to.toLowerCase()) {
            return Result.ok(value);
        }

        const cast = this.castMap.get([from, to]);
        if (cast === undefined) {
            // TODO: This is bogus, replace it with a proper error.
            throw new Error(`Cast from ${from} to ${to} not found`);
        }
        return cast!(value);
    }
}
