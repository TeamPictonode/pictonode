<!-- GNU AGPL v3 License -->
<!-- Written by John Nunley -->

<script lang="ts">
import { defineComponent } from "vue";
import { NodeTemplateComponentProps } from "../NodeTypes";
import { SpecificData, SpecificDataType } from "../getPipeline";
import { uploadImage } from "../../../api";

import { srcImgIds } from "../BaklavaNodes"

export default defineComponent({
  props: NodeTemplateComponentProps,
  emits: {
    updated: (data: SpecificData) => true,
  },
  data: () => ({
    imgName: "image",
  }),
  methods: {
   async onFileChange(e: any) {
      console.log("made it to on file change")
      const file = e.target.files[0];
      this.imgName = file.name;

      await uploadImage(file).then((id) => {
        this.$emit("updated", {
          type: SpecificDataType.InputImage,
          imageId: id,
        });
        srcImgIds.push(id)
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
                        id="file"
                        name="file"
                        placeholder="Upload an Image" 
                        required 
                        v-on:change="onFileChange"
                        />
                </label>
</template>
