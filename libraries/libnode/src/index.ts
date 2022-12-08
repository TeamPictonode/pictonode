// AGPL v3 License

export type ComputeFunction<T, M> = (inputs: Array<Link<T, M>>) => Array<T>;

export class ComputeFunctionTable<T, M> {
  private table: Map<string, ComputeFunction<T, M>>;

  public constructor() {
    this.table = new Map();
  }

  // Add a compute function to the table
  public add(name: string, computeFunction: ComputeFunction<T, M>) {
    this.table.set(name, computeFunction);
  }

  // Get a compute function from the table
  public get(name: string): ComputeFunction<T, M> {
    const func = this.table.get(name);

    if (func === undefined) {
      throw new Error(`Compute function ${name} does not exist`);
    }

    return func;
  } 
}

let ID = 0;

export class Node<T, M> implements HydrateTarget {
  // Unique ID for this node.
  private readonly id = ID++;

  // The input links to this node. We hydrate from these links.
  private readonly inputLinks: Array<Link<T, M>>;

  // Reference to the original input links.
  private readonly originalInputLinks: Array<Link<T, M>>;

  // The output links from this node. We hydrate to these links.
  private readonly outputLinks: Array<Link<T, M>>;

  // Reference to the original output links.
  private readonly originalOutputLinks: Array<Link<T, M>>;

  // The compute function table for this node.
  private readonly compute_table: ComputeFunctionTable<T, M>;

  // The name of the compute function we use.
  private readonly compute_name: string;

  // Metadata for this node.
  private readonly metadata: M;

  public constructor(
    inputLinks: Array<Link<T, M>>,
    outputLinks: Array<Link<T, M>>,
    compute_table: ComputeFunctionTable<T, M>,
    compute_name: string,
    metadata: M
  ) {
    if (inputLinks.length !== outputLinks.length) {
      throw new Error(
        `Input and output link counts do not match: ${inputLinks.length} !== ${outputLinks.length}`
      );
    }

    this.inputLinks = inputLinks;
    this.originalInputLinks = inputLinks;
    this.outputLinks = outputLinks;
    this.originalOutputLinks = outputLinks;
    this.compute_table = compute_table;
    this.compute_name = compute_name;
    this.metadata = metadata;

    forEach(this.inputLinks, (link, i) => {
      link.__setToNode(this, i);
    });

    forEach(this.outputLinks, (link, i) => {
      link.__setFromNode(this, i);
    });
  }

  // Get an array of the input links to this node.
  public getInputs(): Array<Link<T, M>> {
    return this.inputLinks;
  }

  // Get an array of the output links from this node.
  public getOutputs(): Array<Link<T, M>> {
    return this.outputLinks;
  }

  public getComputeName(): string {
    return this.compute_name;
  }

  __hydrate(): void {
    // Are any of the links dirty?
    const dirty = any(this.inputLinks, (link) => link.isDirty());

    if (!dirty) {
      // We are not dirty, so we don't need to recompute.
      return;
    }

    // Compute the outputs.
    const compute_func = this.compute_table.get(this.compute_name);
    const outputs = compute_func(this.inputLinks);

    // Set the outputs.
    forEach(this.outputLinks, (link, index) => {
      link.set(outputs[index]!);
    });
  }

  // Get the metadata for this node.
  public getMetadata(): M {
    return this.metadata;
  }

  // Get the ID for this node.
  public getID(): number {
    return this.id;
  }

  __setInputLink(index: number, link: Link<T, M>): void {
    this.inputLinks[index] = link;
  }

  __setOutputLink(index: number, link: Link<T, M>): void {
    this.outputLinks[index] = link;
  }

  __restoreInputLink(index: number): void {
    this.inputLinks[index] = this.originalInputLinks[index]!;
  }
}

export class Link<T, M> {
  // A unique ID for this link.
  private readonly id = ID++;

  // The value of the link.
  private value: T;

  // Metadata about the link.
  private metadata: M;

  // The node that this link hydrates from.
  private fromNode: HydrateTarget;

  // The index of this link in the output array of the from node.
  private outputIndex: number;

  // The node that this link hydrates to.
  private toNode: HydrateTarget;

  // The index of this link in the input array of the to node.
  private inputIndex: number;

  // A string describing the type of the link.
  private type: string;

  // Has our value been changed since the last hydration?
  private dirty: boolean;

  public constructor(defaultValue: T, metadata: M, type: string) {
    this.value = defaultValue;
    this.metadata = metadata;
    this.type = type;
    this.dirty = true;
    this.fromNode = NO_NODE;
    this.toNode = NO_NODE;
    this.inputIndex = -1;
    this.outputIndex = -1;
  }

  __setFromNode(node: HydrateTarget, index: number) {
    this.fromNode = node;
    this.outputIndex = index;
  }

  __setToNode(node: HydrateTarget, index: number) {
    this.toNode = node;
    this.inputIndex = index;
  }

  __inputIndex(): number {
    return this.inputIndex;
  }

  __outputIndex(): number {
    return this.outputIndex;
  }

  // Hydrate and set the value of this link.
  private __hydrate() {
    this.fromNode.__hydrate();
    this.dirty = false;
  }

  // Get the value of this link.
  public get(): T {
    this.__hydrate();
    return this.value;
  }

  // Set the value of this link.
  public set(value: T) {
    this.value = value;
    this.dirty = true;
  }

  // Get the metadata of this link.
  public getMetadata(): M {
    return this.metadata;
  }

  // Is this link dirty?
  public isDirty(): boolean {
    return this.dirty;
  }

  // Get the type of this link.
  public getType(): string {
    return this.type;
  }

  // Do we have a node that this link hydrates from?
  public hasFromNode(): boolean {
    return this.fromNode !== NO_NODE;
  }

  // Do we have a node that this link hydrates to?
  public hasToNode(): boolean {
    return this.toNode !== NO_NODE;
  }

  // Get the node that this link hydrates from.
  public getFromNode(): Node<T, M> {
    const node = this.fromNode;

    if (node === NO_NODE) {
      throw new Error("Link has no from node");
    }

    return node as Node<T, M>;
  }

  // Get the node that this link hydrates to.
  public getToNode(): Node<T, M> {
    const node = this.toNode;

    if (node === NO_NODE) {
      throw new Error("Link has no to node");
    }

    return node as Node<T, M>;
  }

  // Get the ID for this link.
  public getID(): number {
    return this.id;
  }
}

export class Pipeline<T, M> {
  // Every node in the pipeline.
  private allNodes: Array<Node<T, M>>;

  // Every link in the pipeline.
  private allLinks: Array<Link<T, M>>;

  // Metadata for this pipeline.
  private metadata: M;

  // The output links that we care about.
  private outputLinks: Array<Link<T, M>>;

  public constructor(metadata: M) {
    this.allLinks = [];
    this.allNodes = [];
    this.metadata = metadata;
  }

  // Get every node in the pipeline.
  public getNodes(): Array<Node<T, M>> {
    return this.allNodes;
  }

  // Get every link in the pipeline.
  public getLinks(): Array<Link<T, M>> {
    return this.allLinks;
  }

  // Add a node to this pipeline.
  public addNode(node: Node<T, M>) {
    this.allNodes.push(node);
    this.allLinks.push(...node.getInputs());
    this.allLinks.push(...node.getOutputs());
  }

  // Connect one node to another.
  public connectNodes(
    fromNode: Node<T, M>,
    fromIndex: number,
    toNode: Node<T, M>,
    toIndex: number
  ) {
    const outputLink = fromNode.getOutputs()[fromIndex]!;
    outputLink.__setToNode(toNode, toIndex);
    toNode.__setOutputLink(toIndex, outputLink);
  }

  // Disconnect one node from another.
  public disconnectNodes(
    fromNode: Node<T, M>,
    fromIndex: number,
    toNode: Node<T, M>,
    toIndex: number
  ) {
    const outputLink = fromNode.getOutputs()[fromIndex]!;
    outputLink.__setToNode(NO_NODE, -1);
    toNode.__restoreInputLink(toIndex);
  }

  // Delete a node from this pipeline.
  public deleteNode(node: Node<T, M>) {
    const linkIds: number[] = [];

    forEach(node.getInputs(), (link, i) => {
      if (link.hasFromNode()) {
        this.disconnectNodes(link.getFromNode(), link.__outputIndex(), node, i);
      }

      linkIds.push(link.getID());
    });

    forEach(node.getOutputs(), (link, i) => {
      if (link.hasToNode()) {
        this.disconnectNodes(node, i, link.getToNode(), link.__inputIndex());
      }

      linkIds.push(link.getID());
    });

    this.allNodes = filter(this.allNodes, (n) => n.getID() !== node.getID());
    this.allLinks = filter(
      this.allLinks,
      (l) => linkIds.indexOf(l.getID()) === -1
    );
  }

  // Serialize this pipeline into a JSON form.
  // 
  // Assumes that `M` is already a valid JSON object.
  public serialize(): PipelineJSON<T, M> {
    const nodes: NodeJSON<T, M>[] = map(this.allNodes, (node) => ({
      id: node.getID(),
      metadata: node.getMetadata(),
      compute_name: node.getComputeName(),
    }));

    const links: LinkJSON<T, M>[] = map(this.allLinks, (link) => ({
      id: link.getID(),
      type: link.getType(),
      metadata: link.getMetadata(),
      fromNode: link.hasFromNode() ? link.getFromNode().getID() : undefined,
      toNode: link.hasToNode() ? link.getToNode().getID() : undefined,
      fromIndex: link.hasFromNode() ? link.__outputIndex() : -1,
      toIndex: link.hasToNode() ? link.__inputIndex() : -1,
    }));

    return {
      nodes,
      links,
      metadata: this.metadata,
    };
  }

  // Get the current outputs for this workflow.
  public getOutputs(): Array<T> {
    return map(this.outputLinks, (link) => link.get());
  }

  // Set the output links for this pipeline.
  public setOutputs(outputLinks: Array<Link<T, M>>) {
    this.outputLinks = outputLinks;
  }

  // Get the metadata for this pipeline.
  public getMetadata(): M {
    return this.metadata;
  }
}

// Deserialize a pipeline from JSON.
// 
// Assumes that M is a JSON object.
export function deserializePipeline<T, M>(
    json: PipelineJSON<T, M>,
    compute: ComputeFunctionTable<T, M>
): Pipeline<T, M> {
    throw new Error("todo");
}

export interface PipelineJSON<T, M> {
  nodes: Array<NodeJSON<T, M>>;
  links: Array<LinkJSON<T, M>>;
  metadata: M;
}

export interface NodeJSON<T, M> {
  id: number;
  metadata: M;
  compute_name: string;
}

export interface LinkJSON<T, M> {
  id: number;
  type: string;
  metadata: M;
  fromNode: number | undefined;
  fromIndex: number;
  toNode: number | undefined;
  toIndex: number;
}

export interface OriginalLinkJSON<T, M> {
  id: number;
  type: string;
  metadata: M;
  default_value: T;
};

interface HydrateTarget {
  // Hydrate this node.
  __hydrate(): void;
}

const NO_NODE: HydrateTarget = {
  __hydrate: () => {},
};

// Iterate over every element in an array and run a function on it.
const forEach: <T>(
  array: Array<T>,
  fn: (item: T, index: number) => void
) => void = (() => {
  if (typeof Array.prototype.forEach === "function") {
    return (array, fn) => array.forEach(fn);
  }

  return (array, fn) => {
    for (let i = 0; i < array.length; i++) {
      fn(array[i]!, i);
    }
  };
})();

// Iterate over an array, get each element, map it, and return an array of all values.
const map: <T, U>(array: Array<T>, fn: (item: T) => U) => Array<U> = (() => {
  if (typeof Array.prototype.map === "function") {
    return (array, fn) => array.map(fn);
  }

  return <T, U>(array: Array<T>, fn: (item: T) => U) => {
    const result: Array<U> = [];

    for (const item of array) {
      result.push(fn(item));
    }

    return result;
  };
})();

// Reduce the array to a single value.
const reduce: <T, U>(
  array: Array<T>,
  fn: (acc: U, item: T) => U,
  initial: U
) => U = (() => {
  if (typeof Array.prototype.reduce === "function") {
    return (array, fn, initial) => array.reduce(fn, initial);
  }

  return <T, U>(array: Array<T>, fn: (acc: U, item: T) => U, initial: U) => {
    let acc = initial;

    for (const item of array) {
      acc = fn(acc, item);
    }

    return acc;
  };
})();

// Are any of the boolean values produced by a closure true?
const any: <T>(array: Array<T>, fn: (item: T) => boolean) => boolean = (() => {
  if (typeof Array.prototype.some === "function") {
    return (array, fn) => array.some(fn);
  }

  return <T>(array: Array<T>, fn: (item: T) => boolean) => {
    return reduce(array, (acc, item) => acc || fn(item), false);
  };
})();

// Filter a list of items.
const filter: <T>(array: Array<T>, fn: (item: T) => boolean) => Array<T> =
  (() => {
    if (typeof Array.prototype.filter === "function") {
      return (array, fn) => array.filter(fn);
    }

    return <T>(array: Array<T>, fn: (item: T) => boolean) => {
      const result: Array<T> = [];

      for (const item of array) {
        if (fn(item)) {
          result.push(item);
        }
      }

      return result;
    };
  })();
