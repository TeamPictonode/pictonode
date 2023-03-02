<!-- GNU AGPL v3 License -->

<!--
  This file in its entirety was written by John Nunley and Grace Meredith.
-->

<script lang="ts">
import { profile } from "console";
import { defineComponent } from "vue";
export default defineComponent({
  name: "Topbar",
  data: () => ({
    drawer: false,
    group: null,
  }),
  watch: {
    group() {
      this.drawer = false;
    },
  },
});
</script>

<template>
  <v-layout>
    <v-app-bar color="#e1e9d0" pictonode>
      <v-app-bar-nav-icon @click.stop="drawer = !drawer"></v-app-bar-nav-icon>
      <v-toolbar-title>
        <router-link to="/" tag="v-btn" style="color: black">
          <v-btn> Pictonode </v-btn>
        </router-link>

        <router-link
          class="text-body-1"
          to="/about"
          tag="v-btn"
          style="color: black"
        >
          <v-btn> About Page </v-btn>
        </router-link>
      </v-toolbar-title>
      <v-spacer />
      <v-menu rounded="pill" slide-x left bottom>
        <template #activator="{ props }">
          <v-btn icon v-bind="props">
            <v-icon>mdi-dots-vertical</v-icon>
          </v-btn>
        </template>

        <v-list>
          <v-list-item>
            <router-link to="/login" tag="v-btn" style="color: black">
              <v-btn rounded="pill" color="#e1e9d0"> Login </v-btn>
            </router-link>
          </v-list-item>
          <v-list-item>
            <router-link to="/register" tag="v-btn" style="color: black">
              <v-btn rounded="pill" color="#e1e9d0">
                Register
              </v-btn></router-link
            >
          </v-list-item>
          <v-list-item> Settings (TODO) </v-list-item>
        </v-list>
      </v-menu>
    </v-app-bar>
    <v-navigation-drawer color="#e1e9d0" v-model="drawer">
      <v-list>
        <v-list-item
          prepend-icon="mdi-account"
          title="My Account"
        ></v-list-item>
        <v-list-item title="Go back to GIMP //TODO"></v-list-item>
        <v-list-item title="Save Project //TODO"></v-list-item>
      </v-list>
    </v-navigation-drawer>
  </v-layout>
</template>

<style></style>
