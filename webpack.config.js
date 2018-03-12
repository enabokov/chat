const path = require("path");
const CopyPlugin = require('copy-webpack-plugin');
const ExtractTextPlugin = require("extract-text-webpack-plugin");
const webpack = require('webpack');

function makeConfig({
  js: { input: jsInput, output: jsOutput, vendorOutput },
  css: { input: cssInput, output: cssOutput },
  copy
}) {
    return {
      entry: {
          app: [jsInput, cssInput],
      },
      output: {
        path: path.resolve(__dirname + "/service/static/public/"),
        filename: jsOutput,
      },
      module: {
        rules: [
          {
            test: /\.css$/,
            use: ExtractTextPlugin.extract({
              use: [
                {
                  loader: 'css-loader',
                  options: {
                    url: false,
                    import: false,
                    minimize: true,
                  },
                }
              ],
            }),
          },

          {
            test: /\.js$/,
            exclude: /node_modules/,
            loader: 'babel-loader',
            options: {
              presets: ['es2015'],
            },
          },
        ]
      },
      plugins: [
        new webpack.ProvidePlugin({
          $: 'jquery',
          jQuery: 'jquery',
          'window.jQuery': 'jquery',
          Popper: ['popper.js', 'default'],
        }),

        new ExtractTextPlugin({
          filename: cssOutput,
          allChunks: true,
        }),

        new CopyPlugin(copy),

        new webpack.optimize.CommonsChunkPlugin({
          name: 'vendor',
          filename: vendorOutput,
          minChunks: function(module, count) {
            console.log(count);
            return /node_modules/.test(module.resource);
          },
        }),
      ],
    }
}

const appConfig = makeConfig({
  js: {
    "input": "./service/static/js/index.js",
    "output": "./js/app.js",
    "vendorOutput": './js/vendor.js',
  },
  css: {
    "input": "./service/static/css/index.css",
    "output": "./css/base.css"
  },
  copy: [
    { from: "./node_modules/bootstrap/dist/css/bootstrap.min.css", to: "./css/bootstrap.min.css" },
    { from: './node_modules/bootstrap/dist/fonts', to: './fonts' },
  ],
});

module.exports = appConfig;
