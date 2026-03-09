/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./src/**/*.{js,jsx,ts,tsx}"],
  theme: {
    extend: {
      colors: {
        glass: {
          light: "rgba(255, 255, 255, 0.15)",
          medium: "rgba(255, 255, 255, 0.25)",
          heavy: "rgba(255, 255, 255, 0.35)",
          dark: "rgba(0, 0, 0, 0.25)",
        },
      },
      backdropBlur: {
        glass: "16px",
      },
      boxShadow: {
        glass: "0 8px 32px 0 rgba(31, 38, 135, 0.18)",
        "glass-sm": "0 4px 16px 0 rgba(31, 38, 135, 0.12)",
        "glass-inset": "inset 0 1px 0 rgba(255, 255, 255, 0.15)",
      },
      borderColor: {
        glass: "rgba(255, 255, 255, 0.18)",
      },
    },
  },
  plugins: [],
};

