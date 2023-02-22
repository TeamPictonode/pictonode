// Various node templates and their types.

import { DefineComponent, PropType, defineComponent } from "vue";

import InputNode from "./NodeData/InputNode.vue";

export interface NodeTemplate {
  templateName: string;
  displayName: string;
  category: string;
  tooltip: string;
  inputs: LinkTemplate[];
  outputs: LinkTemplate[];
  innerComponent: DefineComponent<{}, {}, any>;
}

export type NodeTemplatePropsType = {
  node: {
    type: PropType<NodeTemplate>,
    required: boolean,
  }
};
export const NodeTemplateComponentProps: NodeTemplatePropsType = {
  node: {
    type: Object as () => NodeTemplate,
    required: true,
  },
}

export interface LinkTemplate {
  color: string;
  title: string;
  data_type: DataType,
}

export enum DataType {
  Image = "image",
  Color = "color",
}

export type SpecificData = {
  type: SpecificDataType.None
} | {
  type: SpecificDataType.InputImage,
  imageId: number,
};

export enum SpecificDataType {
  None = "none",
  InputImage = "input-image",
}

// List of templates.

const emptyComponent = defineComponent<NodeTemplatePropsType, {}, {}>({
  props: NodeTemplateComponentProps,
  template: `
    <div class="node">
    </div>
  `
});

export const nodeTemplates: Record<string, NodeTemplate> = {
  "input": {
    templateName: "input",
    displayName: "Input",
    category: "Input",
    tooltip: "Try uploading an image to me!",
    inputs: [],
    outputs: [
      {
        color: "red",
        title: "Image",
        data_type: DataType.Image,
      }
    ],
    innerComponent: InputNode,
  },

  "invert": {
    templateName: "invert",
    displayName: "Invert",
    category: "Transforms",
    tooltip: "I invert values of an input image!",
    inputs: [
      {
        color: "red",
        title: "Image",
        data_type: DataType.Image,
      }
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

  "output": {
    templateName: "output",
    displayName: "Output",
    category: "Output",
    tooltip: "I am an output node!",
    inputs: [
      {
        color: "red",
        title: "Image",
        data_type: DataType.Image,
      }
    ],
    outputs: [],
    innerComponent: emptyComponent,
  }
};
