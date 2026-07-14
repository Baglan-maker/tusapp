module.exports = function (api) {
  api.cache(true);
  return {
    presets: ['babel-preset-expo'],
    // Reanimated 4 moved its babel plugin into react-native-worklets.
    // It must stay LAST in the plugin list.
    plugins: ['react-native-worklets/plugin'],
  };
};
