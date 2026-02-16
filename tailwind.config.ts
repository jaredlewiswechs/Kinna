import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: [
          "-apple-system",
          "BlinkMacSystemFont",
          "SF Pro Display",
          "SF Pro Text",
          "Helvetica Neue",
          "Helvetica",
          "Arial",
          "sans-serif",
        ],
        mono: [
          "SF Mono",
          "SFMono-Regular",
          "ui-monospace",
          "Menlo",
          "monospace",
        ],
      },
      colors: {
        accent: {
          DEFAULT: "#007AFF",
          hover: "#0066D6",
        },
        surface: {
          primary: "#FFFFFF",
          secondary: "#F2F2F7",
          tertiary: "#E5E5EA",
        },
        label: {
          primary: "#000000",
          secondary: "#3C3C43",
          tertiary: "#48484A",
          quaternary: "#636366",
        },
        separator: "#C6C6C8",
        congruent: "#34C759",
        suspect: "#FF9500",
        conflict: "#FF3B30",
      },
      borderRadius: {
        xl: "12px",
        "2xl": "16px",
        "3xl": "20px",
      },
    },
  },
  plugins: [],
};

export default config;
