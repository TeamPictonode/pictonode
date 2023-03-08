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
    }
  }),
  name: "Login",
  methods: {
    setUsername(template: string) {
      this.user.username = template
    },
    setPassword(template: string) {
      this.user.password = template
    },
    login() {
      checkLogin(this.user)
        .then(() => {
          this.$router.push("/home");
        })
        .catch((error) => {
          const errorCode = error.code;
          const errorMessage = error.message;
          console.log(errorCode);
          console.log(errorMessage);
        });
    }
  }
});
</script>

<template>
  <v-card class="mx-auto" max-width="300" id="login" tile>
    <v-card-title class="text-center">Login</v-card-title>
    <v-card-text>
      <v-form>
        <v-text-field label="Username" solo @input="setUsername" aria-required/>
        <v-text-field type="password" label="Password" @input="setPassword" aria-required/>
      </v-form>
    </v-card-text>
    <v-card-actions>
      <v-spacer />
      <v-btn color="primary" @click="login">Login</v-btn>
    </v-card-actions>
  </v-card>
</template>

<style scoped lang="scss">
#login {
  padding: 1rem;
  margin: 1rem;
}
</style>
