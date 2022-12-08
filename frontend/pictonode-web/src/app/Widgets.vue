<!-- GNU AGPL v3 License -->
<script lang="ts">
import { defineComponent } from "vue";

const ITEMS = [
  {
    name: "INPUTS",
    values: ["Input Image", "Solid Color"],
  },
  {
    name: "COMPOSITES",
    values: ["Composite Images"],
  },
  {
    name: "OUTPUTS",
    values: ["Render Image"],
  },
];

export default defineComponent({
  name: "Widgets",
  data() {
    return {
      items: ITEMS,
    };
  },
});
</script>

<template>
  <v-card class="mx-auto" max-width="300" id="widgets" tile>
    <v-list>
      <div v-for="item in items" :key="item.name">
        <v-subheader>{{ item.name }}</v-subheader>
        <v-list-item-group color="primary">
          <v-list-item v-for="value in item.values" :key="value">
            <v-btn plain>
              {{ value }}
            </v-btn>
          </v-list-item>
        </v-list-item-group>
      </div>
    </v-list>
  </v-card>
</template>

<style scoped lang="scss">
#widgets {
  padding: 1rem;
  margin: 1rem;
}
</style>
