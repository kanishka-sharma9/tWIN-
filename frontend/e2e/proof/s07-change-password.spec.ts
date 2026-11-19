import { expect, type Locator, type Page, test } from "@playwright/test";

// E02-S07 proof through Swagger UI: log in, send the bearer token, change the password
// (204), try a wrong current password (401), then log in with the new password and
// confirm the old one is refused.
const API = "http://127.0.0.1:8000";
const OLD = "S3cret-passphrase-Zq9";
const NEW = "A brand new passphrase 42";

test.describe.configure({ mode: "serial" }); // one flow, shared account

function op(page: Page, method: string, path: string): Locator {
	return page.locator(`.opblock-${method}`).filter({
		has: page.locator(`[data-path="${path}"]`),
	});
}

const opened = new Set<string>();

async function open(op: Locator, key: string) {
	if (opened.has(key)) return;
	opened.add(key);
	await op.locator(".opblock-summary").click();
	await op.getByRole("button", { name: "Try it out" }).click();
}

async function run(op: Locator, key: string, body: object): Promise<Locator> {
	await open(op, key);
	await op
		.locator("textarea.body-param__text")
		.fill(JSON.stringify(body, null, 2));
	await op.getByRole("button", { name: "Execute" }).click();
	const live = op.locator(".live-responses-table");
	await expect(live).toBeVisible();
	await live.scrollIntoViewIfNeeded();
	return live;
}

const status = (live: Locator) =>
	live.locator("tbody .response-col_status").first();

test("change password through Swagger UI", async ({ page }) => {
	const email = `proof-s07-${Date.now()}@example.com`;
	await page.goto(`${API}/docs`);
	await expect(page.locator(".swagger-ui .info")).toBeVisible();

	const signup = op(page, "post", "/api/auth/signup");
	const signupLive = await run(signup, "signup", { email, password: OLD });
	await expect(status(signupLive)).toHaveText(/201/);
	await page.screenshot({ path: "e2e/test-results/s07-1-signup.png" });

	const login = op(page, "post", "/api/auth/login");
	const loginLive = await run(login, "login", { email, password: OLD });
	await expect(status(loginLive)).toHaveText(/200/);
	await page.screenshot({ path: "e2e/test-results/s07-2-login.png" });
	const text = await loginLive.locator(".microlight").first().textContent();
	const token = (JSON.parse(text ?? "") as { access_token: string }).access_token;
	expect(token.length).toBeGreaterThan(20);

	// Authorize: Swagger UI adds "Bearer " itself; the field takes the bare token.
	await page.locator("button.authorize").click();
	await page.locator(".auth-container input[type=text]").fill(token);
	await page.locator(".modal-ux button.modal-btn.authorize").click();
	await page.screenshot({ path: "e2e/test-results/s07-2b-authorized.png" });
	await page.locator(".modal-ux button.btn-done").click();

	const change = op(page, "post", "/api/auth/change-password");
	const wrong = await run(change, "change", {
		current_password: "not the password!",
		new_password: NEW,
	});
	await expect(status(wrong)).toHaveText(/401/);
	await expect(wrong).toContainText("wrong_password");
	await page.screenshot({ path: "e2e/test-results/s07-3-wrong-current.png" });

	const weak = await run(change, "change", {
		current_password: OLD,
		new_password: "short",
	});
	await expect(status(weak)).toHaveText(/422/);
	await expect(weak).toContainText("weak_password");
	await page.screenshot({ path: "e2e/test-results/s07-4-weak.png" });

	const ok = await run(change, "change", {
		current_password: OLD,
		new_password: NEW,
	});
	await expect(status(ok)).toHaveText(/204/);
	await page.screenshot({ path: "e2e/test-results/s07-5-changed.png" });

	const oldLogin = await run(login, "login", { email, password: OLD });
	await expect(status(oldLogin)).toHaveText(/401/);
	await expect(oldLogin).toContainText("invalid_credentials");
	await page.screenshot({ path: "e2e/test-results/s07-6-old-refused.png" });

	const newLogin = await run(login, "login", { email, password: NEW });
	await expect(status(newLogin)).toHaveText(/200/);
	await page.screenshot({ path: "e2e/test-results/s07-7-new-login.png" });
});
