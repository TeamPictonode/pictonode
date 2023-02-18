// AGPL v3 License

// This file in its entirety was written by John Nunley.

// More nodes than we'll probably ever use (about 16 million).
const MAX_NODES: number = 1 << 24;

// A table made up of node templates.
export class TemplateTable<T, M> {
  private readonly table: Map<string, NodeTemplate<T, M>>;

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
  public getTemplates(): string[] {
    return Array.from(this.table.keys());
  }
}

// Template for creating a node.
export class NodeTemplate<T, M> {
  // Callback for when the node's data is processed.
  private readonly onProcess: (data: Array<Link<T, M>>) => T[];

  // Inputs for this node.
  private readonly inputs: Array<LinkTemplate<T, M>>;

  // Outputs for this node.
  private readonly outputs: Array<LinkTemplate<T, M>>;

  // Metadata
  private readonly metadata: M;

  public constructor(
    // Callback for when the node's data is processed.
    onProcess: (data: Array<Link<T, M>>) => T[],
    // Default inputs for this node.
    inputs: Array<LinkTemplate<T, M>>,
    // Default outputs for this node.
    outputs: Array<LinkTemplate<T, M>>,
    // Metadata
    metadata: M
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
  __process(data: Array<Link<T, M>>): T[] {
    return this.onProcess(data);
  }
}

// Template for creating a link.
export class LinkTemplate<T, M> {
  private readonly metadata: M;
  private readonly defaultValue: T;

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
}

// A node in the graph.
export class Node<T, M> implements HydrateTarget {
  // The template table this node uses.
  private readonly templateTable: TemplateTable<T, M>;

  // The template this node uses.
  private readonly template: string;

  // The metadata for this node.
  private metadata: M;

  // The links coming into this node.
  private inputs: Array<Link<T, M>>;

  // The links coming out of this node.
  private outputs: Array<Link<T, M>>;

  // The ID of this node.
  private id: number;

  public constructor(
    // The template this node uses.
    templateTable: TemplateTable<T, M>,
    template: string,
    // The metadata for this node.
    metadata: M,
    // The ID of this node.
    id: number
  ) {
    this.templateTable = templateTable;
    this.template = template;
    this.metadata = metadata;
    this.id = id;

    const realTemplate = templateTable.getTemplate(template);
    let lastLinkId = id + MAX_NODES;

    this.inputs = map(realTemplate.getInputs(), (inputTemplate, index) => {
      const link = new Link(
        inputTemplate,
        inputTemplate.getMetadata(),
        lastLinkId
      );
      link.__setTo(this, index);
      lastLinkId += MAX_NODES;
      return link;
    });

    this.outputs = map(realTemplate.getOutputs(), (outputTemplate, index) => {
      const link = new Link(
        outputTemplate,
        outputTemplate.getMetadata(),
        lastLinkId
      );
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

  __setId(id: number): void {
    this.id = id;
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
      /* eslint-disable @typescript-eslint/no-non-null-assertion */
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

      this.inputs[index] = new Link(
        inputTemplate,
        inputTemplate.getMetadata(),
        id
      );
    } else {
      const outputTemplate = template.getOutputs()[index];

      if (outputTemplate === undefined) {
        throw new Error(`Invalid output index ${index}`);
      }

      this.outputs[index] = new Link(
        outputTemplate,
        outputTemplate.getMetadata(),
        id
      );
    }
  }

  // PRIVATE: As the "to" node, link this node to a "from" node.
  __linkFrom(
    from: Node<T, M>,
    fromIndex: number,
    toIndex: number,
    meta: M
  ): Link<T, M> {
    /* eslint-disable @typescript-eslint/no-non-null-assertion */
    const link = this.inputs[toIndex]!;

    const fromValue = from.outputs[fromIndex]!.get(); 

    from.outputs[fromIndex] = link;
    link.__setFrom(from, fromIndex);
    link.__setTo(this, toIndex);
    link.__setMetadata(meta);
    link.set(fromValue);
    return link;
  }

  // PRIVATE: As the "to" node, remove the link from a "from" node.
  __unlinkFrom(
    from: Node<T, M>,
    fromIndex: number,
    toIndex: number,
    id: number
  ): void {
    from.__replaceLink(fromIndex, false, id);
    this.inputs[toIndex]!.__clearFrom();
    this.inputs[toIndex]!.__clearTo();
  }

  // PRIVATE: Unlink all links coming into this node.
  __unlinkAll(): void {
    /* eslint-disable @typescript-eslint/no-non-null-assertion */
    for (let i = this.inputs.length - 1; i > 0; i--) {
      this.__unlinkFrom(
        this.inputs[i]!.getFrom()!,
        this.inputs[i]!.getFromIndex()!,
        i,
        this.inputs[i]!.getId()
      );
    }

    throw new Error("TODO");
  }

  // Is the input at the given index occupied?
  public isInputOccupied(index: number): boolean {
    /* eslint-disable @typescript-eslint/no-non-null-assertion */
    return this.inputs[index]!.__isFromOccupied();
  }

  // Is the output at the given index occupied?
  public isOutputOccupied(index: number): boolean {
    /* eslint-disable @typescript-eslint/no-non-null-assertion */
    return this.outputs[index]!.__isToOccupied();
  }
}

// A link between two nodes.
export class Link<T, M> {
  private readonly template: LinkTemplate<T, M>;

  private id: number;

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

  __eat(): any {
    return [this.template, this.customDefault];
  }

  public constructor(
    // The link template this link uses.
    template: LinkTemplate<T, M>,
    // Metadata for this link.
    metadata: M,
    // The ID of this link.
    id: number
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

  __setId(id: number): void {
    this.id = id;
  }

  __setMetadata(metadata: M): void {
    this.metadata = metadata;
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

  __serDefaultValue(): T | undefined {
    if (this.customDefault) {
      return this.value;
    } else {
      return undefined;
    }
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
  __hydrate: () => void;
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
  private readonly nodes: Map<number, Node<T, M>>;

  // List of all links in the pipeline.
  private readonly links: Map<number, Link<T, M>>;

  // Table of templates.
  private readonly templateTable: TemplateTable<T, M>;

  // The ID of the next node to be created.
  private nextNodeId: number;

  // The ID of the output node.
  private outputNodeId: number | undefined;

  public constructor(templateTable: TemplateTable<T, M>) {
    this.nodes = new Map();
    this.links = new Map();
    this.templateTable = templateTable;
    this.nextNodeId = 0;
    this.outputNodeId = undefined;
  }

  // Create a new node in the pipeline.
  public createNode(template: string, metadata: M): Node<T, M> {
    const node = new Node(
      this.templateTable,
      template,
      metadata,
      this.nextNodeId
    );
    this.nodes.set(this.nextNodeId, node);
    this.nextNodeId++;
    return node;
  }

  // Link two nodes together at the given index.
  public link(
    fromId: number,
    fromIndex: number,
    toId: number,
    toIndex: number,
    meta: M
  ): Link<T, M> {
    const from = this.nodes.get(fromId);

    if (from === undefined) {
      throw new Error(`Node with ID ${fromId} does not exist.`);
    }

    const to = this.nodes.get(toId);

    if (to === undefined) {
      throw new Error(`Node with ID ${toId} does not exist.`);
    }

    const link = to.__linkFrom(from, fromIndex, toIndex, meta);
    this.links.set(link.getId(), link);
    return link;
  }

  // Unlink two nodes at the given index.
  public unlink(
    fromId: number,
    fromIndex: number,
    toId: number,
    toIndex: number
  ): void {
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

  // Get the output node.
  public getOutput(): Node<T, M> | undefined {
    if (this.outputNodeId === undefined) {
      return undefined;
    }

    return this.nodes.get(this.outputNodeId);
  }

  // Set the ID of the output node.
  public setOutput(id: number): void {
    this.outputNodeId = id;
  }

  __outputId(): number | undefined {
    return this.outputNodeId;
  }
}

// The serialized form of a pipeline.
export interface SerializedPipeline<M> {
  nodes: Array<SerializedNode<M>>;
  links: Array<SerializedLink<M>>;
  output: number | undefined;
}

export interface SerializedNode<M> {
  id: number;
  template: string;
  metadata: M;
}

export type SerializedLink<M> = {
  id: number;
  metadata: M;
  defaultValue: any | undefined;
} & ({ from: number; fromIndex: number } | { from: undefined }) &
  ({ to: number; toIndex: number } | { to: undefined });

// Serialize a pipeline to a JSON object.
export function serializePipeline<T, M>(
  pipeline: Pipeline<T, M>
): SerializedPipeline<M> {
  const nodes: Array<SerializedNode<M>> = reduce(
    pipeline.getNodes(),
    (nodes, node) => {
      nodes.push({
        id: node.getId(),
        template: node.getTemplate(),
        metadata: node.getMetadata(),
      });
      return nodes;
    },
    [] as Array<SerializedNode<M>>
  );

  const links: Array<SerializedLink<M>> = reduce(
    pipeline.getLinks(),
    (links, link) => {
      let linkValue: SerializedLink<M> = {
        id: link.getId(),
        from: undefined,
        to: undefined,
        defaultValue: link.__serDefaultValue(),
        metadata: link.getMetadata(),
      };

      // Set from and to values.
      const fromNode = link.getFrom();
      if (fromNode !== undefined) {
        linkValue = {
          ...linkValue,
          from: fromNode.getId(),
          fromIndex: link.getFromIndex(),
        };
      }

      const toNode = link.getTo();
      if (toNode !== undefined) {
        linkValue = {
          ...linkValue,
          to: toNode.getId(),
          toIndex: link.getToIndex(),
        };
      }

      links.push(linkValue);
      return links;
    },
    [] as Array<SerializedLink<M>>
  );

  return {
    nodes,
    links,
    output: pipeline.__outputId() || -1,
  };
}

// Deserialize a pipeline from a JSON object.
export function deserializePipeline<T, M>(
  serialized: SerializedPipeline<M>,
  templateTable: TemplateTable<T, M>
): Pipeline<T, M> {
  const pipeline = new Pipeline(templateTable);

  forEach(serialized.nodes, (node) => {
    const newNode = pipeline.createNode(node.template, node.metadata);
    newNode.__setId(node.id);
  });

  forEach(serialized.links, (link) => {
    if (link.from === undefined || link.to === undefined) {
      console.log(`Invalid link with id ${link.id}}`);
      return;
    }

    const newLink = pipeline.link(
      link.from,
      link.fromIndex,
      link.to,
      link.toIndex,
      link.metadata
    );
    newLink.__setId(link.id);
    if (link.defaultValue !== undefined) {
      newLink.set(link.defaultValue);
    }
  });

  if (serialized.output !== undefined) {
    pipeline.setOutput(serialized.output);
  }

  return pipeline;
}

// Iterate over every element in an array and run a function on it.
const forEach: <T>(array: T[], fn: (item: T, index: number) => void) => void =
  (() => {
    if (typeof Array.prototype.forEach === "function") {
      return (array, fn) => array.forEach(fn);
    }

    return (array, fn) => {
      let i = 0;
      for (const item of array) {
        fn(item, i);
        i++;
      }
    };
  })();

// Iterate over an array, get each element, map it, and return an array of all values.
const map: <T, U>(array: T[], fn: (item: T, index: number) => U) => U[] =
  (() => {
    if (typeof Array.prototype.map === "function") {
      return (array, fn) => array.map(fn);
    }

    return <T, U>(array: T[], fn: (item: T, index: number) => U) => {
      const result: U[] = [];

      forEach(array, (item, index) => {
        result.push(fn(item, index));
      });

      return result;
    };
  })();

// Reduce the array to a single value.
const reduce: <T, U>(array: T[], fn: (acc: U, item: T) => U, initial: U) => U =
  (() => {
    if (typeof Array.prototype.reduce === "function") {
      return (array, fn, initial) => array.reduce(fn, initial);
    }

    return <T, U>(array: T[], fn: (acc: U, item: T) => U, initial: U) => {
      let acc = initial;

      for (const item of array) {
        acc = fn(acc, item);
      }

      return acc;
    };
  })();

// Are any of the boolean values produced by a closure true?
const any: <T>(array: T[], fn: (item: T) => boolean) => boolean = (() => {
  if (typeof Array.prototype.some === "function") {
    return (array, fn) => array.some(fn);
  }

  return <T>(array: T[], fn: (item: T) => boolean) => {
    return reduce(array, (acc, item) => acc || fn(item), false);
  };
})();
