<!-- GNU AGPL v3 License -->
<!-- Written by John Nunley -->

<script lang="ts">
import { defineComponent } from "vue";
import { NodeTemplateComponentProps } from "../NodeTypes";
import { SpecificData, SpecificDataType } from "../getPipeline";
import { uploadImage } from "../../../api";

export default defineComponent({
  props: NodeTemplateComponentProps,
  emits: {
    updated: (data: SpecificData) => true,
  },
  methods: {
    onFileChange(e: any) {
      const file = e.target.files[0];

      uploadImage(file).then((id) => {
        this.$emit("updated", {
          type: SpecificDataType.InputImage,
          imageId: id,
        });
      });
    },
  },
});
</script>

<template>
  <v-file-input @change="onFileChange" />
</template>
