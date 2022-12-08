<!-- GNU AGPL v3 License -->

<script lang="ts">
import { defineComponent } from "vue";

export default defineComponent({
  name: "Register",
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
              <v-text-field label="Username" solo />
            </v-col>
          </v-row>
          <v-row>
            <v-col cols="12">
              <v-text-field label="Email" solo />
            </v-col>
          </v-row>
          <v-row>
            <v-col cols="12" sm="6">
              <v-text-field label="First Name" solo />
            </v-col>
            <v-col cols="12" sm="6">
              <v-text-field label="Last Name" solo />
            </v-col>
          </v-row>
          <v-row>
            <v-col cols="6">
              <v-text-field type="password" label="Password" />
            </v-col>
            <v-col cols="6">
              <v-text-field type="password" label="Confirm Password" />
            </v-col>
          </v-row>
        </v-container>
      </v-form>
    </v-card-text>
    <v-card-actions>
      <v-spacer />
      <v-btn color="primary">Register</v-btn>
    </v-card-actions>
  </v-card>
</template>

<style scoped lang="scss">
#register {
  padding: 1rem;
  margin: 1rem;
}
</style>
