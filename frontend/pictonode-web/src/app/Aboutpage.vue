<template>
  <div id="aboutpage">
    <p class="text-h5 text-center">Pictonode</p>
    <div class="about">
      <p class="text-h6 text-center">
        CS 426 Senior Project in Computer Science, Spring 2023, University of
        Nevada, Reno, Department of Computer Science and Engineering
      </p>
      <p class="text-h6 text-center">Team #7: Team Picto</p>
      <p class="text-h6 text-center">
        Developers: John Nunley, Stephen Foster, Parker Nelms, & Grace Meredith
      </p>
      <p class="text-h6 text-center">
        Instructors: Dr. Dave Feil-Seifer, Mrs. Devrin Lee
      </p>
      <p class="text-h6 text-center">Advisor: Dr. Alireza Tavakkoli</p>
    </div>
    <div class="about">
      <h1 class="text-h4 text-center">Project Description</h1>
      <P class="text-center"
        >The main goals of Pictonode include helping artists save time on their
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
      </P>
    </div>
    <div class="about">
      <h1 class="text-h4 text-center">Related Projects and Resources</h1>
      <v-list class="text-center list">
        <v-list-item>
          <a
            class="text-body-1 buttonLinks"
            href="https://github.com/notgull/pictonode"
            tag="v-btn"
          >
            <v-btn rounded="pill" color="#e1e9d0" size="x-large">
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
            <v-btn rounded="pill" color="#e1e9d0" size="x-large">
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
            <v-btn rounded="pill" color="#e1e9d0" size="x-large"> GIMP </v-btn>
          </a>
        </v-list-item>
        <v-list-item>
          <a
            class="text-body-1 buttonLinks"
            href="https://www.gegl.org"
            tag="v-btn"
          >
            <v-btn rounded="pill" color="#e1e9d0" size="x-large"> GEGL </v-btn>
          </a>
        </v-list-item>
        <v-list-item>
          <a
            class="text-body-1 buttonLinks"
            href="https://github.com/aluntzer/gtknodes"
            tag="v-btn"
          >
            <v-btn rounded="pill" color="#e1e9d0" size="x-large">
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
            <v-btn rounded="pill" color="#e1e9d0" size="x-large">
              GTK.NodeGraph
            </v-btn>
          </a>
        </v-list-item>
      </v-list>
    </div>
  </div>
</template>

<style scoped lang="scss">
#aboutpage {
  padding: 1rem;
  margin: 1rem;
}

.about {
  margin-bottom: 50px;
}
.list {
  display: flex;
  flex-direction: row;
  justify-content: space-around;
  align-items: center;
  background-color: #bddde9;
}
.buttonLinks {
  color: black;
}
</style>
