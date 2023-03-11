<!-- GNU AGPL v3 License -->

<!--
  This file in its entirety was written by John Nunley and Grace Meredith.
-->

<script lang="ts">
import { defineComponent } from "vue";
import { checkLogin } from "../api";

export default defineComponent({
  data: () => ({
    user: {
      username: null as string | null,
      password: null as string | null,
    },
  }),
  name: "Login",
  methods: {
    login() {
      const user: JSON = <JSON>(<unknown>{
        username: `${this.user.username}`,
        password: `${this.user.password}`,
      });
      checkLogin(user)
        .then(() => {
          this.$router.push("/");
        })
        .catch((error) => {
          const errorCode = error.code;
          const errorMessage = error.message;
          console.log(errorCode);
          console.log(errorMessage);
        });
    },
  },
});
</script>

<template>
  <v-card class="mx-auto" max-width="300" id="login" tile>
    <v-card-title class="text-center">Login</v-card-title>
    <v-card-text>
      <v-form>
        <v-text-field
          label="Username"
          solo
          v-model="user.username"
          aria-required
        />
        <v-text-field
          type="password"
          label="Password"
          v-model="user.password"
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
