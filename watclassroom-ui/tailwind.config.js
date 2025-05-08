/** @type {import('tailwindcss').Config} */
module.exports = {
  // NOTE: Update this to include the paths to all of your component files.
  content: ["./app/**/*.{js,jsx,ts,tsx}"],
  presets: [require("nativewind/preset")],
  theme: {
    extend: {
      colors: {
        back: "#222831",
        element: "#393E46",
        default: "#EEEEEE",
        heading: "#00ADB5"
      }
    },
  },
  plugins: [],
}