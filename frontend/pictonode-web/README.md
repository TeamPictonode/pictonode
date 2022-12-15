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
