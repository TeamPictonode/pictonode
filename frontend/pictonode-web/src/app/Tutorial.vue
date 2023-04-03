
<template>
  <div class="tutorial-items">
    <div style="position: fixed; align-self: flex-start;">
    <router-link to="/" tag="v-btn" style="color: white">
          <v-btn color="#474545" rounded="pill"> back to home </v-btn>
    </router-link>
  </div>
    <div class="title-logo">
      <img src="https://pictonode.s3.us-west-2.amazonaws.com/pictonode_logo.png" alt="Pictonode Logo" style="height: auto; width: 500px;">
    </div>
    <div class="title-logo tutorial-header">
      <h1 class="body-content tutorial-header">Quick Start</h1>
      <p class="body-content tutorial-paragraph">Welcome to Pictonode! Here is a quickstart guide for using our interface, and creating your first project</p>
    </div>
    <div class="title-logo tutorial-header">
      <h1 class="body-content tutorial-header">
        Uploading your first Image
      </h1>
      <p class="body-content tutorial-paragraph">Upon creating a project, you should be presented with an input node and a rendered node. The first step is to upload an image: </p>
      <img class="tutorial-images" src="https://pictonode.s3.us-west-2.amazonaws.com/Tutorial1.png" alt="Initial Nodes">
      <p class="body-content tutorial-paragraph">Once Uploaded, your input node should look something like this: </p>
      <img class="tutorial-images" style="width: 40%" src="https://pictonode.s3.us-west-2.amazonaws.com/Tutorial2.png" alt="Uploaded image">
      <p class="body-content tutorial-paragraph">Next, Just drag the image output to the rendered input: now you have an image!</p>
      <img class="tutorial-images" src="https://pictonode.s3.us-west-2.amazonaws.com/Tutorial3.png" alt="drag image">
      <img class="tutorial-images" src="https://pictonode.s3.us-west-2.amazonaws.com/Tutorial4.png" alt="rendered image">
    </div>
    <div class="title-logo tutorial-header">
      <h1  class="body-content tutorial-header">Deleting a connection</h1>
      <p class="body-content tutorial-paragraph">To delete a node connection, just single click on the right part of the connection</p>
      <img class="tutorial-images" src="https://pictonode.s3.us-west-2.amazonaws.com/Tutorial5.png" alt="delete a connection">
    </div>
    <div class="title-logo tutorial-header">
      <h1 class="body-content tutorial-header">Adding a Node</h1>
      <p class="body-content tutorial-paragraph">To add a node, just right click anywhere in the editor, and select "add node"</p>
      <img class="tutorial-images" src="https://pictonode.s3.us-west-2.amazonaws.com/Tutorial6.png" alt="right-click">
      <img class="tutorial-images" src="https://pictonode.s3.us-west-2.amazonaws.com/Tutorial7.png" alt="select add node">
      <p class="body-content tutorial-paragraph">Select the node type you would like to use: </p>
      <img class="tutorial-images" src="https://pictonode.s3.us-west-2.amazonaws.com/Tutorial8.png" alt="select node type">
      <p class="body-content tutorial-paragraph"> Next connect the nodes together, to get desired affect</p>
      <img class="tutorial-images" src="https://pictonode.s3.us-west-2.amazonaws.com/Tutorial10.png" alt="connect invert node">
    </div>
    <div class="title-logo tutorial-header">
      <h1 class="body-content tutorial-header">Combining Nodes</h1>
      <p class="body-content tutorial-paragraph">Now, you can experiment with different node combinations!</p>
      <img class="tutorial-images" src="https://pictonode.s3.us-west-2.amazonaws.com/Tutorial11.png" alt="disconnect invert node">
      <img class="tutorial-images" src="https://pictonode.s3.us-west-2.amazonaws.com/Tutorial12.png" alt="add gauss blur">
    </div>
    <div class="title-logo tutorial-header">
      <h1 class="body-content tutorial-header">Changing Source Image</h1>
      <P class="body-content tutorial-paragraph">If you want to change the source image, hover on the input image node, right-click to delete it, and add a new input image node</P>
      <img class="tutorial-images" src="https://pictonode.s3.us-west-2.amazonaws.com/Tutorial13.png" alt="delete node">
      <img class="tutorial-images" src="https://pictonode.s3.us-west-2.amazonaws.com/Tutorial14.png" alt="add image node">
      <img class="tutorial-images" src="https://pictonode.s3.us-west-2.amazonaws.com/Tutorial15.png" alt="upload new image">
    </div>
    <div class="title-logo tutorial-header">
      <h1 class="body-content tutorial-header">That's it for now...</h1>
      <p class="body-content tutorial-paragraph">Congratulations! You're ready to start creating projects</p>
    </div>
  </div>
</template>

<style lang="scss">
  .tutorial-items {
    display: flex;
    flex-direction: column;
    align-items: center;
    width: 100%;
    position: relative;
   
  }
  .title-logo {
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

  .body-content {
    align-self: flex-start;
    padding-left: 3rem;
  }

  .tutorial-header {
    font-size: 40px;
  }

  .tutorial-paragraph {
    font-size: 20px;
    margin-top: 1rem;
  }

  .tutorial-images {
    height: auto;
    width: 80%;
    border-radius: 25px;
    align-self: center;
    margin-top: 3rem;
  }
</style>