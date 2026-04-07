import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        brand: {
          navy: "#1e293b",
          accent: "#0d9488",
          surface: "#f8fafc",
          muted: "#f1f5f9",
        },
      },
    },
  },
  plugins: [],
};

export default config;
