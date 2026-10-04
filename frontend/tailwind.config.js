/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        paper: "#FBFCFE",
        ink: { DEFAULT: "#1E2A44", soft: "#46536E", faint: "#8792A8" },
        rule: "#DCE3EE",
        grid: "#E9EEF5",
        marker: { DEFAULT: "#F5D547", soft: "#FBEFB0" },
        mastery: { DEFAULT: "#2E8B6E", soft: "#D5EEE5" },
        revise: { DEFAULT: "#B83A4B", soft: "#F6DDE0" },
        progress: { DEFAULT: "#3A63B8", soft: "#DCE5F7" },
      },
      fontFamily: {
        display: ['"Bricolage Grotesque"', "system-ui", "sans-serif"],
        sans: ['"Atkinson Hyperlegible"', "system-ui", "sans-serif"],
        mono: ['"JetBrains Mono"', "ui-monospace", "monospace"],
      },
      boxShadow: { card: "0 1px 0 #DCE3EE, 0 1px 3px rgba(30,42,68,0.05)" },
    },
  },
  plugins: [],
};
