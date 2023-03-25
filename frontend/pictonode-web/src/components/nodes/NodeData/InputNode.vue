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
  data: () => ({
    imgName: "image"
  }),
  methods: {
    onFileChange(e: any) {
      const file = e.target.files[0];
      this.imgName = file.name;

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
  <label htmlFor='image'>
                    {{ imgName }}
                    <input 
                        type='file' 
                        id='file' 
                        name="file"
                        placeholder="Upload an Image" 
                        required 
                        @change={onFileChange}
                        />
                </label>
</template>
