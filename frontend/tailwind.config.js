/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        // Deep ink navy -- the page's base, not a neutral gray/black.
        ink: {
          950: "#0F1830",
          900: "#14213D",
          800: "#1C2D4F",
          700: "#28406C",
        },
        // Ledger paper -- used for cards and surfaces, never full-bleed.
        paper: {
          50: "#FBF8F0",
          100: "#F1E9D8",
          200: "#E6D9BE",
        },
        // Ink-on-paper text.
        inktext: "#2B2118",
        // Stamp-pad accents -- muted, not neon.
        seal: {
          green: "#2F6E4F",
          amber: "#B8863B",
          grey: "#6B655A",
          red: "#9C3D3D",
          teal: "#1F5C6B",
        },
      },
      fontFamily: {
        display: ["Fraunces", "serif"],
        body: ["IBM Plex Sans", "system-ui", "sans-serif"],
        mono: ["IBM Plex Mono", "monospace"],
      },
      borderRadius: {
        card: "6px",
      },
    },
  },
  plugins: [],
};
