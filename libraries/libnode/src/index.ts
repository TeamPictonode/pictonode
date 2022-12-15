// AGPL v3 License

// This file in its entirety was written by John Nunley.

// More nodes than we'll probably ever use (about 16 million).
const MAX_NODES: number = 1 << 24;

// A table made up of node templates.
export class TemplateTable<T, M> {
  private table: Map<string, NodeTemplate<T, M>>;
  
  public constructor() {
    this.table = new Map();
  }

  public addTemplate(name: string, template: NodeTemplate<T, M>): void {
    this.table.set(name, template);
  }

  public getTemplate(name: string): NodeTemplate<T, M> {
    const template = this.table.get(name);

    if (template === undefined) {
      throw new Error(`Template "${name}" does not exist.`);
    }

    return template;
  }

  // Get a list of every template.
  public getTemplates(): Array<string> {
    return Array.from(this.table.keys());
  }
};

// Template for creating a node.
export class NodeTemplate<T, M> {
  // Callback for when the node's data is processed.
  private onProcess: (data: Array<Link<T, M>>) => Array<T>;

  // Inputs for this node.
  private inputs: Array<LinkTemplate<T, M>>;

  // Outputs for this node.
  private outputs: Array<LinkTemplate<T, M>>;

  // Metadata
  private metadata: M;

  public constructor(
    // Callback for when the node's data is processed.
    onProcess: (data: Array<Link<T, M>>) => Array<T>,
    // Default inputs for this node.
    inputs: Array<LinkTemplate<T, M>>,
    // Default outputs for this node.
    outputs: Array<LinkTemplate<T, M>>,
    // Metadata
    metadata: M,
  ) {
    this.onProcess = onProcess;
    this.inputs = inputs;
    this.outputs = outputs;
    this.metadata = metadata;
  }

  // Get the inputs for this node.
  public getInputs(): Array<LinkTemplate<T, M>> {
    return this.inputs;
  }

  // Get the outputs for this node.
  public getOutputs(): Array<LinkTemplate<T, M>> {
    return this.outputs;
  }

  // Get the metadata for this node.
  public getMetadata(): M {
    return this.metadata;
  }

  // PRIVATE: Process the node's data.
  __process(data: Array<Link<T, M>>): Array<T> {
    return this.onProcess(data);
  }
};

// Template for creating a link.
export class LinkTemplate<T, M> {
  private metadata: M;
  private defaultValue: T;

  public constructor(metadata: M, defaultValue: T) {
    this.metadata = metadata;
    this.defaultValue = defaultValue;
  }

  public getMetadata(): M {
    return this.metadata;
  }

  public getDefaultValue(): T {
    return this.defaultValue;
  }
};

// A node in the graph.
export class Node<T, M> implements HydrateTarget {
  // The template table this node uses.
  private templateTable: TemplateTable<T, M>;

  // The template this node uses.
  private template: string;

  // The metadata for this node.
  private metadata: M;

  // The links coming into this node.
  private inputs: Array<Link<T, M>>;

  // The links coming out of this node.
  private outputs: Array<Link<T, M>>;

  // The ID of this node.
  private readonly id: number;

  public constructor(
    // The template this node uses.
    templateTable: TemplateTable<T, M>,
    template: string,
    // The metadata for this node.
    metadata: M,
    // The ID of this node.
    id: number,
  ) {
    this.templateTable = templateTable;
    this.template = template;
    this.metadata = metadata;
    this.id = id;

    const realTemplate = templateTable.getTemplate(template);
    let lastLinkId = id + MAX_NODES;

    this.inputs = map(realTemplate.getInputs(), (inputTemplate, index) => {
      const link = new Link(inputTemplate, inputTemplate.getMetadata(), lastLinkId);
      link.__setTo(this, index);
      lastLinkId += MAX_NODES;
      return link;
    });

    this.outputs = map(realTemplate.getOutputs(), (outputTemplate, index) => {
      const link = new Link(outputTemplate, outputTemplate.getMetadata(), lastLinkId);
      link.__setFrom(this, index);
      lastLinkId += MAX_NODES;
      return link;
    });
  }

  public getTemplateTable(): TemplateTable<T, M> {
    return this.templateTable;
  }

  public getTemplate(): string {
    return this.template;
  }

  public getId(): number {
    return this.id;
  }

  public getMetadata(): M {
    return this.metadata;
  }

  public setMetadata(metadata: M): void {
    this.metadata = metadata;
  }

  public getInputs(): Array<Link<T, M>> {
    return this.inputs;
  }

  public getOutputs(): Array<Link<T, M>> {
    return this.outputs;
  }

  __hydrate(): void {
    const isDirty = any(this.inputs, (input) => input.isDirty());

    // If this node is dirty, process it.
    if (!isDirty) {
      return;
    }

    // Process the node.
    const template = this.templateTable.getTemplate(this.template);
    const outputs = template.__process(this.inputs);

    // Set the outputs.
    forEach(this.outputs, (output, index) => {
      output.set(outputs[index]!);
    });
  }

  // PRIVATE: Set an output link.
  __setOutputLink(link: Link<T, M>, index: number): void {
    this.outputs[index] = link;
  }

  // PRIVATE: Replace the link at the given index.
  __replaceLink(index: number, input: boolean, id: number): void {
    if (index === -1) {
      return;
    }

    const template = this.templateTable.getTemplate(this.template);

    if (input) {
      const inputTemplate = template.getInputs()[index];

      if (inputTemplate === undefined) {
        throw new Error(`Invalid input index ${index}`);
      }

      this.inputs[index] = new Link(inputTemplate, inputTemplate.getMetadata(), id);
    } else {
      const outputTemplate = template.getOutputs()[index];

      if (outputTemplate === undefined) {
        throw new Error(`Invalid output index ${index}`);
      }

      this.outputs[index] = new Link(outputTemplate, outputTemplate.getMetadata(), id);
    }
  }

  // PRIVATE: As the "to" node, link this node to a "from" node.
  __linkFrom(from: Node<T, M>, fromIndex: number, toIndex: number): Link<T, M> {
    from.outputs[fromIndex] = this.inputs[toIndex]!;
    this.inputs[toIndex]!.__setFrom(from, fromIndex);
    this.inputs[toIndex]!.__setTo(this, toIndex);
    return this.inputs[toIndex]!;
  }

  // PRIVATE: As the "to" node, remove the link from a "from" node.
  __unlinkFrom(from: Node<T, M>, fromIndex: number, toIndex: number, id: number): void {
    from.__replaceLink(fromIndex, false, id);
    this.inputs[toIndex]!.__clearFrom();
    this.inputs[toIndex]!.__clearTo();
  }

  // PRIVATE: Unlink all links coming into this node.
  __unlinkAll(): void {
    for (let i = this.inputs.length - 1; i > 0; i--) {
      this.__unlinkFrom(this.inputs[i]!.getFrom()!, this.inputs[i]!.getFromIndex()!, i, this.inputs[i]!.getId());
    }

    throw new Error("TODO");
  }

  // Is the input at the given index occupied?
  public isInputOccupied(index: number): boolean {
    return this.inputs[index]!.__isFromOccupied();
  }

  // Is the output at the given index occupied?
  public isOutputOccupied(index: number): boolean {
    return this.outputs[index]!.__isToOccupied();
  }
};

// A link between two nodes.
export class Link<T, M> {
  private template: LinkTemplate<T, M>;

  private readonly id: number;

  // The node this link is coming from.
  private from: HydrateTarget;

  // The index of the link in the 'from' node's outputs.
  private fromIndex: number;

  // The node this link is going to.
  private to: HydrateTarget;

  // The index of the link in the 'to' node's inputs.
  private toIndex: number;

  // The metadata for this link.
  private metadata: M;

  // Whether this link needs to be hydrated.
  private dirty: boolean;

  // The current value of this link.
  private value: T;

  // Is this link using a default value not belonging to the template?
  private customDefault: boolean;

  public constructor(
    // The link template this link uses.
    template: LinkTemplate<T, M>,
    // Metadata for this link.
    metadata: M,
    // The ID of this link.
    id: number,
  ) {
    this.template = template;
    this.from = NO_NODE;
    this.fromIndex = -1;
    this.to = NO_NODE;
    this.toIndex = -1;
    this.metadata = metadata;
    this.dirty = true;
    this.value = template.getDefaultValue();
    this.customDefault = false;
    this.id = id;
  }

  public getId(): number {
    return this.id;
  }

  __isFromOccupied(): boolean {
    return !isNoNode(this.from);
  }

  __isToOccupied(): boolean {
    return !isNoNode(this.to);
  }

  // PRIVATE: Set the "from" node of this link.
  __setFrom(from: HydrateTarget, fromIndex: number): void {
    this.from = from;
    this.fromIndex = fromIndex;
  }

  // PRIVATE: Clear the "from" node of this link.
  __clearFrom(): void {
    this.from = NO_NODE;
    this.fromIndex = -1;
  }

  // PRIVATE: Set the "to" node of this link.
  __setTo(to: HydrateTarget, toIndex: number): void {
    this.to = to;
    this.toIndex = toIndex;
  }

  // PRIVATE: Clear the "to" node of this link.
  __clearTo(): void {
    this.to = NO_NODE;
    this.toIndex = -1;
  }

  // Is this link currently dirty?
  public isDirty(): boolean {
    return this.dirty;
  }

  // Hydrate this link.
  public hydrate(): void {
    this.from.__hydrate();
    this.dirty = false;
  }

  // Get the value of this link.
  public get(): T {
    this.hydrate();
    return this.value;
  }

  // Set the value of this link.
  public set(value: T): void {
    this.value = value;
    this.dirty = true;
    this.customDefault = true;
  }

  // Get the 'from' node of this link.
  public getFrom(): Node<T, M> | undefined {
    const from = this.from;

    if (isNoNode(from)) {
      return undefined;
    }

    return from as Node<T, M>;
  }

  /// Get the index of this link in the 'from' node's outputs.
  public getFromIndex(): number {
    return this.fromIndex;
  }

  // Get the 'to' node of this link.
  public getTo(): Node<T, M> | undefined {
    const to = this.to;

    if (isNoNode(to)) {
      return undefined;
    }

    return to as Node<T, M>;
  }

  // Get the index of this link in the 'to' node's inputs.
  public getToIndex(): number {
    return this.toIndex;
  }

  // Get the metadata for this link.
  public getMetadata(): M {
    return this.metadata;
  }
}

interface HydrateTarget {
  // Hydrate this node.
  __hydrate(): void;
}

const NO_NODE: HydrateTarget & { __thisIsNoNode: true } = {
  __thisIsNoNode: true,
  __hydrate: () => {},
};

function isNoNode(node: HydrateTarget): node is typeof NO_NODE {
  return (node as any).__thisIsNoNode === true;
}

// A pipeline consisting of several nodes.
export class Pipeline<T, M> {
  // List of all nodes in the pipeline.
  private nodes: Map<number, Node<T, M>>;

  // List of all links in the pipeline.
  private links: Map<number, Link<T, M>>;

  // Table of templates.
  private templateTable: TemplateTable<T, M>;

  // The ID of the next node to be created.
  private nextNodeId: number;

  public constructor(templateTable: TemplateTable<T, M>) {
    this.nodes = new Map();
    this.links = new Map();
    this.templateTable = templateTable;
    this.nextNodeId = 0;
  }

  // Create a new node in the pipeline.
  public createNode(template: string, metadata: M): Node<T, M> {
    const node = new Node(this.templateTable, template, metadata, this.nextNodeId);
    this.nodes.set(this.nextNodeId, node);
    this.nextNodeId++;
    return node;
  }

  // Link two nodes together at the given index.
  public link(fromId: number, fromIndex: number, toId: number, toIndex: number): void {
    const from = this.nodes.get(fromId);

    if (from === undefined) {
      throw new Error(`Node with ID ${fromId} does not exist.`);
    }

    const to = this.nodes.get(toId);

    if (to === undefined) {
      throw new Error(`Node with ID ${toId} does not exist.`);
    }

    const link = to.__linkFrom(from, fromIndex, toIndex);
    this.links.set(link.getId(), link);
  }

  // Unlink two nodes at the given index.
  public unlink(fromId: number, fromIndex: number, toId: number, toIndex: number): void {
    const from = this.nodes.get(fromId);

    if (from === undefined) {
      throw new Error(`Node with ID ${fromId} does not exist.`);
    }

    const to = this.nodes.get(toId);

    if (to === undefined) {
      throw new Error(`Node with ID ${toId} does not exist.`);
    }

    to.__unlinkFrom(from, fromIndex, toIndex, this.nextNodeId);
    this.nextNodeId++;
  }

  // Get a node by its ID.
  public getNode(id: number): Node<T, M> | undefined {
    return this.nodes.get(id);
  }

  // Get every node.
  public getNodes(): Array<Node<T, M>> {
    return Array.from(this.nodes.values());
  }

  // Get every link.
  public getLinks(): Array<Link<T, M>> {
    return Array.from(this.links.values());
  }

  // Remove a node.
  public removeNode(id: number): void {
    const node = this.nodes.get(id);

    if (node === undefined) {
      throw new Error(`Node with ID ${id} does not exist.`);
    }

    node.__unlinkAll();
    this.nextNodeId++;
    this.nodes.delete(id);
  }
};

// TODO: Serialization/Deserialization

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
const map: <T, U>(array: Array<T>, fn: (item: T, index: number) => U) => Array<U> = (() => {
  if (typeof Array.prototype.map === "function") {
    return (array, fn) => array.map(fn);
  }

  return <T, U>(array: Array<T>, fn: (item: T, index: number) => U) => {
    const result: Array<U> = [];

    forEach(array, (item, index) => {
      result.push(fn(item, index));
    });

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
