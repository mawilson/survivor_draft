/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./survive/templates/survive/*.html", "./static_collected/survive/*.js", "./survive/static/survive/*.js"],
  theme: {
    extend: {
      colors: {
        'survivor-blue': '#439BA6',
      },
    },
  },
  plugins: [],
}

