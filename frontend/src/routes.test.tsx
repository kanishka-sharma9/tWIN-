import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";
import { getAccessToken } from "@/api/client";
import { errorBody, jsonResponse } from "@/test/fetchMock";
import { mockApi, renderApp, signedInServer, tokens } from "@/test/mockApi";

afterEach(() => {
	vi.unstubAllGlobals();
});

const EMPTY = "This vault is empty. Files will appear here.";

describe("routing", () => {
	it("redirects signed-out access to / to /login", async () => {
		mockApi();
		renderApp("/");
		expect(
			await screen.findByRole("heading", { name: "Log in" }),
		).toBeInTheDocument();
	});

	it("redirects signed-out access to /account to /login", async () => {
		mockApi();
		renderApp("/account");
		expect(
			await screen.findByRole("heading", { name: "Log in" }),
		).toBeInTheDocument();
	});

	it.each(["/login", "/signup"])(
		"redirects signed-in access to %s to /",
		async (route) => {
			mockApi(signedInServer());
			renderApp(route);
			expect(await screen.findByText(EMPTY)).toBeInTheDocument();
		},
	);

	it("keeps the person signed in on load by refreshing with the CSRF header", async () => {
		const fetchMock = mockApi(signedInServer());
		renderApp("/");
		expect(await screen.findByText(EMPTY)).toBeInTheDocument();
		const refresh = fetchMock.mock.calls
			.map(([request]) => request as Request)
			.find((request) => request.url.endsWith("/api/auth/refresh"));
		expect(refresh?.method).toBe("POST");
		expect(refresh?.headers.get("X-Requested-With")).toBe("twin");
		expect(getAccessToken()).toBe("access-1");
	});

	it("Log out calls the API with the header, clears the token and returns to /login", async () => {
		const fetchMock = mockApi(signedInServer());
		renderApp("/");
		const user = userEvent.setup();
		await user.click(await screen.findByRole("button", { name: "Log out" }));
		expect(
			await screen.findByRole("heading", { name: "Log in" }),
		).toBeInTheDocument();
		const logout = fetchMock.mock.calls
			.map(([request]) => request as Request)
			.find((request) => request.url.endsWith("/api/auth/logout"));
		expect(logout?.headers.get("X-Requested-With")).toBe("twin");
		expect(getAccessToken()).toBeNull();
	});

	it("sends the person to /login when a 401 survives the one refresh retry", async () => {
		let refreshes = 0;
		mockApi({
			"POST /api/auth/refresh": () => {
				refreshes += 1;
				// Signs in on load, then refuses every later refresh.
				return refreshes === 1
					? jsonResponse(tokens())
					: jsonResponse(errorBody("invalid_refresh_token", "x"), 401);
			},
			"POST /api/auth/change-password": () =>
				jsonResponse(errorBody("unauthorized", "x"), 401),
		});
		renderApp("/account");
		const user = userEvent.setup();
		await user.type(await screen.findByLabelText("Current password"), "a");
		await user.type(screen.getByLabelText("New password"), "b");
		await user.type(screen.getByLabelText("Confirm new password"), "b");
		await user.click(screen.getByRole("button", { name: "Change password" }));
		expect(
			await screen.findByRole("heading", { name: "Log in" }),
		).toBeInTheDocument();
	});

	it("never writes the access token to web storage or cookies", async () => {
		mockApi(signedInServer());
		renderApp("/");
		await screen.findByText(EMPTY);
		const stores = [
			JSON.stringify({ ...localStorage }),
			JSON.stringify({ ...sessionStorage }),
			document.cookie,
		].join("");
		expect(stores).not.toContain("access-1");
	});
});
