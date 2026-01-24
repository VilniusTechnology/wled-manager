/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#3B82F6', // Blue 500
          dark: '#2563EB', // Blue 600
          light: '#60A5FA', // Blue 400
        },
        success: {
          DEFAULT: '#10B981', // Green 500
          dark: '#059669', // Green 600
          light: '#34D399', // Green 400
        },
        danger: {
          DEFAULT: '#EF4444', // Red 500
          dark: '#DC2626', // Red 600
          light: '#F87171', // Red 400
        },
        warning: {
          DEFAULT: '#F59E0B', // Amber 500
          dark: '#D97706', // Amber 600
          light: '#FBBF24', // Amber 400
        },
        info: {
          DEFAULT: '#3B82F6', // Blue 500
          dark: '#2563EB', // Blue 600
          light: '#60A5FA', // Blue 400
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      }
    },
  },
  plugins: [
    require('@tailwindcss/typography'),
  ],
}
