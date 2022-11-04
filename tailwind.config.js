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
  plugins: [ require('@tailwindcss/forms'),require('flowbite/plugin'), require('flowbite-typography')],
}
