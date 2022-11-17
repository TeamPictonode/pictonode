<!-- GNU AGPL v3 License -->
<script lang="ts">
  import { defineComponent } from "vue";

  export default defineComponent({
    name: "Topbar",
  });
</script>

<template>
  <v-app-bar pictonode>
    <v-app-bar-nav-icon />
    <v-toolbar-title>Pictonode</v-toolbar-title>
    <router-link to="/">Homepage</router-link>
    <v-spacer />
    <v-menu left bottom>
      <template #activator="{ props }">
        <v-btn icon v-bind="props">
          <v-icon>mdi-dots-vertical</v-icon>
        </v-btn>
      </template>

      <v-list>
        <v-list-item>
          <router-link to="/login">Login</router-link> 
        </v-list-item>
        <v-list-item>
          <router-link to="/register">Register</router-link>
        </v-list-item>
        <v-list-item>
          Settings (TODO)
        </v-list-item>
      </v-list>
    </v-menu>
  </v-app-bar>
</template>