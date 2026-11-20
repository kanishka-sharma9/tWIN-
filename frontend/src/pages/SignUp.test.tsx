import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";
import { errorBody, jsonResponse } from "@/test/fetchMock";
import { mockApi, renderApp, tokens } from "@/test/mockApi";

afterEach(() => {
	vi.unstubAllGlobals();
});

async function fillAndSubmit(email: string, password: string) {
	const user = userEvent.setup();
	await user.type(await screen.findByLabelText("Email"), email);
	await user.type(screen.getByLabelText("Password"), password);
	await user.click(screen.getByRole("button", { name: "Sign up" }));
}

describe("SignUp", () => {
	it("shows the fields, the hint and the right autocomplete values", async () => {
		mockApi();
		renderApp("/signup");
		const email = await screen.findByLabelText("Email");
		expect(email).toHaveAttribute("autocomplete", "email");
		expect(screen.getByLabelText("Password")).toHaveAttribute(
			"autocomplete",
			"new-password",
		);
		expect(screen.getByText("At least 10 characters")).toBeInTheDocument();
	});

	it("toggles the password between hidden and shown", async () => {
		mockApi();
		renderApp("/signup");
		const user = userEvent.setup();
		const input = await screen.findByLabelText("Password");
		expect(input).toHaveAttribute("type", "password");
		await user.click(screen.getByRole("button", { name: "Show password" }));
		expect(input).toHaveAttribute("type", "text");
	});

	it("opens the vault after a successful sign up (Enter submits)", async () => {
		const fetchMock = mockApi({
			"POST /api/auth/signup": () => jsonResponse(tokens(), 201),
		});
		renderApp("/signup");
		const user = userEvent.setup();
		await user.type(await screen.findByLabelText("Email"), "ada@example.com");
		await user.type(
			screen.getByLabelText("Password"),
			"correct horse 1{Enter}",
		);
		expect(
			await screen.findByText("This vault is empty. Files will appear here."),
		).toBeInTheDocument();
		const signup = fetchMock.mock.calls
			.map(([request]) => request as Request)
			.find((request) => request.url.endsWith("/api/auth/signup"));
		expect(await signup?.json()).toEqual({
			email: "ada@example.com",
			password: "correct horse 1",
		});
	});

	it("email_taken: shows the message with a Log in link", async () => {
		mockApi({
			"POST /api/auth/signup": () =>
				jsonResponse(errorBody("email_taken", "taken"), 409),
		});
		renderApp("/signup");
		await fillAndSubmit("ada@example.com", "correct horse 1");
		expect(
			await screen.findByText("An account with this email already exists."),
		).toBeInTheDocument();
		expect(screen.getAllByRole("link", { name: "Log in" })[0]).toHaveAttribute(
			"href",
			"/login",
		);
	});

	it("weak_password: shows the message under the password field", async () => {
		mockApi({
			"POST /api/auth/signup": () =>
				jsonResponse(errorBody("weak_password", "short"), 422),
		});
		renderApp("/signup");
		await fillAndSubmit("ada@example.com", "short");
		const message = await screen.findByText(
			"Use a password of 10 to 128 characters.",
		);
		expect(screen.getByLabelText("Password")).toHaveAccessibleDescription(
			expect.stringContaining(message.textContent ?? ""),
		);
	});

	it("validation_error: shows field errors from details.fields, not the raw code", async () => {
		mockApi({
			"POST /api/auth/signup": () =>
				jsonResponse(
					errorBody("validation_error", "The request is not valid.", {
						fields: [{ field: "email", reason: "Value error, bad" }],
					}),
					422,
				),
		});
		renderApp("/signup");
		await fillAndSubmit("nope", "correct horse 1");
		expect(
			await screen.findByText("Enter a valid email address."),
		).toBeInTheDocument();
		expect(screen.queryByText(/validation_error/)).not.toBeInTheDocument();
	});

	it("validation_error without fields: shows the generic validation message", async () => {
		mockApi({
			"POST /api/auth/signup": () =>
				jsonResponse(errorBody("validation_error", "x"), 422),
		});
		renderApp("/signup");
		await fillAndSubmit("a@b.co", "correct horse 1");
		expect(
			await screen.findByText("Some of the details are not valid."),
		).toBeInTheDocument();
	});

	it("disables the button while submitting", async () => {
		let release: (response: Response) => void = () => {};
		mockApi({
			"POST /api/auth/signup": () =>
				new Promise<Response>((resolve) => {
					release = resolve;
				}),
		});
		renderApp("/signup");
		await fillAndSubmit("ada@example.com", "correct horse 1");
		expect(
			await screen.findByRole("button", { name: "Creating account…" }),
		).toBeDisabled();
		release(new Response(JSON.stringify(tokens()), { status: 201 }));
	});

	it("shows an unknown code as the generic line", async () => {
		mockApi({
			"POST /api/auth/signup": () =>
				jsonResponse(errorBody("teapot", "x"), 418),
		});
		renderApp("/signup");
		await fillAndSubmit("ada@example.com", "correct horse 1");
		expect(await screen.findByText(/Something went wrong/)).toBeInTheDocument();
	});
});

describe("Google button", () => {
	it("is absent when providers says google is false", async () => {
		const fetchMock = mockApi();
		renderApp("/signup");
		await screen.findByLabelText("Email");
		await vi.waitFor(() =>
			expect(
				fetchMock.mock.calls.some(([r]) =>
					(r as Request).url.endsWith("/api/auth/providers"),
				),
			).toBe(true),
		);
		expect(
			screen.queryByRole("link", { name: "Continue with Google" }),
		).not.toBeInTheDocument();
	});

	it("is present, as a plain link to the start route, when google is true", async () => {
		mockApi({
			"GET /api/auth/providers": () => jsonResponse({ google: true }),
		});
		renderApp("/signup");
		const link = await screen.findByRole("link", {
			name: "Continue with Google",
		});
		expect(link).toHaveAttribute("href", "/api/auth/google/start");
		expect(screen.getByText("or")).toBeInTheDocument();
	});
});
