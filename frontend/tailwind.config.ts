import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        brand: {
          navy: "#0F1D2A",
          deep: "#0B1622",
          accent: "#0E8C74",
          bright: "#1ABC9C",
          surface: "#FAFAF9",
          muted: "#F2F0ED",
          line: "#E8E6E3",
        },
      },
      fontFamily: {
        display: ["var(--font-display)", "system-ui", "sans-serif"],
      },
    },
  },
  plugins: [],
};

export default config;
