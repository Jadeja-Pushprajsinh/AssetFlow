/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        teal: {
          DEFAULT: '#008080',
          dark:    '#006666',
          darker:  '#00796b',
          light:   '#aeeeee',
          lighter: '#b2ebf2',
        },
        surface: '#f5f5f5',
        ink:     '#333333',
      },
      fontFamily: {
        sans: ['Montserrat', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
