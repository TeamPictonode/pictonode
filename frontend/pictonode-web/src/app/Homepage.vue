<!-- GNU AGPL v3 License -->

<!--
  This file in its entirety was written by John Nunley and Grace Meredith.
-->

<script>
import { defineComponent } from "vue";
import { getUsername, listSavedProjects } from "../api";

export default defineComponent({
  data: () => ({
    savedProjects: [],
  }),

  mounted() {
    getUsername().then(async (name) => {
      if ("error" in name) {
        this.savedProjects = [];
      } else {
        this.savedProjects = await listSavedProjects(name["username"]);
      }
    });
  },
});
</script>

<template>
  <div class="home-items">
    <div id="homepage">
      <img
        class="pictonode-logo"
        src="https://pictonode.s3.us-west-2.amazonaws.com/pictonode_logo.png"
        alt="Pictonode Logo"
      />
      <p class="text-center" style="color: white; font-size: 50px">
        Your new favorite image editor
      </p>
    </div>
    <div class="home-options">
      <v-divider />
      <v-list class="text-center home-list">
        <v-list-item>
          <router-link
            class="text-body-1"
            to="/editor"
            tag="v-btn"
            style="color: white"
          >
            <v-btn rounded="pill" size="large" color="#474545">
              Create a new Project
            </v-btn>
          </router-link>
        </v-list-item>
        <div class="scrollbox">
          <router-link
            v-for="project in savedProjects"
            :key="project.id"
            class="text-body-1"
            :to="'/editor/' + project.id"
            tag="v-btn"
            style="color: white"
          >
            <v-list-item>
              <v-btn rounded="pill" size="large" color="#696969">
                {{ project.name }}
              </v-btn>
            </v-list-item>
          </router-link>
        </div>
      </v-list>
    </div>
  </div>
</template>

<style scoped lang="scss">
@import url("https://fonts.googleapis.com/css2?family=Alfa+Slab+One&family=Poppins:wght@300&display=swap");
#homepage {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 1rem;
  margin-left: 5rem;
  background: #474545;
  width: 1050px;
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
  align-items: center;
  justify-content: center;
}

.pictonode-logo {
  width: auto;
  height: 250px;
}

.scrollbox {
  overflow-y: scroll;
  height: 50%;
  width: 300px;
  border: 1px solid #474545;
  border-radius: 5px;
  padding: 5px;
  margin-bottom: 10px;
}
</style>
