/** @type {import('tailwindcss').Config} */
module.exports = {
  // Configura las rutas para que Tailwind escanee tus plantillas
  content: [
    "./templates/**/*.html",
    "./**/templates/**/*.html",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
