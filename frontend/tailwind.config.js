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
        amber: {
          DEFAULT: '#f59e0b', // Used for Under Maintenance (text/icon)
          light:   '#fef3c7', // Used for Under Maintenance pill bg
        },
        red: {
          DEFAULT: '#ef4444', // Used for Lost (text/icon)
          light:   '#fee2e2', // Used for Lost pill bg
        },
      },
      fontFamily: {
        sans: ['Montserrat', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
