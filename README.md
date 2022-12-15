# pictoode


Pictonode is an image editor using a revolutionary node-based system that allows for greater flexibility and reproducibility. The end goal is to make image processing a parallelized process that anyone can take part in, regardless of their technical background. In addition, we also aim to allow those already familiar with contemporary image editing software to easily transition to Pictonode. 

## Credits

The web interface was written by John Nunley and Grace Meredith. The backend for GIMP was written by Parker Nelms and Stephen Foster.

# ALL BELOW IS DEPREACTED

* As a website that can be used independently.
* As a plugin for Photoshop.
* (Nice To Have) As an independent native application.
* (Nice To Have) As a plugin for GIMP. 

## Intended Project Structure

The overall project is written in [Typescript](https://www.typescriptlang.org/). It is similar to Javascript and is able to be compiled to Javascript easily, for use in browser and plugin applications. However, it also provides type-checking utilities that allow one to avoid the usual footguns that pop up when programming in Javascript. Feel free to write files in Javascript if they contain concepts too difficult to express in Typescript.

"Pure" Typescript indicates that the module should not contain code that relies on the [DOM](https://developer.mozilla.org/en-US/docs/Web/API/Document_Object_Model) or [Node.JS](https://nodejs.org/en/) primitives being present.

This entire repository is set up as a [Yarn](https://yarnpkg.com/) workspace. This ensures that packages can easily depend on eachother and share dependencies. It also allows us to easily run tests across the entire project.

The overall folders are as follows:

- `libraries/` contains the core libraries that are used by the application. These are written in Typescript and are "pure".
- `frontend/` contains the code for the website. This is written in Typescript and is intended to be run on a web environment.
- `backend/` contains the code for the backend. This is written in Typescript and is intended to be run on a Node.JS environment.
- `photostop/` TODO

Each individual package is set up as follows:

- `package.json` describes the package, its dependencies, and its scripts.
- `tsconfig.json` describes the Typescript configuration used for testing.
- `src/` contains the source code for the package.
- `test/` contains the tests for the package using the [Mocha](https://mochajs.org/)/[Chai](https://www.chaijs.com/) testing framework.

In order to run all tests, run the command `yarn workspaces run test`.

### libnode

`libnode` (unrelated to nodejs) is a library that allows a user to create a node-based processing pipeline for any type of data. These nodes aim to be composable and modular, allowing for a wide variety of use cases. However, the nodes are also strongly typed, allowing for type-checking and type inference. This library is written in pure Typescript and is intended to be used throughout the rest of the project.

**Status:** A prototype is completed and stored at `libraries/libnode`.

### libimage

`libimage` is a library for image processing. It provides basic image primitives, like colors, curves, and image buffers. It also provides basic functionality for acting on these primitives, like blurring, sharpening, compositing and color correction. This library is written in pure Typescript and is intended to be used throughout the rest of the project.

**Status:** Not started.

### libpictonode

`libpictonode` combines the functionality of `libimage` and `libnode` to provide a node-based image processing pipeline. It provides a set of nodes that can be used to create a processing pipeline. This library is written in pure Typescript and is intended to be used throughout the rest of the project.

**Status:** Not started.

### node-editor

`node-editor` is a library that provides a user interface for creating and editing node-based processing pipelines. It implements wrappers around `libnode` such as color and position that allow it to be visualized and rendered in the browser. It is written in DOM-enabled Typescript and is intended to be used in browser environments. 

**Status:** Not started.

### website-backend

`website-backend` is a binary that hosts a website that allows users to create and edit node-based processing pipelines. It can be written in anything; current preference is to use Node.js-enabled Typescript using express-js.

**Status:** Not started.

### website-frontend

`website-frontend` is a binary that integrates `node-editor` and `libpictonode` together to create a node-based image editor. It is written in DOM-enabled Typescript and is intended to be used in browser environments.

**Status:** Not started.

### photoshop-plugin

`photoshop-plugin` is a binary that integrates `node-editor` and `libpictonode` together to create a node-based image editor integrated into Photostop. It is written in whatever form of JS/TS that Photoshop accepts.

**Status:** Not started.

### native-app (Nice To Have)

`native-app` is a binary that integrates `node-editor` and `libpictonode` together to create a node-based image editor hosted on the native desktop using Electron. It is written in DOM-enabled Typescript and is intended to be used in browser environments.

**Status:** Not started.

### gimp-plugin (Nice To Have)

`gimp-plugin` is a binary that integrates `node-editor` and `libpictonode` together to create a node-based image editor integrated into GIMP. It is written in C that calls back to a Typescript library.