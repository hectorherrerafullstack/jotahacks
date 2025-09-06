/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./templates/**/*.html",
    "./**/templates/**/*.html",   // si tienes apps con plantillas propias
    "./static/js/**/*.js"
  ],
  theme: { extend: {} },
  plugins: [],
  safelist: [
    // Clases que activas por JS en el menú:
    "opacity-0","opacity-100","pointer-events-none",
    "translate-x-0","translate-x-2",
    // Arbitrary values del hero y layout:
    "w-screen","left-1/2","right-1/2","-ml-[50vw]","-mr-[50vw]","-mt-10",
    "origin-top-right"
  ]
};
