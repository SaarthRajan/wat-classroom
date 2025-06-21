/** @type {import('tailwindcss').Config} */
module.exports = {
  // NOTE: Update this to include the paths to all of your component files.
  content: ["./app/**/*.{js,jsx,ts,tsx}"],
  presets: [require("nativewind/preset")],
  theme: {
    extend: {
      colors: {
        back: "#000000",
        element: "#787878",
        default: "#FFFFFF",
        heading: "#EAAB00"
      },
      fontFamily: {
        heading: ['"Roboto Condensed"', '"HelveticaNeue-CondensedBold"', '"sans-serif-condensed"', 'sans-serif'],
        body: ['Georgia', 'serif'],
        ui: ['Verdana', 'sans-serif'],
      },
    },
  },
  plugins: [],
}