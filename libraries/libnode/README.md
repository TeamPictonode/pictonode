# libnode

`libnode` (not to be confused with Node.js, the Javascript runtime) is a library for modeling composable, node-based pipelines. It is written in pure TypeScript, allowing it to be portable to any JavaScript environment (e.g. browser or Node.js).

## Concepts

Certain processes and operations can be expressed as a pipeline that operates on data. In most cases, this pipeline can be divided into "steps" that each operate on the data in some way. For instance, a pipeline to make a cake would first mix the ingredients into the bowl, and then pass the result of that step (the mixed ingredients) to the oven, which would then process those ingredients into a cake by baking them. 

Sometimes, a step takes multiple inputs, and each of those inputs are processed as a concurrent sub-pipeline. In our cake making metaphor, this would likely involve making frosting for the cake, and then applying the frosting to the cake in a step that takes both the cake and the frosting as inputs. Making the frosting itself is also its own sub-pipeline. Likewise, a step can have multiple outputs; maybe you use the same dough you use to make the cake to also make a set of cupcakes.

These kinds of pipelines can be modeled as a graph. Each step is a node, and nodes are connected by links. The "cook in oven" step in our pipeline above would have a "dough" input link connected to the output link of a "mix ingredients" node, and a "cake" output link connected to the input link of a "apply frosting" node. Like a graph, a pipeline can be rearranged freely, and new nodes can be added or removed. This allows for a wide variety of transformations to be applied to the data, preventing calcification of the pipeline into a single, inflexible process.

Each node can be thought of as a function of its inputs and outputs; however, for any well-defined process there are limits as to the possible operations that the node can perform. You don't want a "print your credit card information" node in your cake baking pipeline after all. Therefore, any pipeline is associated with a set of *node templates*. Each node template has an associated function and predefined set of input and output link templates. Each link template has a "default value" that is used when the link is not connected to another node. The templates are further organized into a table where each template is associated with a unique name.

A node is instantiated from a template by providing a template table and the name of the desired template. Each node has an array of associated input and output links, which are originally borrowed from the template's input/output link templates. To connect one node to another node, the output link on the "from" node is replaced by the "to" link on the input node.

By connecting nodes and links like this, a *pipeline* is formed. The pipeline is the total collection of the nodes and links.

Usually, output is derived from the pipeline by specifying a single "output" link and then fetching the value of that link. By retrieving this value, a process called "hydration" is started. The link has its nodes check its input links to see if any of their values have changed (as well as any of its *parent* values). If any of the values have changed, the node is re-run, and the output link is updated with the new value. This process continues recursively until all nodes have been re-run and all output links have been updated. This process is called "hydration" because it is similar to how a plant absorbs water from the soil.

This is the basic function of `libnode`: a set of nodes that can recursively provide eachother with values in a way that calculates the final result.

## Serialization Format

A pipeline CAN serialize to and be deserialized from a JSON object. The root of the JSON object MUST contain the `output`, `nodes` and `links` fields. These fields MUST contain an array of node and link objects, respectively. 

The node object is a two-field object. The `template` field MUST be a string that is the name of the node template. The `id` field is a unique numerical identifier for the node. The `id` field MUST be unique within the pipeline.

The link object consists of its own unique `id` field. It also contains a `from` and `to` field, representing the nodes it goes from and to, respectively. These fields are numerical identifiers equivalent to the `id` fields of the nodes. There is also a `fromIndex` and `toIndex` field representing the index of the link in the `outputs` and `inputs` arrays of the nodes, respectively. These fields are used to determine which link is connected to which link.

The `output` field is an integer that contains the `id` of the node that is the output of the pipeline.

The template table is kept out of band, meaning that the pipeline itself does not contain the template table. This means that the serializer and deserialize must agree on the template table. 
