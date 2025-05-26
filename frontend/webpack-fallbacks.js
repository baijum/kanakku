const webpack = require('webpack');
const path = require('path');

module.exports = function override(config) {
  // Add resolve extensions to handle ESM modules
  config.resolve.extensions = [...(config.resolve.extensions || []), '.js', '.mjs'];

  // Add fallbacks for node modules
  config.resolve.fallback = {
    ...config.resolve.fallback, // Keep any existing fallbacks
    "http": require.resolve("stream-http"),
    "https": require.resolve("https-browserify"),
    "stream": require.resolve("stream-browserify"),
    "buffer": require.resolve("buffer/"),
    "util": require.resolve("util/"),
    "url": require.resolve("url/"),
    "process": false,
    "zlib": require.resolve("browserify-zlib"),
    "assert": require.resolve("assert/"),
    "crypto": require.resolve("crypto-browserify"),
    "path": require.resolve("path-browserify"),
    "querystring": require.resolve("querystring-es3"),
    "fs": false,
    "os": require.resolve("os-browserify/browser"),
  };

  // Add module alias for process/browser
  config.resolve.alias = {
    ...config.resolve.alias,
    "process/browser": "process/browser.js"
  };

  // Add plugins to provide Buffer and process
  config.plugins.push(
    new webpack.ProvidePlugin({
      process: require.resolve("process/browser"),
      Buffer: ['buffer', 'Buffer'],
    })
  );

  return config;
};
