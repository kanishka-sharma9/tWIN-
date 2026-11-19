import { expect, test } from "@playwright/test";

test("home page loads, shows the health result, logs no errors and does not overflow", async ({
	page,
}) => {
	const problems: string[] = [];
	page.on("console", (message) => {
		if (message.type() === "error") problems.push(message.text());
	});
	page.on("pageerror", (error) => problems.push(error.message));

	await page.goto("/");
	await expect(page).toHaveTitle("tWIN!!");
	await expect(page.getByText("API: ok, database: up")).toBeVisible();

	// No horizontal scroll at any width, phone included.
	const overflow = await page.evaluate(
		() => document.documentElement.scrollWidth - window.innerWidth,
	);
	expect(overflow).toBeLessThanOrEqual(0);

	expect(problems).toEqual([]);
});
