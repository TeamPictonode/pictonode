<!-- GNU AGPL v3 License -->

<script lang="ts">
import { defineComponent } from "vue";
import { Node, SpecialNodeType, MetadataType, NodeDataType } from "./NodeTree";

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

      // Convert it to a canvas.
      const reader = new FileReader();
      reader.readAsDataURL(imageBlob);
      reader.onload = (e) => {
        const img = new Image();
        img.onload = () => {
          // Create a canvas.
          const canvas = document.createElement("canvas");
          canvas.width = img.width;
          canvas.height = img.height;

          // Draw the image on the canvas.
          const ctx = canvas.getContext("2d");
          if (!ctx) {
            throw new Error("Could not get canvas context");
          }

          ctx.drawImage(img, 0, 0);

          this.node.getOutputs()[0].set({
            type: NodeDataType.Image,
            canvas,
          });
          this.$emit("input-update");
        };

        // @ts-ignore
        img.src = e.target!.result;
      };
    },

    onColorInputUpdate(color: string) {
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
    @input="onColorInputUpdate"
  ></v-color-picker>
</template>
