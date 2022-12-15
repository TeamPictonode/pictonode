// GNU AGPL 3.0 License

// This file in its entirety was written by John Nunley and Grace Meredith.

const { join, resolve } = require("path");
const { VueLoaderPlugin } = require("vue-loader");
const { VuetifyPlugin } = require("webpack-plugin-vuetify");

const mode = "development";
const webpackConfig = {
    entry: "./src/index.ts",
    mode,
    module: {
        rules: [
            {
                test: /\.vue$/,
                loader: "vue-loader",
            },
            {
                test: /\.tsx?$/,
                loader: "ts-loader",
                //exclude: /node_modules/,
                options: { appendTsSuffixTo: [/\.vue$/ ] }
            },
            {
                test: /\.s[ac]ss$/i,
                use: [
                    "style-loader",
                    "css-loader",
                    "sass-loader",
                ]
            },
            {
                test: /\.css$/i,
                use: [
                    "style-loader",
                    "css-loader",
                ]
            }
        ]
    },
    resolve: {
        extensions: [".tsx", ".ts", ".js"]
    },
    externals: {
        "vue": "Vue",
        "vuetify": "Vuetify",
        "vue-router": "VueRouter",
    },
    output: {
        filename: "bundle.js",
        path: resolve(__dirname, "dist")
    },
    devServer: {
        static: [
            join(__dirname, "dist"),
            join(__dirname, "static"),
        ],
        compress: true,
        port: 8675,
    },
    plugins: [
        new VueLoaderPlugin(),
        new VuetifyPlugin({ autoImport: true }),
    ]
};

if (mode === "development") {
    webpackConfig.devtool = "inline-source-map";
}

module.exports = webpackConfig;