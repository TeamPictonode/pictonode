<!-- GNU AGPL v3 License -->

<!--
  This file in its entirety was written by John Nunley and Grace Meredith.
-->

<script lang="ts">
import { defineComponent } from "vue";
import { Node, SpecialNodeType, MetadataType, NodeDataType } from "./NodeTree";
import { uploadImage } from "../../api";

export default defineComponent({
  props: {
    node: {
      type: Object as () => Node,
      required: true,
    },
  },
  data: () => ({
    SpecialNodeType,
  }),
  emits: ["input-update"],
  methods: {
    onImageInputUpdate() {
      console.log("Input updated");

      // Get the image blob.
      // @ts-ignore
      const imageBlob = this.$refs.imageInput.files[0];

      // Upload to the server.
      uploadImage(imageBlob).then((id) => {
        console.log(`id: ${id}`);
        this.node.getOutputs()[0].set({
          type: NodeDataType.Image,
          id,
        });
      });
    },

    onColorInputUpdate(color: string) {
      console.log(`Color input updated: ${color}`);
      this.node.getOutputs()[0].set({
        type: NodeDataType.Color,

        // @ts-ignore
        color,
      });
      this.$emit("input-update");
    },
  },
  computed: {
    specialType(): SpecialNodeType {
      const metadata = this.node
        .getTemplateTable()
        .getTemplate(this.node.getTemplate())
        .getMetadata();

      if (metadata.metatype !== MetadataType.NodeTemplate) {
        throw new Error("Node metadata is not of type NodeTemplate");
      }

      return metadata.special;
    },
  },
});
</script>

<template>
  <v-file-input
    v-if="specialType === SpecialNodeType.ImageInput"
    ref="imageInput"
    @change="onImageInputUpdate"
  />
  <v-color-picker
    v-if="specialType === SpecialNodeType.ColorInput"
    dot-size="25"
    swatches-max-height="200"
    value="#FF0000"
    @input="onColorInputUpdate"
  ></v-color-picker>
</template>
