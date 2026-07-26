export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        brand: {
          50: "#EFF6FF",
          100: "#DBEAFE",
          500: "#2563EB",
          600: "#1D4ED8",
          700: "#1E40AF",
        },
        accent: {
          500: "#10B981",
          600: "#059669",
        },
      },
      boxShadow: {
        soft: "0 24px 60px rgba(15, 23, 42, 0.08)",
        lift: "0 18px 40px rgba(37, 99, 235, 0.12)",
      },
      keyframes: {
        fadeUp: {
          "0%": { opacity: 0, transform: "translateY(14px)" },
          "100%": { opacity: 1, transform: "translateY(0)" },
        },
        pulseSoft: {
          "0%, 100%": { transform: "scale(1)", opacity: 1 },
          "50%": { transform: "scale(0.94)", opacity: 0.72 },
        },
      },
      animation: {
        fadeUp: "fadeUp 0.55s ease-out both",
        pulseSoft: "pulseSoft 1.2s ease-in-out infinite",
      },
    },
  },
  plugins: [],
};
