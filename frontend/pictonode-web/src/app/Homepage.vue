<!-- GNU AGPL v3 License -->

<!--
  This file in its entirety was written by John Nunley and Grace Meredith.
-->

<template>
  <div class="home-items">
    <div id="homepage">
      <p class="welcome text-center">Pictonode</p>
      <p class="text-center" style="color: white">
        Your new favorite image editor
      </p>
    </div>
    <div class="home-options">
      <v-divider />
      <v-list class="text-center home-list">
        <v-list-item>
          <router-link
            class="text-body-1"
            to="/canvas"
            tag="v-btn"
            style="color: white"
          >
            <v-btn rounded="pill" size="large" color="#bddde9">
              Create a new Project
            </v-btn>
          </router-link>
        </v-list-item>
        <v-list-item>
          <router-link
            class="text-body-1"
            to="/baklava"
            tag="v-btn"
            style="color: white"
          >
            <v-btn rounded="pill" size="large" color="#bddde9">
              baklava test
            </v-btn>
          </router-link>
        </v-list-item>
        <v-list-item>
          <p>Open an existing project (TODO)</p>
        </v-list-item>
      </v-list>
    </div>
  </div>
</template>

<style scoped lang="scss">
@import url("https://fonts.googleapis.com/css2?family=Alfa+Slab+One&family=Poppins:wght@300&display=swap");
#homepage {
  padding: 1rem;
  margin-left: 20rem;
  background: #bddde9;
  width: 700px;
  height: 500px;
  border-radius: 25px;
}

.welcome {
  padding-top: 150px;
  font-size: 100px;
  font-family: "Alfa Slab One", sans-serif;
  color: white;
}
.home-list {
  background-color: transparent;
  padding-left: 130px;
}
.home-options {
  align-items: right;
}

.home-items {
  display: flex;
  flex-direction: row;
}
</style>
