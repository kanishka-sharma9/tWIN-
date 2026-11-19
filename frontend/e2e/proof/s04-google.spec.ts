import { type ChildProcess, spawn } from "node:child_process";
import { expect, type Page, test } from "@playwright/test";

// E02-S04 proof through Swagger UI, in both states:
// - Google off: the API started by the Playwright config, which has no Google settings.
// - Google on: a second API on port 8001 started here with fake client values.
// Real Google is not exercised: the fake values only switch the feature on, and nobody
// completes a sign-in at Google. The branch logic is proven by the pytest suite.
const OFF = "http://127.0.0.1:8000";
const ON = "http://127.0.0.1:8001";

async function execute(
	page: Page,
	method: string,
	path: string,
	body?: string,
) {
	const op = page.locator(`.opblock-${method}`).filter({
		has: page.locator(`[data-path="${path}"]`),
	});
	await op.locator(".opblock-summary").click();
	await op.getByRole("button", { name: "Try it out" }).click();
	if (body !== undefined) {
		await op.locator("textarea.body-param__text").fill(body);
	}
	await op.getByRole("button", { name: "Execute" }).click();
	const live = op.locator(".live-responses-table");
	await expect(live).toBeVisible();
	await live.scrollIntoViewIfNeeded();
	return live;
}

async function openDocs(page: Page, base: string) {
	await page.goto(`${base}/docs`);
	await expect(page.locator(".swagger-ui .info")).toBeVisible();
}

const status = (live: ReturnType<Page["locator"]>) =>
	live.locator("tbody .response-col_status").first();

test.describe("Google not configured", () => {
	test.beforeEach(async ({ page }) => openDocs(page, OFF));

	test("providers reports Google off", async ({ page }) => {
		const live = await execute(page, "get", "/api/auth/providers");
		await expect(status(live)).toHaveText(/200/);
		await expect(live).toContainText('"google": false');
		await page.screenshot({ path: "e2e/test-results/s04-off-providers.png" });
	});

	test("google start answers 404 not_found", async ({ page }) => {
		const live = await execute(page, "get", "/api/auth/google/start");
		await expect(status(live)).toHaveText(/404/);
		await expect(live).toContainText("not_found");
		await page.screenshot({ path: "e2e/test-results/s04-off-start.png" });
	});

	test("google callback answers 404 not_found", async ({ page }) => {
		const live = await execute(page, "get", "/api/auth/google/callback");
		await expect(status(live)).toHaveText(/404/);
		await expect(live).toContainText("not_found");
		await page.screenshot({ path: "e2e/test-results/s04-off-callback.png" });
	});

	test("email and password sign-up still works", async ({ page }) => {
		const email = `proof-${Date.now()}@example.com`;
		const body = JSON.stringify({ email, password: "S3cret-passphrase-Zq9" });
		const live = await execute(page, "post", "/api/auth/signup", body);
		await expect(status(live)).toHaveText(/201/);
		await expect(live).toContainText('"has_password": true');
		await page.screenshot({ path: "e2e/test-results/s04-off-signup.png" });
	});
});

test.describe("Google configured with fake values", () => {
	test.describe.configure({ mode: "serial" }); // one API process for the group
	let api: ChildProcess;

	test.beforeAll(async () => {
		api = spawn("uv", ["run", "twin"], {
			cwd: "../backend",
			env: {
				...process.env,
				TWIN_PORT: "8001",
				TWIN_JWT_SECRET:
					process.env.TWIN_JWT_SECRET ??
					"factory-proof-throwaway-secret-0123456789",
				TWIN_GOOGLE_CLIENT_ID: "fake-client-id.apps.googleusercontent.com",
				TWIN_GOOGLE_CLIENT_SECRET: "fake-client-secret",
				TWIN_GOOGLE_REDIRECT_URI: `${ON}/api/auth/google/callback`,
			},
			stdio: "ignore",
		});
		await expect
			.poll(
				async () => {
					try {
						return (await fetch(`${ON}/api/health`)).status;
					} catch {
						return 0;
					}
				},
				{ timeout: 60_000 },
			)
			.toBe(200);
	});

	test.afterAll(() => {
		api.kill();
	});

	test.beforeEach(async ({ page }) => openDocs(page, ON));

	test("providers reports Google on", async ({ page }) => {
		const live = await execute(page, "get", "/api/auth/providers");
		await expect(status(live)).toHaveText(/200/);
		await expect(live).toContainText('"google": true');
		await page.screenshot({ path: "e2e/test-results/s04-on-providers.png" });
	});

	test("google start redirects to Google with state and an S256 challenge", async ({
		page,
		request,
	}) => {
		// Swagger UI's fetch follows the redirect and the browser blocks the cross-origin
		// result, so it shows the attempt; the redirect itself is read without following it.
		const live = await execute(page, "get", "/api/auth/google/start");
		await expect(live).toBeVisible();
		await page.screenshot({ path: "e2e/test-results/s04-on-start.png" });
		const response = await request.get(`${ON}/api/auth/google/start`, {
			maxRedirects: 0,
		});
		expect(response.status()).toBe(302);
		const location = new URL(response.headers().location as string);
		expect(location.host).toBe("accounts.google.com");
		expect(location.searchParams.get("code_challenge_method")).toBe("S256");
		expect(location.searchParams.get("state")).toBeTruthy();
		expect(location.searchParams.get("scope")).toBe("openid email");
		expect(location.href).not.toContain("fake-client-secret");
		expect(response.headers()["set-cookie"]).toContain("oauth_state=");
	});

	test("callback with a forged state goes back to login", async ({
		request,
	}) => {
		const response = await request.get(
			`${ON}/api/auth/google/callback?code=x&state=forged`,
			{ maxRedirects: 0 },
		);
		expect(response.status()).toBe(302);
		expect(response.headers().location).toBe("/login?error=google_failed");
	});
});
