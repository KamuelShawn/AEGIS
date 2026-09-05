import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        graphite: {
          950: "#0b0d0c",
          900: "#121513",
          800: "#1b201d",
          700: "#262c28",
          600: "#333b35",
          500: "#4a544c",
        },
        earth: {
          100: "#f4f2ec",
          200: "#e9e5da",
          300: "#d8d1bf",
        },
        sustaina: {
          green: "#4c8c5a",
          "green-dim": "#2e4a34",
          blue: "#3f7ea6",
          "blue-dim": "#274a5e",
          amber: "#c98a34",
          red: "#b1443a",
        },
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
      },
      animation: {
        "pulse-slow": "pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite",
      },
    },
  },
  plugins: [],
};
export default config;
