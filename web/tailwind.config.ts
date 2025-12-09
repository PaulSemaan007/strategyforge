import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        'blue-force': '#3B82F6',
        'red-force': '#EF4444',
        'neutral': '#6B7280',
      },
    },
  },
  plugins: [],
}
export default config
