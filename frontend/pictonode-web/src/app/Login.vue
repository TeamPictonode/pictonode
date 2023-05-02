<!-- GNU AGPL v3 License -->

<!--
  This file in its entirety was written by John Nunley and Grace Meredith.
-->

<script lang="ts">
import { defineComponent } from "vue";
import { ref } from "vue";
import { useStore } from "vuex";
import { checkLogin } from "../api";
import store from "../store";

export default defineComponent({
  data: () => ({
    username: ref(null as string | null),
    password: ref(null as string | null),
    failed: false,
  }),
  setup() {
    const store = useStore();
  },
  name: "Login",
  methods: {
    async login() {
      const result = await checkLogin({
        username: `${this.username}`,
        password: `${this.password}`,
      });

      // result is a JSON object that contains "error" if it errored out
      if ("error" in result) {
        this.failed = true;
        return;
      }

      //await store.dispatch("login", user);
      this.$router.push("/");

      // Reload the window to reload the topbar
      window.location.reload();
    },
  },
});
</script>

<template>
  <v-card class="mx-auto" max-width="300" id="login" tile>
    <v-card-title class="text-center">Login</v-card-title>
    <v-card-text>
      <div v-if="failed" class="text-center">
        <p>Failed to log in.</p>
      </div>
      <v-form>
        <v-text-field label="Username" solo v-model="username" aria-required />
        <v-text-field
          type="password"
          label="Password"
          v-model="password"
          aria-required
        />
      </v-form>
    </v-card-text>
    <v-card-actions>
      <v-spacer />
      <v-btn color="black" rounded="pill" @click="login">Login</v-btn>
    </v-card-actions>
  </v-card>
</template>

<style lang="scss">
#login {
  padding: 1rem;
  margin: 1rem;
}
</style>
