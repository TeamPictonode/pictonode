// No Implied Warranty

/**
 * An empty object.
 */
export type Unit = Record<string, never>;

/**
 * A result type that can be either a success or a failure.
 */
export type Result<T, E> = { ok: true, value: T } | { ok: false, error: E };


function Ok<T, E>(value: T): Result<T, E> {
    return { ok: true, value };
}


function Err<T, E>(error: E): Result<T, E> {
    return { ok: false, error };
}


function map_res<T, U, E>(result: Result<T, E>, func: (value: T) => U): Result<U, E> {
    if (result.ok) {
        return Ok(func(result.value));
    } else {
        return Err(result.error);
    }
}


/**
 * An optional type that can either be a value or defined.
 */
export type Option<T> = { defined: true, value: T } | { defined: false };


function Some<T>(value: T): Option<T> {
    return { defined: true, value };
}


function None<T>(): Option<T> {
    return { defined: false };
}


function unwrap_opt<T>(option: Option<T>): T {
    if (option.defined) {
        return option.value;
    } else {
        throw new Error("Option is not defined");
    }
}


/**
 *  Interface for a type-erased node.
 */
interface NodeBase<E> {
    // Hydrate this node.
    // 
    // Returns "true" if the node was changed during hydration.
    hydrate(): Result<boolean, E>;
}


/**
 * A link from one node to another.
 * 
 * Essentially a channel with only one item.
 */
export class Link<T, E> {
    // The inner value, if it exists.
    private value: Option<T>;

    // The node that the input side of this link is connected to.
    private input: NodeBase<E>;

    // Whether this link has been updated since the last hydration.
    private updated: boolean;

    constructor(nb: NodeBase<E>) {
        this.value = None();
        this.input = nb;
        this.updated = false;
    }

    // Store a value in this link.
    public setValue(value: T): void {
        this.value = Some(value);
        this.updated = true;
    }

    // Whether this link is in need of hydration.
    public needsHydration(): boolean {
        return this.updated;
    }

    // Hydrate this link.
    public hydrate(): Result<boolean, E> {
        // Hydrate the input node.
        // 
        // setValue() will be called as a result of hydration.
        return map_res(this.input.hydrate(), hydrated => hydrated || this.updated);
    }

    // Get the value stored in this link.
    // 
    // Returns true if the value was hydrated.
    public getValue(): Result<[T, boolean], E> {
        // Hydrate ourselves first if necessary.
        // 
        // After a hydration, the value will be set.
        return map_res(this.hydrate(), hydrated => {
            return [unwrap_opt(this.value), hydrated];
        });
    }
};


type InputSpigots<List extends [...any[]], E> = {
    [Key in keyof List]: Spigot<List[Key], E>;
} & { length: List["length"] };


type OutputSinks<List extends [...any[]], E> = {
    [Key in keyof List]: Sink<List[Key], E>;
} & { length: List["length"] };


/**
 * A node that can be used to create a graph.
 */
export abstract class Node<Inputs extends [...any[]], Outputs extends [...any[]], E> {
    // The input spigots we receive value from.
    private inputs: InputSpigots<Inputs, E>;

    // The output sinks we send values to.
    private outputs: OutputSinks<Outputs, E>; 

    // Convert the set of inputs into the set of outputs.
    protected abstract convert(inputs: Inputs): Result<Outputs, E>;

    protected constructor(numInputs: number, numOutputs: number) {
        for (let i = 0; i < numInputs; i++) {
            this.inputs[i] = new Spigot(this);
        }

        for (let i = 0; i < numOutputs; i++) {
            this.outputs[i] = new Sink(this);
        }
    }

    // Get the list of input spigots.
    public getInputs(): InputSpigots<Inputs, E> {
        return this.inputs;
    }

    // Get the list of output sinks.
    public getOutputs(): OutputSinks<Outputs, E> {
        return this.outputs;
    }

    // Set the input value at the given index.
    public setInput(index: number, value: Inputs[number]): void {
        this.inputs[index]!.setValue(value);
    }

    // Get the output value at the given index.
    public getOutput(index: number): Result<Outputs[number], E> {
        return map_res(this.outputs[index]!.getValue(), value => value[0]);
    }

    // Hydrate this node, checking the inputs for updated and propagating them
    // to the outputs.
    hydrate(): Result<boolean, E> {
        // Check if any of the inputs have been updated.
        const input_results = map(this.inputs, input => input.getValue());
        let needs_hydration = false;
        const input_values: any[] = []

        for (let i = 0; i < input_results.length; i++) {
            const result = input_results[i]!;
            
            if (!result.ok) {
                return Err(result.error);
            } else {
                const [value, hydrated] = result.value;
                needs_hydration = needs_hydration || hydrated;
                input_values.push(value);
            }
        }

        if (!needs_hydration) {
            return Ok(false);
        }

        // inputs is now a valid array of type Inputs.
        const inputs: Inputs = <Inputs> input_values;

        // Convert the inputs into outputs.
        const output_results = this.convert(inputs);
        if (!output_results.ok) {
            return Err(output_results.error);
        }

        // Set output value of links.
        for (let i = 0; i < output_results.value.length; i++) {
            const result = output_results.value[i];
            this.outputs[i]!.setValue(result); 
        }

        return Ok(true);
    }
};


// Convenience source node for a single value.
export class SourceNode<T, E> extends Node<[], [T], E> {
    protected convert(_inputs: []): Result<[T], E> {
        return Ok([this.value]);
    }

    private value: T;

    constructor(value: T) {
        super(0, 1);
        this.value = value;
    }

    public setValue(value: T): void {
        this.value = value;
        this.getOutputs()[0].setValue(value);
    }
};


// Convenience sink node for a single value.
export class SinkNode<T, E> extends Node<[T], [], E> {
    protected convert(inputs: [T]): Result<[], E> {
        this.value = inputs[0];
        return Ok([]);
    }

    private value: T;

    constructor() {
        super(1, 0);
    }

    public getValue(): T {
        return this.value;
    }
};


export class NodeLink<T, E> extends Link<T, E> {};


export class Spigot<T, E> extends NodeLink<T, E> {};


export class Sink<T, E> extends NodeLink<T, E> {};


// Map the array to a new array.
function map<Type, Result>(list: Type[], mapper: (value: Type) => Result): Result[] {
    if (typeof Array.prototype.map === "function") {
        return list.map(mapper);
    }

    const result: Result[] = [];

    for (let i = 0; i < list.length; i++) {
        result.push(mapper(list[i]!));
    }

    return result;
}
