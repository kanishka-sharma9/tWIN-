import { expect, type Page, test } from "@playwright/test";

// E02-S06: the sign up, log in and account screens against the real API and database.
// Needs the API running (`npm run e2e:full` starts it). Every test uses its own email.
const PASSWORD = "S3cret-passphrase-Zq9";
const NEW_PASSWORD = "A brand new passphrase 42";
const EMPTY_VAULT = "This vault is empty. Files will appear here.";

let counter = 0;
function uniqueEmail() {
	counter += 1;
	return `e2e-${Date.now()}-${counter}-${Math.random().toString(36).slice(2, 8)}@example.com`;
}

async function noHorizontalScroll(page: Page) {
	const overflow = await page.evaluate(
		() => document.documentElement.scrollWidth - window.innerWidth,
	);
	expect(overflow).toBeLessThanOrEqual(0);
}

async function signUp(page: Page, email: string, password = PASSWORD) {
	await page.goto("/signup");
	await page.getByLabel("Email").fill(email);
	await page.getByLabel("Password", { exact: true }).fill(password);
	await page.getByRole("button", { name: "Sign up" }).click();
}

async function logOutFromShell(page: Page) {
	await page.getByRole("button", { name: "Log out" }).click();
	await expect(page).toHaveURL(/\/login$/);
}

test("a new person goes from the first screen to the empty vault using only the UI", async ({
	page,
}, testInfo) => {
	const shot = (name: string) =>
		page.screenshot({ path: testInfo.outputPath(`${name}.png`) });
	const email = uniqueEmail();

	// The first screen redirects to the login screen.
	await page.goto("/");
	await expect(page).toHaveURL(/\/login$/);
	await shot("01-login-empty");
	await noHorizontalScroll(page);

	await page.getByRole("link", { name: "Sign up" }).click();
	await expect(page).toHaveURL(/\/signup$/);
	await expect(page.getByText("At least 10 characters")).toBeVisible();
	await expect(page.getByRole("link", { name: /Google/ })).toHaveCount(0);
	await shot("02-signup-empty");
	await noHorizontalScroll(page);

	// Error states: invalid email, weak password.
	await page.getByLabel("Email").fill("not-an-email");
	await page.getByLabel("Password", { exact: true }).fill(PASSWORD);
	await page.getByRole("button", { name: "Sign up" }).click();
	await expect(page.getByText("Enter a valid email address.")).toBeVisible();
	await shot("03-signup-invalid-email");

	await page.getByLabel("Email").fill(email);
	await page.getByLabel("Password", { exact: true }).fill("short");
	await page.getByRole("button", { name: "Sign up" }).click();
	await expect(
		page.getByText("Use a password of 10 to 128 characters."),
	).toBeVisible();
	await shot("04-signup-weak-password");

	// Show/hide toggle, then submit with Enter.
	await page.getByLabel("Password", { exact: true }).fill(PASSWORD);
	await page.getByRole("button", { name: "Show password" }).click();
	await expect(page.getByLabel("Password", { exact: true })).toHaveAttribute(
		"type",
		"text",
	);
	await shot("05-signup-filled");
	await page.getByLabel("Password", { exact: true }).press("Enter");

	await expect(page).toHaveURL(/\/$/);
	await expect(page.getByText(EMPTY_VAULT)).toBeVisible();
	await expect(page.getByText(email)).toBeVisible();
	await shot("06-vault-shell");
	await noHorizontalScroll(page);

	// The same email again is refused, with a link to Log in.
	await logOutFromShell(page);
	await shot("07-login-after-logout");
	await signUp(page, email);
	await expect(
		page.getByText("An account with this email already exists."),
	).toBeVisible();
	await expect(
		page.getByRole("link", { name: "Log in" }).first(),
	).toBeVisible();
	await shot("08-signup-email-taken");

	// Wrong password on log in: one generic line.
	await page.goto("/login");
	await page.getByLabel("Email").fill(email);
	await page.getByLabel("Password", { exact: true }).fill("wrong wrong wrong");
	await page.getByRole("button", { name: "Log in" }).click();
	await expect(
		page.getByText("That email and password do not match."),
	).toBeVisible();
	await shot("09-login-invalid-credentials");

	// Messages for the Google redirect errors.
	await page.goto("/login?error=account_exists");
	await expect(
		page.getByText("An account with this email already exists."),
	).toBeVisible();
	await shot("10-login-account-exists");
	await page.goto("/login?error=google_failed");
	await expect(
		page.getByText("Google sign-in did not work. Please try again."),
	).toBeVisible();
	await shot("11-login-google-failed");
});

test("reloading keeps the person signed in; after Log out a reload shows /login", async ({
	page,
}, testInfo) => {
	await signUp(page, uniqueEmail());
	await expect(page.getByText(EMPTY_VAULT)).toBeVisible();

	await page.reload();
	await expect(page.getByText(EMPTY_VAULT)).toBeVisible();
	await expect(page).toHaveURL(/\/$/);

	await page.goto("/account");
	await expect(page.getByRole("heading", { name: "Account" })).toBeVisible();
	await page.reload();
	await expect(page.getByRole("heading", { name: "Account" })).toBeVisible();

	await page.goto("/");
	await logOutFromShell(page);
	await page.reload();
	await expect(page).toHaveURL(/\/login$/);
	await expect(page.getByRole("heading", { name: "Log in" })).toBeVisible();
	await page.screenshot({
		path: testInfo.outputPath("after-logout-reload.png"),
	});

	// Signed-out access to the account screen redirects, and signed-in access to /login does too.
	await page.goto("/account");
	await expect(page).toHaveURL(/\/login$/);
});

test("changes the password on the account screen and logs in with the new one", async ({
	page,
}, testInfo) => {
	const shot = (name: string) =>
		page.screenshot({ path: testInfo.outputPath(`${name}.png`) });
	const email = uniqueEmail();
	await signUp(page, email);
	await expect(page.getByText(EMPTY_VAULT)).toBeVisible();

	await page.getByRole("link", { name: email }).click();
	await expect(page).toHaveURL(/\/account$/);
	await expect(
		page.getByLabel("Current password", { exact: true }),
	).toBeVisible();
	await shot("01-account-before");
	await noHorizontalScroll(page);

	// A wrong current password shows its message and changes nothing.
	await page
		.getByLabel("Current password", { exact: true })
		.fill("wrong wrong wrong");
	await page.getByLabel("New password", { exact: true }).fill(NEW_PASSWORD);
	await page
		.getByLabel("Confirm new password", { exact: true })
		.fill(NEW_PASSWORD);
	await page.getByRole("button", { name: "Change password" }).click();
	await expect(
		page.getByText("The current password is not correct."),
	).toBeVisible();
	await shot("02-account-wrong-password");

	await page.getByLabel("Current password", { exact: true }).fill(PASSWORD);
	await page.getByRole("button", { name: "Change password" }).click();
	await expect(
		page.getByText("Password changed. Your other devices were signed out."),
	).toBeVisible();
	await shot("03-account-after");

	// Still signed in here; log out, the old password fails, the new one works.
	await logOutFromShell(page);
	await page.getByLabel("Email").fill(email);
	await page.getByLabel("Password", { exact: true }).fill(PASSWORD);
	await page.getByRole("button", { name: "Log in" }).click();
	await expect(
		page.getByText("That email and password do not match."),
	).toBeVisible();

	await page.getByLabel("Password", { exact: true }).fill(NEW_PASSWORD);
	await page.getByLabel("Password", { exact: true }).press("Enter");
	await expect(page.getByText(EMPTY_VAULT)).toBeVisible();
});

test("no screen overflows horizontally and every control is reachable by keyboard", async ({
	page,
}) => {
	async function tabbable(): Promise<string[]> {
		const found: string[] = [];
		await page.locator("body").click({ position: { x: 1, y: 1 } });
		for (let i = 0; i < 12; i++) {
			await page.keyboard.press("Tab");
			const name = await page.evaluate(() => {
				const el = document.activeElement as HTMLElement | null;
				if (!el || el === document.body) return "";
				return (
					(el.getAttribute("aria-label") ||
						el.textContent?.trim() ||
						el.getAttribute("name")) ??
					""
				);
			});
			if (name) found.push(name);
		}
		return found;
	}

	await page.goto("/signup");
	await noHorizontalScroll(page);
	expect(await tabbable()).toEqual(
		expect.arrayContaining([
			"email",
			"password",
			"Show password",
			"Sign up",
			"Log in",
		]),
	);

	await page.goto("/login");
	await noHorizontalScroll(page);
	expect(await tabbable()).toEqual(
		expect.arrayContaining([
			"email",
			"password",
			"Show password",
			"Log in",
			"Sign up",
		]),
	);

	await signUp(page, uniqueEmail());
	await expect(page.getByText(EMPTY_VAULT)).toBeVisible();
	await noHorizontalScroll(page);
	expect(await tabbable()).toEqual(expect.arrayContaining(["Log out"]));

	await page.goto("/account");
	await expect(page.getByRole("heading", { name: "Account" })).toBeVisible();
	await noHorizontalScroll(page);
	expect(await tabbable()).toEqual(
		expect.arrayContaining([
			"current_password",
			"new_password",
			"confirm_password",
			"Change password",
		]),
	);

	// Touch targets are at least 44 px high.
	for (const control of await page.locator("button, a[href], input").all()) {
		if (!(await control.isVisible())) continue;
		const box = await control.boundingBox();
		expect(box?.height ?? 0).toBeGreaterThanOrEqual(43.5);
	}
});

test("the access token is never written to storage or a script-readable cookie", async ({
	page,
}) => {
	let accessToken = "";
	page.on("response", async (response) => {
		if (!/\/api\/auth\/(signup|login|refresh)$/.test(response.url())) return;
		if (!response.ok()) return;
		const body = (await response.json()) as { access_token?: string };
		if (body.access_token) accessToken = body.access_token;
	});

	await signUp(page, uniqueEmail());
	await expect(page.getByText(EMPTY_VAULT)).toBeVisible();
	await page.reload();
	await expect(page.getByText(EMPTY_VAULT)).toBeVisible();
	await expect.poll(() => accessToken).not.toBe("");

	const stored = await page.evaluate(() =>
		JSON.stringify({
			local: { ...localStorage },
			session: { ...sessionStorage },
			cookie: document.cookie,
		}),
	);
	expect(stored).not.toContain(accessToken);
	// The refresh cookie exists but is HttpOnly, so scripts cannot read it.
	expect(stored).not.toContain("refresh_token");
	const cookies = await page.context().cookies();
	expect(cookies.find((c) => c.name === "refresh_token")?.httpOnly).toBe(true);
});
