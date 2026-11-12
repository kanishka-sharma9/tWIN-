import { defineConfig, devices } from "@playwright/test";

// Browsers: Chromium, Firefox and WebKit (D-044); WebKit stands in for Safari.
// Each runs at desktop (1280x800) and phone (iPhone 14 preset, 390x844) widths (D-043).
const { defaultBrowserType: _ignored, ...iphone } = devices["iPhone 14"];
const desktop = { viewport: { width: 1280, height: 800 } };

// `npm run e2e:full` also starts the database and the API; otherwise they must already be running.
const full = Boolean(process.env.E2E_FULL);

export default defineConfig({
	testDir: "./e2e",
	outputDir: "./e2e/test-results",
	fullyParallel: true,
	forbidOnly: Boolean(process.env.CI),
	reporter: [["list"]],
	use: { baseURL: "http://localhost:5173" },
	projects: [
		{
			name: "chromium-desktop",
			use: { ...devices["Desktop Chrome"], ...desktop },
		},
		{
			name: "chromium-phone",
			use: { ...iphone, browserName: "chromium" },
		},
		{
			name: "firefox-desktop",
			use: { ...devices["Desktop Firefox"], ...desktop },
		},
		{
			// Firefox does not support mobile emulation, so only the viewport and touch carry over.
			name: "firefox-phone",
			use: { ...iphone, browserName: "firefox", isMobile: false },
		},
		{
			name: "webkit-desktop",
			use: { ...devices["Desktop Safari"], ...desktop },
		},
		{
			name: "webkit-phone",
			use: { ...iphone, browserName: "webkit" },
		},
	],
	webServer: [
		{
			command: "npm run dev",
			url: "http://localhost:5173",
			reuseExistingServer: true,
		},
		...(full
			? [
					{
						command:
							"cd ../backend && uv run alembic upgrade head && uv run twin",
						url: "http://127.0.0.1:8000/api/health",
						reuseExistingServer: true,
					},
				]
			: []),
	],
});
