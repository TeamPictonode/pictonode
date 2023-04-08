<!-- GNU AGPL v3 License -->

<!--
  This file in its entirety was written by John Nunley and Grace Meredith.
-->

<script lang="ts">
import { profile } from "console";
import { defineComponent } from "vue";
import { useStore } from 'vuex'
import { ref } from 'vue'
import store from "../store";

export default defineComponent({
  name: "Topbar",
  data: () => ({
    drawer: false,
    group: null,
    loggedIn: false,
  }),

  setup() {
    const store = useStore()
  },
  watch: {
    group() {
      this.drawer = false;
    },
  },
  computed: {
    user() {
      return store.getters.user;
    }
  },
  methods: {
    async signout() {
      await store.dispatch('logOut')
      this.$router.push("/login");
    }
  }
});
</script>

<template>
  <v-layout>
    <v-app-bar color="#474545" pictonode>
      <v-toolbar-title>
        <router-link to="/" tag="v-btn" style="color: white">
          <v-btn> Pictonode </v-btn>
        </router-link>

        <router-link
          class="text-body-1"
          to="/about"
          tag="v-btn"
          style="color: white"
        >
          <v-btn> About Page </v-btn>
        </router-link>
        <router-link
          class="text-body-1"
          to="/tutorial"
          tag="v-btn"
          style="color: white"
        >
          <v-btn> Tutorial </v-btn>
        </router-link>
      </v-toolbar-title>
      <v-spacer />
      <v-menu rounded="pill" slide-x left bottom>
        <template #activator="{ props }">
          <v-btn icon v-bind="props">
            <v-icon color="white">mdi-dots-vertical</v-icon>
          </v-btn>
        </template>

        <v-list v-if="user.loggedIn">
          <v-list-item>
            <v-btn rounded="pill" color="#474545" style="color: white">Account</v-btn>
          </v-list-item>
          <v-list-item>
            <v-btn rounded="pill" color="#474545" @click="signout()" style="color: white">Log Out</v-btn>
          </v-list-item>
        </v-list>

        <v-list v-else>
          <v-list-item>
            <router-link to="/login" tag="v-btn" style="color: white">
              <v-btn rounded="pill" color="#474545"> Login </v-btn>
            </router-link>
          </v-list-item>
          <v-list-item>
            <router-link to="/register" tag="v-btn" style="color: white">
              <v-btn rounded="pill" color="#474545">
                Register
              </v-btn></router-link
            >
          </v-list-item>
        </v-list>
      </v-menu>
    </v-app-bar>
  </v-layout>
</template>

<style></style>
