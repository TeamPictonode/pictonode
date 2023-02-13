// GNU AGPL v3.0
// Written by John Nunley

// Setup webpack to compile to a single file
const path = require('path');

const mode = process.env.NODE_ENV || 'development';

module.exports = {
  entry: './src/index.ts',
  target: 'node',
  mode,
  devtool: false,
  module: {
    rules: [
      {
        test: /\.tsx?$/,
        use: 'ts-loader',
        //exclude: /node_modules/,
      },
    ],
  },
  externals: {
    "sharp": "sharp",
    "express": "express",
    "pg": "pg",
    "fs": "fs",
    "path": "path",
    "os": "os"
  },
  resolve: {
    extensions: [ '.tsx', '.ts', '.js' ],
  },
  output: {
    filename: 'index.js',
    path: path.resolve(__dirname, 'dist'),
  },
};
