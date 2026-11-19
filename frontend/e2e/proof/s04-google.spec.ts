import { expect, type Page, test } from "@playwright/test";

// E02-S04 proof through Swagger UI. The API started here has no Google settings, so this
// covers the "not configured" paths and that email + password still works. The configured
// flow is proven by the pytest suite with a fake IdentityProvider; real Google is not exercised.
const DOCS = "http://127.0.0.1:8000/docs";

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
	return { op, live };
}

test.beforeEach(async ({ page }) => {
	await page.goto(DOCS);
	await expect(page.locator(".swagger-ui .info")).toBeVisible();
});

test("providers reports Google off when it is not configured", async ({
	page,
}) => {
	const { live } = await execute(page, "get", "/api/auth/providers");
	await expect(live.locator("tbody .response-col_status").first()).toHaveText(
		/200/,
	);
	await expect(live).toContainText('"google": false');
	await page.screenshot({ path: "e2e/test-results/s04-providers-off.png" });
});

test("google start answers 404 provider_disabled when not configured", async ({
	page,
}) => {
	const { live } = await execute(page, "get", "/api/auth/google/start");
	await expect(live.locator("tbody .response-col_status").first()).toHaveText(
		/404/,
	);
	await expect(live).toContainText("provider_disabled");
	await page.screenshot({ path: "e2e/test-results/s04-start-404.png" });
});

test("google callback answers 404 provider_disabled when not configured", async ({
	page,
}) => {
	const { live } = await execute(page, "get", "/api/auth/google/callback");
	await expect(live.locator("tbody .response-col_status").first()).toHaveText(
		/404/,
	);
	await expect(live).toContainText("provider_disabled");
	await page.screenshot({ path: "e2e/test-results/s04-callback-404.png" });
});

test("email and password sign-up still works with Google off", async ({
	page,
}) => {
	const email = `proof-${Date.now()}@example.com`;
	const body = JSON.stringify({ email, password: "S3cret-passphrase-Zq9" });
	const { live } = await execute(page, "post", "/api/auth/signup", body);
	await expect(live.locator("tbody .response-col_status").first()).toHaveText(
		/201/,
	);
	await expect(live).toContainText('"has_password": true');
	await page.screenshot({ path: "e2e/test-results/s04-signup-works.png" });
});
