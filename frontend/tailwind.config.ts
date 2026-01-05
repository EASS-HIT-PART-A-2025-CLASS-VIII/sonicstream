import type { Config } from "tailwindcss";

const config: Config = {
    darkMode: "class",
    plugins: [],
    content: [
        "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
        "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
        "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
    ],
    theme: {
        extend: {
            colors: {
                background: '#0a0a0a',
                foreground: '#ededed',
                primary: {
                    DEFAULT: '#1ed760',
                    foreground: '#000000',
                    hover: '#1fdf64'
                },
                card: {
                    DEFAULT: '#181818',
                    foreground: '#ededed'
                },
                popover: {
                    DEFAULT: '#121212',
                    foreground: '#ededed'
                },
                muted: {
                    DEFAULT: '#282828',
                    foreground: '#a7a7a7'
                },
                accent: {
                    DEFAULT: '#282828',
                    foreground: '#ededed'
                },
                destructive: {
                    DEFAULT: '#e91e63',
                    foreground: '#ededed'
                },
                border: '#282828',
                input: '#282828',
                ring: '#1ed760',
            },
            borderRadius: {
                lg: 'var(--radius)',
                md: 'calc(var(--radius) - 2px)',
                sm: 'calc(var(--radius) - 4px)'
            },
            keyframes: {
                "accordion-down": {
                    from: { height: "0" },
                    to: { height: "var(--radix-accordion-content-height)" },
                },
                "accordion-up": {
                    from: { height: "var(--radix-accordion-content-height)" },
                    to: { height: "0" },
                },
            },
            animation: {
                "accordion-down": "accordion-down 0.2s ease-out",
                "accordion-up": "accordion-up 0.2s ease-out",
            },
        }
    },
};
export default config;
