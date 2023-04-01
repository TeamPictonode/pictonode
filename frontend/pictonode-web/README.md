# pictonode-web

Pictonode web frontend. Many pictos, much nodes. Wow.

## Credits

The code in this folder was developed in its entirety by John Nunley (notgull) and Grace Meredith, with a few exceptions. All dependencies except for `libnode` were created by others.

## Development

Install a recent version of Node and NPM. Linux/MacOS users can use [nvm](https://github.com/nvm-sh/nvm#install--update-script) to take care of this. Just do:

```bash
$ curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.2/install.sh | bash
$ nvm install node # install latest version of node/npm
```

Windows users can install Node from [here](https://nodejs.org/en/download/current/) (or alternatively, install a better OS :wink:).

Then, run the following commands to start the development server:

```bash
$ cd frontend/pictonode-web # change to the frontend directory
$ npm install # install dependencies
$ npx webpack serve # run the dev server
```

All is tested on the latest version of Node (`v19.0.1` at the time of writing). If you aren't sure you're running the latest Node, run:

```
$ node --version
```

to see the version you're running.

Whatever you do, do not install Node/NVM in the latest WSL. There are a handful of bugs there.

## Baklava JS: How it we're using it

BaklavaJS is a javascript library that renders nodes and handles a lot of our node-graph interface. Here are the basics you should know:

-The editor itself comes from Baklava's Core, and is rendered through ViewPlugin.
-On create, we must use the editor to register each node type we have created, and then use the engine to run the initial calculation.
-Baklava auto-recalculates the entire node tree dynamically with eachn option/input change

-for the ImgsSrc input, we are able to register a vue component as an option, using the option-plugin. Unfortunately, due to Baklava's asynchronous behavior, and the asynchronous behavior of uploading files, we are only allowing one upload per img src node as the processes screw up the calculation process. Baklava currenty doesn't have a recalculate option, and I have yet to sort out a viable solution to this.

-Each node created recieves a current pipeline and adds it's node/link attributes to the pipeline before passing it on the next node. Once it reaches the final rendered node, it does the final process of sending the completed pipeline to ontario and updated our canvas tag with the new rendered image.

-currently every node-type is functioning except composite node returns 500, and brightness/contrast doesn't seem to have any visual affect to the rendered image.
