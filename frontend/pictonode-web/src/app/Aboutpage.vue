<template>
  <div class="about-items">
    <div style="position: fixed; align-self: flex-start">
      <router-link to="/" tag="v-btn" style="color: white">
        <v-btn color="#474545" rounded="pill"> back to home </v-btn>
      </router-link>
    </div>
    <div class="about-logo">
      <img
        src="https://pictonode.s3.us-west-2.amazonaws.com/pictonode_logo.png"
        alt="Pictonode Logo"
        style="height: auto; width: 500px"
      />
    </div>
    <div class="about-logo about-header">
      <h1 class="about-body-content about-header">About Pictonode</h1>
      <p class="about-body-content about-paragraph">
        Here, you will find a summary about the Pictonode: Image Editor Project
        and its developers
      </p>
    </div>
    <div class="about-logo about-header">
      <h1 class="about-body-content about-header">Context:</h1>
      <p class="about-body-content about-paragraph">
        CS 426 Senior Project in Computer Science, Spring 2023, University of
        Nevada, Reno, Department of Computer Science and Engineering
      </p>
    </div>
    <div class="about-logo about-header">
      <h1 class="about-body-content about-header">Developers:</h1>
      <p class="about-body-content about-paragraph">
        John Nunley, Stephen Foster, Grace Meredith, & Parker Nelms
      </p>
      <img
        class="about-images"
        src="https://pictonode.s3.us-west-2.amazonaws.com/PictonodeDevs.jpg"
        alt="Initial Nodes"
      />
      <h1 class="about-body-content about-header">Instructors:</h1>
      <p class="about-body-content about-paragraph">
        Dr. Dave Feil-Seifer, Mrs. Devrin Lee
      </p>
      <h1 class="about-body-content about-header" style="margin-top: 1em">
        Advisor:
      </h1>
      <p class="about-body-content about-paragraph">
        Dr. Alireza Tavakkoli (Professor at UNR)
      </p>
    </div>
    <div class="about-logo about-header">
      <h1 class="about-body-content about-header">Project Description:</h1>
      <p class="about-body-content about-paragraph">
        The main goals of Pictonode include helping artists save time on their
        projects, create a lightweight environment for beginner digital artists,
        and innovate GIMP’s non-destructive image editing with a fresh user
        interface. Pictonode implements node-based editing for users, so they
        can visualize how each component of their image works together to create
        the rendered output image. Our intended users include digital artists,
        photographers, graphic designers, students, and GIMP enthusiasts.
        Essentially, if they need a quick, lightweight option to make easy edits
        to their image, they can visit our web-app, upload an image and
        experiment with our input nodes from there. On the other hand, if a user
        is deep in a GIMP project, and needs to create a simple easy edit to a
        layer, they can access our plugin by launching our app, which will open
        the current layer as a new Pictonode project, perform the input nodes
        they need to, and go back to GIMP seamlessly. Finally, another interest
        for users could potentially be educators who want a lightweight
        application to introduce their students to digital art. Main
        functionality that will be implemented in Pictonode include: uploading
        an image, creating a new project, opening an existing project, creating
        input nodes for the image, rendering an output image, saving the
        rendered image, and opening/closing the plugin from GIMP. For the
        technologies, we are using NodeJS, Vue3 and Typescript for the web-app,
        Python and the GTKNodes library for the plugin, and Postgres with
        Typescript for the backend. Essentially, Pictonode will have two
        front-end systems for the web-app and GIMP plugin, which will share a
        daemon for the node processing.
      </p>
    </div>
    <div class="about-logo about-header">
      <h1 class="about-body-content about-header">About the Devs:</h1>
      <h2 class="about-body-content about-2nd-header">John Nunley</h2>
      <p class="about-body-content about-paragraph">
        John designed & developed the backend system for Pictonode. He also
        assisted in some of the front-end development for the website. His main
        interests include Italian architecture and cyber security.
      </p>
      <h2 class="about-body-content about-2nd-header">Parker Nelms</h2>
      <p class="about-body-content about-paragraph">
        Parker implemented most of the UI for our native GIMP Plugin
        application. His interests include music and data science.
      </p>
      <h2 class="about-body-content about-2nd-header">Stephen Foster</h2>
      <p class="about-body-content about-paragraph">
        Stephen designed the architecture, and helped implement the UI for our
        native GIMP Plugin application. His interests include teaching his
        friends how to program, and game development.
      </p>
      <h2 class="about-body-content about-2nd-header">Grace Meredith</h2>
      <p class="about-body-content about-paragraph">
        Grace implemented most of the front-end design for the website. Her main
        interests include art and web development.
      </p>
    </div>
    <div class="about-logo about-header">
      <h1 class="about-body-content about-header">
        Related Projects and Resources:
      </h1>
      <v-list class="text-center button-list">
        <v-list-item>
          <a
            class="text-body-1 buttonLinks"
            href="https://github.com/notgull/pictonode"
            tag="v-btn"
          >
            <v-btn rounded="pill" color="#c3dee5" size="x-large">
              Github Repo
            </v-btn>
          </a>
        </v-list-item>
        <v-list-item>
          <a
            class="text-body-1 buttonLinks"
            href="https://www.blender.org"
            tag="v-btn"
          >
            <v-btn rounded="pill" color="#c3dee5" size="x-large">
              Blender
            </v-btn>
          </a>
        </v-list-item>
        <v-list-item>
          <a
            class="text-body-1 buttonLinks"
            href="https://www.gimp.org"
            tag="v-btn"
          >
            <v-btn rounded="pill" color="#c3dee5" size="x-large"> GIMP </v-btn>
          </a>
        </v-list-item>
        <v-list-item>
          <a
            class="text-body-1 buttonLinks"
            href="https://www.gegl.org"
            tag="v-btn"
          >
            <v-btn rounded="pill" color="#c3dee5" size="x-large"> GEGL </v-btn>
          </a>
        </v-list-item>
        <v-list-item>
          <a
            class="text-body-1 buttonLinks"
            href="https://github.com/aluntzer/gtknodes"
            tag="v-btn"
          >
            <v-btn rounded="pill" color="#c3dee5" size="x-large">
              GTKNodes
            </v-btn>
          </a>
        </v-list-item>
        <v-list-item>
          <a
            class="text-body-1 buttonLinks"
            href=" https://github.com/AliensGroup/Gtk.NodeGraph"
            tag="v-btn"
          >
            <v-btn rounded="pill" color="#c3dee5" size="x-large">
              GTK.NodeGraph
            </v-btn>
          </a>
        </v-list-item>
      </v-list>
    </div>
  </div>
</template>

<style scoped lang="scss">
.about-items {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100%;
  position: relative;
}
.about-logo {
  background-color: #474545;
  display: flex;
  flex-direction: column;
  align-content: space-between;
  width: 1500px;
  padding: 1rem;
  border-radius: 25px;
  color: white;
  margin: 2rem;
}

.about-body-content {
  align-self: flex-start;
  padding-left: 3rem;
}

.about-header {
  font-size: 40px;
}

.about-2nd-header {
  font-size: 25px;
  margin-top: 1rem;
}

.about-paragraph {
  font-size: 20px;
  margin-top: 1rem;
}

.about-images {
  height: auto;
  width: 80%;
  border-radius: 25px;
  align-self: center;
  margin-top: 3rem;
  margin-bottom: 3rem;
}
.buttonLinks {
  color: #474545;
}
.about-images {
  height: auto;
  width: 80%;
  border-radius: 25px;
  align-self: center;
  margin-top: 3rem;
}
.button-list {
  display: flex;
  flex-direction: row;
  background-color: transparent;
}
</style>
