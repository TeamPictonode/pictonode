<!-- GNU AGPL v3 License -->

<!--
  This file in its entirety was written by John Nunley and Grace Meredith.
-->

<script lang="ts">
import { defineComponent } from "vue";
import { useStore } from "vuex";
import { ref } from "vue";
import { setRegister } from "../api";
import store from "../store";

export default defineComponent({
  data: () => ({
    username: ref(null as string | null),
    fullName: ref(null as string | null),
    password: ref(null as string | null),
    confirmPassword: null as string | null,
    errorMessage: "Passwords do not match",
    error: false,
  }),

  setup() {
    const store = useStore();
  },

  name: "Register",
  methods: {
    async register() {
      const result = await setRegister({
        username: `${this.username}`,
        realname: `${this.fullName}`,
        password: `${this.password}`,
      });
      if ("error" in result) {
        this.error = true;
        this.errorMessage = result["error"];
        return;
      }

      //await store.dispatch("register", user);
      this.$router.push("/login");
    },

    validateForm() {
      if (this.password !== this.confirmPassword) {
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
                v-model="username"
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
                v-model="fullName"
                aria-required
              />
            </v-col>
          </v-row>
          <v-row>
            <v-col cols="6">
              <v-text-field
                type="password"
                label="Password"
                v-model="password"
                aria-required
              />
            </v-col>
            <v-col cols="6">
              <v-text-field
                type="password"
                label="Confirm Password"
                v-model="confirmPassword"
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
