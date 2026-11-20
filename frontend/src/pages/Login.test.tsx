import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";
import { errorBody, jsonResponse } from "@/test/fetchMock";
import { mockApi, renderApp, tokens } from "@/test/mockApi";

afterEach(() => {
	vi.unstubAllGlobals();
});

async function logIn(email = "ada@example.com", password = "correct horse 1") {
	const user = userEvent.setup();
	await user.type(await screen.findByLabelText("Email"), email);
	await user.type(screen.getByLabelText("Password"), password);
	await user.click(screen.getByRole("button", { name: "Log in" }));
}

describe("Login", () => {
	it("has current-password autocomplete and a link to Sign up", async () => {
		mockApi();
		renderApp("/login");
		expect(await screen.findByLabelText("Password")).toHaveAttribute(
			"autocomplete",
			"current-password",
		);
		expect(screen.getByRole("link", { name: "Sign up" })).toHaveAttribute(
			"href",
			"/signup",
		);
	});

	it("opens the vault after a successful login", async () => {
		mockApi({ "POST /api/auth/login": () => jsonResponse(tokens()) });
		renderApp("/login");
		await logIn();
		expect(
			await screen.findByText("This vault is empty. Files will appear here."),
		).toBeInTheDocument();
		expect(screen.getByText("ada@example.com")).toBeInTheDocument();
	});

	it("invalid_credentials: shows one generic line", async () => {
		mockApi({
			"POST /api/auth/login": () =>
				jsonResponse(errorBody("invalid_credentials", "x"), 401),
		});
		renderApp("/login");
		await logIn();
		expect(
			await screen.findByText("That email and password do not match."),
		).toBeInTheDocument();
	});

	it("rate_limited: shows how long to wait from Retry-After", async () => {
		mockApi({
			"POST /api/auth/login": () =>
				Promise.resolve(
					new Response(JSON.stringify(errorBody("rate_limited", "x")), {
						status: 429,
						headers: {
							"Content-Type": "application/json",
							"Retry-After": "42",
						},
					}),
				),
		});
		renderApp("/login");
		await logIn();
		expect(
			await screen.findByText("Too many attempts. Try again in 42 seconds."),
		).toBeInTheDocument();
	});

	it("rate_limited without a wait time: shows the plain message", async () => {
		mockApi({
			"POST /api/auth/login": () =>
				jsonResponse(errorBody("rate_limited", "x"), 429),
		});
		renderApp("/login");
		await logIn();
		expect(
			await screen.findByText(
				"Too many attempts. Please wait a little and try again.",
			),
		).toBeInTheDocument();
	});

	it("account_exists: /login?error=account_exists shows the message", async () => {
		mockApi();
		renderApp("/login?error=account_exists");
		expect(
			await screen.findByText("An account with this email already exists."),
		).toBeInTheDocument();
	});

	it("google_failed: /login?error=google_failed shows the message", async () => {
		mockApi();
		renderApp("/login?error=google_failed");
		expect(
			await screen.findByText("Google sign-in did not work. Please try again."),
		).toBeInTheDocument();
	});

	it("ignores an unknown ?error value", async () => {
		mockApi();
		renderApp("/login?error=<script>");
		await screen.findByLabelText("Email");
		expect(screen.queryByText(/script/)).not.toBeInTheDocument();
	});

	it("shows the Google button only when providers says google is true", async () => {
		mockApi({
			"GET /api/auth/providers": () => jsonResponse({ google: true }),
		});
		renderApp("/login");
		expect(
			await screen.findByRole("link", { name: "Continue with Google" }),
		).toBeInTheDocument();
	});
});
