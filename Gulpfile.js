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
const tfPrettier = parallel(...TS.map(runPrettier));

/**
 * Checks formatting on all files in the project.
 */
const tfPrettierCheck = parallel(...TS.map(prettierCheck));

/**
 * Runs npm ci on all projects.
 */
const tfNpmCi = parallel(...TS.map(runNpmCi));

/**
 * 
 */

/**
 * Runs webpack on the pictonode-web-frontend.
 */
function tfWebpack() {
  // Run webpack as a child process.
  return spawn("npx", ["webpack"], {
    cwd: join(__dirname, "frontend/pictonode-web"),
  })
}

/**
 * Runs mocha for all tests in the project.
 */
const tfMocha = parallel(...TS.map(runMocha));

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

  return () => src(join(path, "**/*.ts"))
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

  return () => src(join(path, "src/**/*.ts"))
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

module.exports = {
  format: tfPrettier,
  "format-check": tfPrettierCheck,
  webpack: tfWebpack,
  mocha: tfMocha,
  "npm-ci": tfNpmCi,
};
