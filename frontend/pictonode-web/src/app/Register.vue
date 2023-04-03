<!-- GNU AGPL v3 License -->

<!--
  This file in its entirety was written by John Nunley and Grace Meredith.
-->

<script lang="ts">
import { defineComponent } from "vue";
import { setRegister } from "../api";

export default defineComponent({
  data: () => ({
    user: {
      username: null as string | null,
      fullName: null as string | null,
      password: null as string | null,
      confirmPassword: null as string | null,
    },
    errorMessage: "Passwords do not match",
    error: false,
  }),
  name: "Register",
  methods: {
    register() {
      const user: JSON = <JSON>(<unknown>{
        username: `${this.user.username}`,
        realname: `${this.user.fullName}`,
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

    validateForm() {
      if (this.user.password !== this.user.confirmPassword) {
        this.error = true;
        return false;
      }
      this.error = false;
      return true;
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
                v-model="user.username"
                aria-required
              >
              </v-text-field>
            </v-col>
          </v-row>
          <v-row>
            <v-col cols="12" sm="6">
              <v-text-field
                label="Name"
                solo
                v-model="user.fullName"
                aria-required
              />
            </v-col>
          </v-row>
          <v-row>
            <v-col cols="6">
              <v-text-field
                type="password"
                label="Password"
                v-model="user.password"
                aria-required
              />
            </v-col>
            <v-col cols="6">
              <v-text-field
                type="password"
                label="Confirm Password"
                v-model="user.confirmPassword"
                @input="validateForm"
                aria-required
              />
              <p v-if="error" style="color: red">{{ errorMessage }}</p>
            </v-col>
          </v-row>
        </v-container>
      </v-form>
    </v-card-text>
    <v-card-actions>
      <v-spacer />
      <v-btn color="black" rounded="pill" @click="register">Register</v-btn>
    </v-card-actions>
  </v-card>
</template>

<style lang="scss">
#register {
  padding: 1rem;
  margin: 1rem;
}
</style>
