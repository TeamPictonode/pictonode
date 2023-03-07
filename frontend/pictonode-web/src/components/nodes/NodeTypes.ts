// Various node templates and their types.

import { DefineComponent, PropType, defineComponent } from "vue";
import { SpecificData, SpecificDataType } from "./getPipeline";

import InputNode from "./NodeData/InputNode.vue";
import OutputNode from "./NodeData/OutputNode";

export interface NodeTemplate {
  templateName: string;
  displayName: string;
  category: string;
  tooltip: string;
  inputs: LinkTemplate[];
  outputs: LinkTemplate[];
  innerComponent: DefineComponent<
    any,
    any,
    any,
    any,
    any,
    any,
    any,
    any,
    any,
    any
  >;
}

export type NodeTemplatePropsType = {
  node: {
    type: PropType<NodeTemplate>;
    required: boolean;
  };
};
export const NodeTemplateComponentProps: NodeTemplatePropsType = {
  node: {
    type: Object as () => NodeTemplate,
    required: true,
  },
};

export interface LinkTemplate {
  color: string;
  title: string;
  data_type: DataType;
}

export enum DataType {
  Image = "image",
  Color = "color",
}

// List of templates.

const emptyComponent = defineComponent<NodeTemplatePropsType, {}, {}>({
  props: NodeTemplateComponentProps,
  template: `
    <div class="node">
    </div>
  `,
  emits: {
    updated: (_data: SpecificData) => true,
  },
});

export const nodeTemplates: Record<string, NodeTemplate> = {
  ImgSrc: {
    templateName: "ImgSrc",
    displayName: "Input",
    category: "Input",
    tooltip: "Try uploading an image to me!",
    inputs: [],
    outputs: [
      {
        color: "red",
        title: "Image",
        data_type: DataType.Image,
      },
    ],
    innerComponent: InputNode,
  },

  Invert: {
    templateName: "Invert",
    displayName: "Invert",
    category: "Transforms",
    tooltip: "I invert values of an input image!",
    inputs: [
      {
        color: "red",
        title: "Image",
        data_type: DataType.Image,
      },
    ],
    outputs: [
      {
        color: "red",
        title: "Inverted Image",
        data_type: DataType.Image,
      },
    ],
    innerComponent: emptyComponent,
  },

  CompOver: {
    templateName: "CompOver",
    displayName: "Composite",
    category: "Transforms",
    tooltip: "I composite two images!",
    inputs: [
      {
        color: "red",
        title: "Top Image",
        data_type: DataType.Image,
      },
      {
        color: "green",
        title: "Bottom Image",
        data_type: DataType.Image,
      },
    ],
    outputs: [
      {
        color: "red",
        title: "Composite Image",
        data_type: DataType.Image,
      },
    ],
    innerComponent: emptyComponent,
  },

  ImgOut: {
    templateName: "ImgOut",
    displayName: "Output",
    category: "Output",
    tooltip: "I am an output node!",
    inputs: [
      {
        color: "red",
        title: "Image",
        data_type: DataType.Image,
      },
    ],
    outputs: [],
    innerComponent: OutputNode,
  },
};
