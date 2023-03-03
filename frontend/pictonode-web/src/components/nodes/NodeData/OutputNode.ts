// GNU AGPL v3 License
// Written by John Nunley

import { defineComponent } from "vue";
import { NodeTemplateComponentProps } from "../NodeTypes";
import { SpecificData, SpecificDataType } from "../getPipeline";

export default defineComponent({
  template: `<div></div>`,
  props: NodeTemplateComponentProps,
  emits: {
    updated: (data: SpecificData) => true,
  },
  mounted() {
    this.$emit("updated", {
      type: SpecificDataType.Output,
    });
  },
});
