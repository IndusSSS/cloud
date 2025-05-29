// postcss.config.cjs
module.exports = {
  plugins: {
    // Use the extracted PostCSS plugin
    '@tailwindcss/postcss': {},
    // Then autoprefixer
    autoprefixer: {},
  },
};
