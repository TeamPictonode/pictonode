<!-- GNU AGPL v3 License -->

<!--
  This file in its entirety was written by John Nunley and Grace Meredith.
-->

<script lang="ts">
import { defineComponent } from "vue";
import { nodeTemplates } from "../components/nodes/NodeTypes";

interface Item {
  templateName: string;
  name: string;
  tooltip: string;
}

interface Category {
  name: string;
  values: Item[];
}

function categorize(): Category[] {
  const catmap = new Map<string, Category>();
  const templates = nodeTemplates; 

  for (const template of Object.values(templates)) {
    const category = template.category;
    const name = template.displayName;
    const tooltip = template.tooltip;

    if (!catmap.has(category)) {
      catmap.set(category, {
        name: category,
        values: [],
      });
    }

    const cat = catmap.get(category);
    if (cat) {
      cat.values.push({
        templateName: template.templateName,
        name,
        tooltip,
      });
    }
  }

  return Array.from(catmap.values());
}

export default defineComponent({
  name: "Widgets",
  emits: ["input"],
  data() {
    return {
      items: categorize(),
    };
  },

  methods: {
    addNode(item: Item) {
      this.$emit("input", item.templateName);
    },
  },
});
</script>

<template>
  <v-card class="mx-auto" max-width="300" id="widgets" tile color="#bddde9">
    <v-list>
      <div v-for="item in items" :key="item.name">
        <v-list-item-group color="primary">
          <v-list-item v-for="value in item.values" :key="value.templateName">
            <v-btn rounded="pill" color="#e1e9d0" size="x-large" plain @click="() => addNode(value)">
              {{ value.name }}
              <v-tooltip activator="parent" location="top">{{ value.tooltip }}</v-tooltip>
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
