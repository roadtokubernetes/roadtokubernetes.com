/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: 'class',
  content: [
    './src/templates/*.html', 
    './src/**/**/*.html', 
    './node_modules/flowbite/**/*.js', 
    'src/static/src/**/*.js'],
  theme: {
    extend: {},
  },
  plugins: [ require('flowbite/plugin'), require('flowbite-typography')],
}
