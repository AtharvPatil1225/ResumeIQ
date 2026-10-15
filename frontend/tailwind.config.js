export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: { ink: "#18243a", violet: { 50: "#f4f1ff", 100: "#e8e2ff", 500: "#7458e8", 600: "#6244d6", 700: "#5137bb" } },
      boxShadow: { card: "0 24px 70px rgba(35, 43, 78, 0.09)" },
    },
  },
  plugins: [],
};
