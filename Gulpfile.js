// GNU AGPL v3 License
// Written By: John Nunley

// Manages the "Gulp" utility for the project, and provides a simple CLI interface
// for reformatting, testing, compiling etc etc

const { join } = require("path");
const { src, dest, parallel } = require("gulp");
const { spawn } = require("child_process");
const { Transform } = require("stream");

const prettier = require("prettier");

// Paths for pure TS projects.
const PURE = [
  "libraries/libnode"
]

// Paths for TS projects expected to be run on a web platform.
// These projects may also contain .vue files.
const WEB = [
  "frontend/pictonode-web"
]

// Paths for TS projects expected to be run on a NodeJS platform.
const NODE = [
  "backend/pictodaemon"
]

// Paths for Python projects.
const PYTHON = [
  "gimp/pictonode-gimp-plugin"
]

// Paths for all TS projects.
const TS = [...PURE, ...WEB, ...NODE]

/**
 * Runs prettier on all files in the project.
 */
const tfPrettier = parallel(...TS.map(name => named(`prettier_${name}`, runPrettier(name))));

/**
 * Checks formatting on all files in the project.
 */
const tfPrettierCheck = parallel(...TS.map(name => named(`prettier_check_${name}`, prettierCheck(name))));

/**
 * Runs npx webpack for all web projects.
 */
const tfNpxWebpack = parallel(...WEB.map(name => named(`webpack_${name}`, runNpxWebpack(name))));

/**
 * Runs mocha for all tests in the project.
 */
const tfMocha = parallel(...TS.map(name => named(`mocha_${name}`, runMocha(name))));

/**
 * Assign an arbitrary name to an anonymous function.
 * @param {string} name The name to assign to the function. 
 * @param {Function} fn The function to name.
 * @returns {Function} The function with the given name.
 */
function named(name, fn) {
  // Sanitize the name.
  name = name.replace(/[^a-zA-Z0-9_]/g, "_");

  return new Function("fn", `return function ${name}() { return fn.apply(this, arguments); }`)(fn);
}

/**
 * Creates a stream that runs prettier on every provided file.
 * @returns {() => Transform} A stream that runs prettier on every provided file.
 */
function runPrettier(path) {
  class PrettierTransform extends Transform {
    constructor(options) {
      super({
        objectMode: true,
        ...options
      });
    }

    _transform(file, _, callback) {
      // Get the config for the file.
      prettier.resolveConfig(file.path).then(config => {
        // Format the file.
        const unformatted = file.contents.toString("utf8");
        let formatted;
        try {
          formatted = prettier.format(unformatted, {
            filepath: file.path,
            ...config,
          });
          console.log(`Formatted ${file.path} with Prettier.`)
        } catch(err) {
          // Emit the error.
          this.emit("error", err);
          callback();
          return;
        }
        file.contents = Buffer.from(formatted, "utf8");

        // Push this file.
        this.push(file);
        callback();
      }).catch(err => {
        // Emit the error.
        this.emit("error", err);
      })
    }
  }

  return () => src(join(path, "**/*.{ts,js,vue}"))
    .pipe(new PrettierTransform())
    .pipe(dest(path));
}

/**
 * Creates a stream that checks formatting on every provided file.
 * @param {string} path The path to the folder to check.
 * @returns {() => Transform} A stream that checks formatting on every provided file. 
 */
function prettierCheck(path) {
  class PrettierCheckTransform extends Transform {
    constructor(options) {
      super({
        objectMode: true,
        ...options
      });

      this.unformattedFiles = [];
    }

    _transform(file, _, callback) {
      // Get the config for the file.
      prettier.resolveConfig(file.path).then(config => {
        // See if the file is formatted.
        const unformatted = file.contents.toString("utf8");
        let isFormatted;
        try {
          isFormatted = prettier.check(unformatted, {
            filepath: file.path,
            ...config,
          });

          if (!isFormatted) {
            this.unformattedFiles.push(file.path);
          }
        } catch(err) {
          // Emit the error.
          this.emit("error", err);
          callback();
          return;
        }

        // Push this file.
        this.push(file);
        callback();
      }).catch(err => {
        // Emit the error.
        this.emit("error", err);
        callback();
      })
    }

    _flush(callback) {
      if (this.unformattedFiles.length > 0) {
        this.emit("error", new Error(`The following files are not formatted:\n${this.unformattedFiles.join("\n")}`));
      }

      callback();
    }
  }

  return () => src(join(path, "src/**/*.{ts,vue,js}"))
    .pipe(new PrettierCheckTransform())
    .pipe(dest(join(path, "src")));
}

/**
 * Runs mocha on a given path.
 * @param {string} path The path to run mocha on.
 */
function runMocha(path) {
  // Run mocha as a child process.
  return () => {
    const tsNodePath = require.resolve("ts-node/register");

    const args = [
      "mocha",
      "--recursive",
      "-r",
      tsNodePath,
      '"tests/**/*.ts"'
    ]

    const compilerOptions = {
      module: "commonjs",
    }

    const extraEnv = {
      TS_NODE_COMPILER_OPTIONS: JSON.stringify(compilerOptions),
    }

    const pr = spawn("npx", args, {
      cwd: join(__dirname, path),
      env: {
        ...extraEnv,
        ...process.env,
      }
    })

    pr.stdout.pipe(process.stdout);
    pr.stderr.pipe(process.stderr);

    return pr
  }
}

/**
 * Run npm ci on a given path.
 * @param {string} path The path to run npm ci on.
 */
function runNpmCi(path) {
  return () => spawn("npm", ["ci"], {
    cwd: join(__dirname, path),
  })
}

/**
 * Run npx webpack on a given path.
 * @param{string} path The path to run npx webpack on
 */
function runNpxWebpack(path) {
  return () => spawn("npx", ["webpack"], {
    cwd: join(__dirname, path)
  })
}

module.exports = {
  format: tfPrettier,
  "format-check": tfPrettierCheck,
  mocha: tfMocha,
  webpack: tfNpxWebpack,
};
