/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{html,ts}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      fontFamily: {
        sans: ['Plus Jakarta Sans', 'Inter', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'sans-serif'],
        serif: ['Source Serif 4', 'Newsreader', 'Georgia', 'serif'],
        mono: ['JetBrains Mono', 'Roboto Mono', 'ui-monospace', 'monospace'],
      },
      colors: {
        anthropic: {
          terracotta: '#D97757',
          'terracotta-hover': '#C16446',
          clay: '#CC785C',
          cream: '#FAF8F5',
          warm: '#F1ECE4',
        },
        google: {
          blue: '#8AB4F8',
          'blue-hover': '#ADC6FF',
          dark: '#131314',
          surface: '#1E1F20',
          elevated: '#282A2D',
          border: '#2E3135',
          'border-subtle': '#24262A',
        },
        neutral: {
          950: '#131314',
          900: '#1E1F20',
          850: '#24262A',
          800: '#282A2D',
          700: '#3C4043',
          600: '#5F6368',
          500: '#80868B',
          400: '#9AA0A6',
          300: '#BDC1C6',
          200: '#E3E3E3',
          100: '#F1F3F4',
        }
      }
    },
  },
  plugins: [],
}
