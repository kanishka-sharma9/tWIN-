import { fileURLToPath } from "node:url";
import tailwindcss from "@tailwindcss/vite";
import react from "@vitejs/plugin-react";
import { defineConfig } from "vitest/config";

export default defineConfig({
	plugins: [react(), tailwindcss()],
	resolve: {
		alias: { "@": fileURLToPath(new URL("./src", import.meta.url)) },
	},
	server: {
		port: 5173,
		// `/api` goes to the backend, so development needs no CORS setup.
		// The object form keeps the browser's Host header (the string form rewrites it), which the
		// API's CSRF check compares with `Origin` on the refresh and logout routes.
		proxy: { "/api": { target: "http://127.0.0.1:8000" } },
	},
	test: {
		environment: "jsdom",
		setupFiles: ["./src/test/setup.ts"],
		include: ["src/**/*.test.{ts,tsx}"],
	},
});
