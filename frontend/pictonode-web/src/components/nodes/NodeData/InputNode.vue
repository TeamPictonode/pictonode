<!-- GNU AGPL v3 License -->
<!-- Written by John Nunley -->

<script lang="ts">
import { defineComponent } from "vue";
import { uploadImage } from "../../../api";
import ValueTracker, { TrackedValue, TrackedValueType } from "../ValueTracker";

export default defineComponent({
  props: {
    node: {
      type: Object,
      required: true,
    },
  },
  data: () => ({
    imgName: "image",
    fileExists: false,
  }),
  methods: {
    onFileChange(e: any) {
      console.log("made it to on file change");
      const file = e.target.files[0];
      this.imgName = file.name;
      this.fileExists = true;

      uploadImage(file).then((id) => {
        ValueTracker.get_instance().set_value({
          node_id: this.node.id,
          type: TrackedValueType.SrcImage,
          image: id,
        });
      });
    },
  },
});
</script>

<template>
  <label htmlFor="image">
    {{ imgName }}
    <input
      v-if="!fileExists"
      type="file"
      id="file"
      name="file"
      placeholder="Upload an Image"
      required
      v-on:change="onFileChange"
    />
  </label>
</template>
