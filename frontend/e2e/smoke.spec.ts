import { expect, test } from "@playwright/test";

test("home page loads, shows the health result, logs no errors and does not overflow", async ({
	page,
}) => {
	const problems: string[] = [];
	page.on("console", (message) => {
		// The app asks the API for a session on every load; for a signed-out visitor that
		// refresh answers 401 and the browser logs it. That is expected, not a problem.
		const expectedSignedOut401 = message.text().includes("status of 401");
		if (message.type() === "error" && !expectedSignedOut401) {
			problems.push(message.text());
		}
	});
	page.on("pageerror", (error) => problems.push(error.message));

	await page.goto("/health");
	await expect(page).toHaveTitle("tWIN!!");
	await expect(page.getByText("API: ok, database: up")).toBeVisible();

	// No horizontal scroll at any width, phone included.
	const overflow = await page.evaluate(
		() => document.documentElement.scrollWidth - window.innerWidth,
	);
	expect(overflow).toBeLessThanOrEqual(0);

	expect(problems).toEqual([]);
});
