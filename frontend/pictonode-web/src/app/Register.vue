<!-- GNU AGPL v3 License -->

<!--
  This file in its entirety was written by John Nunley and Grace Meredith.
-->

<script lang="ts">
import { defineComponent } from "vue";
import { threadId } from "worker_threads";
import { setRegister } from "../api";

export default defineComponent({
  data: () => ({
    user: {
      username: null as string | null,
      firstName: null as string | null,
      password: null as string | null,
    },
  }),
  name: "Register",

  methods: {
    addUsername(template: string) {
      this.user.username = template;
    },
    addFirstName(template: string) {
      this.user.firstName = template;
    },
    setPassword(template: string) {
      this.user.password = template;
    },
    confirmPassword(template: string) {
      //to do
    },
    register() {
      const user: JSON = <JSON>(<unknown>{
        username: `${this.user.username}`,
        realname: `${this.user.firstName}`,
        password: `${this.user.password}`,
      });
      setRegister(user)
        .then(() => {
          console.log("Registration completed");
          this.$router.push("/login");
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
  <v-card class="mx-auto" max-width="600" id="register" tile>
    <v-card-title class="text-center">Register</v-card-title>
    <v-card-text>
      <v-form>
        <v-container>
          <v-row>
            <v-col cols="12">
              <v-text-field
                label="Username"
                solo
                @input="addUsername"
                aria-required
              />
            </v-col>
          </v-row>
          <v-row>
            <v-col cols="12" sm="6">
              <v-text-field
                label="Name"
                solo
                @input="addFirstName"
                aria-required
              />
            </v-col>
          </v-row>
          <v-row>
            <v-col cols="6">
              <v-text-field
                type="password"
                label="Password"
                @input="setPassword"
                aria-required
              />
            </v-col>
            <v-col cols="6">
              <v-text-field
                type="password"
                label="Confirm Password"
                @input="confirmPassword"
                aria-required
              />
            </v-col>
          </v-row>
        </v-container>
      </v-form>
    </v-card-text>
    <v-card-actions>
      <v-spacer />
      <v-btn color="primary" @click="register">Register</v-btn>
    </v-card-actions>
  </v-card>
</template>

<style scoped lang="scss">
#register {
  padding: 1rem;
  margin: 1rem;
}
</style>
