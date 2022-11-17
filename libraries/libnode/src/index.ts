// No Implied Warranty

/*
This library aims to model the logical behavior of a node tree and the output it is able
to produce. It is programmed in pure TypeScript with no dependencies. In addition to
underpinning the basics for a node tree, I'm also writing it with the intent to act as an
explanation for TypeScript.

The general model for this library is as follows:

- A node is a function that takes in a set of inputs and produces a set of outputs.
- Nodes have input and outputs, which are represented through "links". Links hold a single
  value and transmit it down the node tree. Their design is inspired by channels; those
  unfamiliar with channels should see this resource: https://gobyexample.com/channels
- When a new value is placed into a link, the link marks itself as "updated".
- The real process starts when the value of a link (most often, the leaf node's output link)
  is requested. At this point, the output link has a node associated with it. The link
  begins a process called "hydration". The link's node examines each of its linked inputs
  and sees if any of them are updated. If none of them are updated, the node can be assured
  that the output value is the intended result of all of the inputs. If at least one is
  updated, or if running a hydration on the input link updates it, then the node should
  update its output links accordingly.
- The initial node calls hydration on the input links, which calls hydration on their
  inputs, and so on and so forth, thus propagated to every node up the tree. This system
  also ensures that no unnecessary calculations are run, since the function is only
  called when inputs change. Recursion!
*/

import { Unit, Result, Ok, Err, Option, Some, None } from "pictotypes";

/**
 *  Interface for a type-erased node.
 *
 *  Interfaces are wrappers over types that can provide a set of fields or functions.
 *  In this case, we only use functions. In order to satisfy the interface, Node and
 *  EmptyNode must both have these functions, so we proceed to define them below.
 */
interface NodeBase<E> {
  // Hydrate this node.
  //
  // Returns "true" if the node was changed during hydration.
  hydrate: (force: boolean) => Result<boolean, E>;
}

/**
 * An empty placeholder node.
 *
 * Links without associated nodes must have something to hydrate off of. This is instead
 * used to indicate that the link's value will not change after the first time it is
 * hydrated.
 */
class EmptyNode<E> implements NodeBase<E> {
  private firstTime: boolean = true;

  hydrate(force: boolean): Result<boolean, E> {
    if (force || this.firstTime) {
      this.firstTime = false;
      return Ok(true);
    } else {
      return Ok(force);
    }
  }
}

/**
 * A link from one node to another.
 *
 * Essentially a channel with only one item.
 */
export class Link<T, E> {
  // The inner value, if it exists.
  protected value: Option<T>;

  // The node that the input side of this link is connected to.
  private readonly input: NodeBase<E>;

  // Whether this link has been updated since the last hydration.
  private updated: boolean;

  // A callback to run before setting `value`.
  private callback: (value: T) => Result<T, E>;

  constructor(nb: NodeBase<E>) {
    this.value = None();
    this.input = nb;
    this.updated = false;
    this.callback = (value: T) => Ok(value);
  }

  // Store a value in this link.
  public setValue(value: T): Result<Unit, E> {
    return this.callback(value).map(value => {
      this.value = Some(value);
      this.updated = true;
      return ({});
    });
  }

  // Whether this link is in need of hydration.
  public needsHydration(): boolean {
    return this.updated;
  }

  // Hydrate this link.
  private hydrate(): Result<boolean, E> {
    // Hydrate the input node.
    //
    // setValue() will be called as a result of hydration.
    return this.input.hydrate(false).map((changed) => changed || this.updated);
  }

  // Get the value stored in this link.
  //
  // Returns true if the value was hydrated.
  public getValue(): Result<[T, boolean], E> {
    // Hydrate ourselves first if necessary.
    //
    // After a hydration, the value will be set.
    return this.hydrate().map((hydrated) => [this.value.unwrap(), hydrated]);
  }

  // Set the callback associated with this link.
  public setCallback(callback: (value: T) => Result<T, E>) {
    this.callback = callback;
  }
}

/**
 * The default link type. Simply gives a single value out.
 */
export class DefaultLink<T, E> extends Link<T, E> {
  public constructor(value: T) {
    super(new EmptyNode());
    this.setValue(value).unwrap();
  }
}

/**
 * A list of links with specific values.
 *
 * This type is marginally complicated, but the general essence is as follows:
 *
 * - If the user passes in the tuple [a, b, c], the result type is
 *   [Link<a>, Link<b>, Link<c>]
 * - If the user passes in an a[], the result type is Link<a>[].
 *
 * Basically, it just maps the tuple or array to its link equivalents. Saying
 * "extends [...any[]]" lets us use both tuples and arrays as the generic input while
 * also maintaining our typing.
 */
type InputSpigots<List extends [...any[]], E> = {
  [Key in keyof List]: Link<List[Key], E>;
} & { length: List["length"] };

/**
 * Same as above, but for the output.
 *
 * TODO: This may be able to be the same type.
 */
type OutputSinks<List extends [...any[]], E> = {
  [Key in keyof List]: Link<List[Key], E>;
} & { length: List["length"] };

/**
 * A node that can be used to create a graph.
 */
export abstract class Node<
  Inputs extends [...any[]],
  Outputs extends [...any[]],
  E
> implements NodeBase<E>
{
  // The input spigots we receive value from.
  private inputs: InputSpigots<Inputs, E>;

  // The output sinks we send values to.
  private readonly outputs: OutputSinks<Outputs, E>;

  // Convert the set of inputs into the set of outputs.
  //
  // This abstract function is meant to be implemented by subclasses of Node.
  protected abstract convert(inputs: Inputs): Result<Outputs, E>;

  protected constructor(
    numInputs: number,
    numOutputs: number,
    defaults: Inputs
  ) {
    const inputs: any[] = [];
    const outputs: any[] = [];

    for (let i = 0; i < numInputs; i++) {
      inputs.push(new DefaultLink(defaults[i]));
    }

    for (let i = 0; i < numOutputs; i++) {
      outputs.push(new Link(this));
    }

    this.inputs = inputs as InputSpigots<Inputs, E>;
    this.outputs = outputs as OutputSinks<Outputs, E>;
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
  public setInput<T extends keyof Inputs>(index: T, value: Inputs[T]): Result<Unit, E> {
    return this.inputs[index]!.setValue(value);
  }

  // Get the output value at the given index.
  public getOutput(index: number): Result<Outputs[number], E> {
    return this.outputs[index]!.getValue().map((value) => value[0]);
  }

  // Link the output of the node at the given index to the input of the node at the
  // given index.
  public link<
    ThisInputKey extends keyof Inputs,
    OtherOutputKey extends keyof OtherOutputs,
    OtherInputs extends [...any[]],
    OtherOutputs extends {
      [Key in OtherOutputKey]: Inputs[ThisInputKey];
    } & [...any[]]
  >(
    thisInputKey: ThisInputKey,
    otherOutputKey: OtherOutputKey,
    otherNode: Node<OtherInputs, OtherOutputs, E>
  ): Result<Unit, E> {
    const otherLink: Link<any, E> = otherNode.getOutputs()[otherOutputKey];
    // TODO: Type this better.
    // @ts-expect-error
    this.inputs[thisInputKey] = otherLink;

    // Hydrate ourselves using our new node.
    return this.hydrate(true).map((_) => ({}));
  }

  // Hydrate this node, checking the inputs for updated and propagating them
  // to the outputs.
  hydrate(force: boolean): Result<boolean, E> {
    // Check if any of the inputs have been updated.
    const inputResults = map(this.inputs, (input) => input.getValue());
    let needsHydration = false;
    const inputValues: any[] = [];

    for (let i = 0; i < inputResults.length; i++) {
      const result = inputResults[i]!;

      let error: E | undefined;
      const errored = result.match(
        ([value, hydrated]) => {
          needsHydration = needsHydration || hydrated;
          inputValues.push(value);
          return false;
        },
        (err) => {
          error = err;
          return true;
        }
      );

      if (errored) {
        return Err(error!);
      }
    }

    if (!needsHydration && !force) {
      return Ok(false);
    }

    // inputs is now a valid array of type Inputs.
    const inputs: Inputs = inputValues as Inputs;

    // Convert the inputs into outputs.
    const outputResults = this.convert(inputs);
    if (!outputResults.isOk()) {
      return Err(outputResults.getErr()!);
    }

    // Set output value of links.
    const outResults = outputResults.get()!;
    for (let i = 0; i < outResults.length; i++) {
      const result = outResults[i];
      this.outputs[i]!.setValue(result);
    }

    return Ok(true);
  }
}

// Convenience source node for a single value.
export class SourceNode<T, E> extends Node<[T], [T], E> {
  protected convert(inputs: [T]): Result<[T], E> {
    return Ok(inputs);
  }

  constructor(value: T) {
    super(1, 1, [value]);
  }

  public setValue(value: T): void {
    this.getInputs()[0].setValue(value);
  }
}

// Convenience sink node for a single value.
export class SinkNode<T, E> extends Node<[T], [T], E> {
  protected convert(inputs: [T]): Result<[T], E> {
    return Ok(inputs);
  }

  constructor(defaultValue: T) {
    super(1, 1, [defaultValue]);
  }

  public getValue(): Result<T, E> {
    return this.getOutput(0);
  }
}

// Convenience node that re-transmits its values.
export class IdentityNode<T extends [...any[]], E> extends Node<T, T, E> {
  protected convert(inputs: T): Result<T, E> {
    return Ok(inputs);
  }

  public constructor(numValues: number, defaults: T) {
    super(numValues, numValues, defaults);
  }
}

// Convenience class that just runs a callback when it is hydrated.
export class CallbackNode<
  Inputs extends [...any[]],
  Outputs extends [...any[]],
  E
> extends Node<Inputs, Outputs, E> {
  private readonly callback: (inputs: Inputs) => Result<Outputs, E>;

  protected convert(inputs: Inputs): Result<Outputs, E> {
    return this.callback(inputs);
  }

  public constructor(
    numInputs: number,
    numOutputs: number,
    defaults: Inputs,
    callback: (inputs: Inputs) => Result<Outputs, E>
  ) {
    super(numInputs, numOutputs, defaults);
    this.callback = callback;
  }
}

// Map the array to a new array.
function map<Type, Result>(
  list: Type[],
  mapper: (value: Type) => Result
): Result[] {
  // Some JS environments provide an optimized version of map.
  if (typeof Array.prototype.map === "function") {
    return list.map(mapper);
  }

  // Otherwise, we have to do it ourselves.
  const result: Result[] = [];

  for (const value of list) {
    result.push(mapper(value));
  }

  return result;
}
