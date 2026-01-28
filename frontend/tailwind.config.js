/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{vue,js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                gray: {
                    950: '#0a0b10',
                    900: '#1a1b26',
                    800: '#24283b',
                    700: '#414868',
                }
            }
        },
    },
    plugins: [],
}
