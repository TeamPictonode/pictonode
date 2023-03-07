<!-- GNU AGPL v3 License -->

<!--
  This file in its entirety was written by John Nunley and Grace Meredith.
-->

<script lang="ts">
import { defineComponent } from "vue";

export default defineComponent({
  data: () => ({
    username: null as string | null,
    email: null as string | null,
    firstName: null as string | null,
    lastName: null as string | null,
    password: null as string | null,
  }),
  name: "Register",

  methods:{
    addUsername(template: string) {
      this.username = template
    },
    addEmail(template: string) {
      this.email = template
    },
    addFirstName(template: string) {
      this.firstName = template
    },
    addLastName(template: string) {
      this.lastName = template
    },
    setPassword(template: string) {
      this.password = template
    },
    confirmPassword(template: string) {
      //to do
    },
    setRegister() {
      //to do
    }
  }
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
              <v-text-field label="Username" solo @input="addUsername"/>
            </v-col>
          </v-row>
          <v-row>
            <v-col cols="12">
              <v-text-field label="Email" solo @input="addEmail"/>
            </v-col>
          </v-row>
          <v-row>
            <v-col cols="12" sm="6">
              <v-text-field label="First Name" solo @input="addFirstName"/>
            </v-col>
            <v-col cols="12" sm="6">
              <v-text-field label="Last Name" solo @input="addLastName"/>
            </v-col>
          </v-row>
          <v-row>
            <v-col cols="6">
              <v-text-field type="password" label="Password" @input="setPassword"/>
            </v-col>
            <v-col cols="6">
              <v-text-field type="password" label="Confirm Password" @input="confirmPassword"/>
            </v-col>
          </v-row>
        </v-container>
      </v-form>
    </v-card-text>
    <v-card-actions>
      <v-spacer />
      <v-btn color="primary" @input="setRegister">Register</v-btn>
    </v-card-actions>
  </v-card>
</template>

<style scoped lang="scss">
#register {
  padding: 1rem;
  margin: 1rem;
}
</style>
