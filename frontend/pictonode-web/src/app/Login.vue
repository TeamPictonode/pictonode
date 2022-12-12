<!-- GNU AGPL v3 License -->

<script lang="ts">
import { defineComponent } from "vue";

export default defineComponent({
  name: "Login",
});
</script>

<template>
  <v-card class="mx-auto" max-width="300" id="login" tile>
    <v-card-title class="text-center">Login</v-card-title>
    <v-card-text>
      <v-form>
        <v-text-field label="Username" solo />
        <v-text-field type="password" label="Password" />
      </v-form>
    </v-card-text>
    <v-card-actions>
      <v-spacer />
      <v-btn color="primary">Login</v-btn>
    </v-card-actions>
  </v-card>
</template>

<style scoped lang="scss">
#login {
  padding: 1rem;
  margin: 1rem;
}
</style>
