<!-- GNU AGPL v3 License -->

<!--
  This file in its entirety was written by John Nunley and Grace Meredith.
-->

<template>
  <div id="homepage">
    <p class="text-h5 text-center">Welcome to Pictonode!</p>
    <v-divider />
    <v-list class="text-center">
      <v-list-item>
        <router-link class="text-body-1" to="/canvas" tag="v-btn">
          <v-btn>
            Create a new Project
          </v-btn>
        </router-link>
      </v-list-item>
      <v-list-item>
        <p>Open an existing project (TODO)</p>
      </v-list-item>
    </v-list>
  </div>
</template>

<style scoped lang="scss">
#homepage {
  padding: 1rem;
  margin: 1rem;
}
</style>
