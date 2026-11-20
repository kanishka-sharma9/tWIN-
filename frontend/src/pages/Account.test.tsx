import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";
import { errorBody } from "@/test/fetchMock";
import { mockApi, renderApp, signedInServer, USER } from "@/test/mockApi";

afterEach(() => {
	vi.unstubAllGlobals();
});

async function submit(current: string, next: string, confirm: string) {
	const user = userEvent.setup();
	await user.type(await screen.findByLabelText("Current password"), current);
	await user.type(screen.getByLabelText("New password"), next);
	await user.type(screen.getByLabelText("Confirm new password"), confirm);
	await user.click(screen.getByRole("button", { name: "Change password" }));
}

describe("Account", () => {
	it("shows the email and the three password fields with autocomplete values", async () => {
		mockApi(signedInServer());
		renderApp("/account");
		expect((await screen.findAllByText(USER.email))[0]).toBeInTheDocument();
		expect(screen.getByLabelText("Current password")).toHaveAttribute(
			"autocomplete",
			"current-password",
		);
		expect(screen.getByLabelText("New password")).toHaveAttribute(
			"autocomplete",
			"new-password",
		);
	});

	it("changes the password and says other devices were signed out", async () => {
		const fetchMock = mockApi({
			...signedInServer(),
			"POST /api/auth/change-password": () =>
				new Response(null, { status: 204 }),
		});
		renderApp("/account");
		await submit("old password 1", "new password 22", "new password 22");
		expect(
			await screen.findByText(
				"Password changed. Your other devices were signed out.",
			),
		).toBeInTheDocument();
		const call = fetchMock.mock.calls
			.map(([request]) => request as Request)
			.find((request) => request.url.endsWith("/change-password"));
		expect(await call?.json()).toEqual({
			current_password: "old password 1",
			new_password: "new password 22",
		});
		expect(call?.headers.get("Authorization")).toBe("Bearer access-1");
	});

	it("wrong_password: shows the message under the current password", async () => {
		const fetchMock = mockApi({
			...signedInServer(),
			"POST /api/auth/change-password": () =>
				Promise.resolve(
					new Response(JSON.stringify(errorBody("wrong_password", "x")), {
						status: 401,
						headers: { "Content-Type": "application/json" },
					}),
				),
		});
		renderApp("/account");
		await submit("nope nope nope", "new password 22", "new password 22");
		expect(
			await screen.findByText("The current password is not correct."),
		).toBeInTheDocument();
		// Sent once: a wrong password must not trigger a refresh and a resend.
		const sent = fetchMock.mock.calls.filter(([r]) =>
			(r as Request).url.endsWith("/change-password"),
		);
		expect(sent).toHaveLength(1);
	});

	it("weak_password: shows the message under the new password", async () => {
		mockApi({
			...signedInServer(),
			"POST /api/auth/change-password": () =>
				Promise.resolve(
					new Response(JSON.stringify(errorBody("weak_password", "x")), {
						status: 422,
						headers: { "Content-Type": "application/json" },
					}),
				),
		});
		renderApp("/account");
		await submit("old password 1", "short", "short");
		expect(
			await screen.findByText("Use a password of 10 to 128 characters."),
		).toBeInTheDocument();
	});

	it("does not call the API when the confirmation differs", async () => {
		const fetchMock = mockApi(signedInServer());
		renderApp("/account");
		await submit("old password 1", "new password 22", "something else 33");
		expect(
			await screen.findByText("The new passwords do not match."),
		).toBeInTheDocument();
		expect(
			fetchMock.mock.calls.some(([r]) =>
				(r as Request).url.endsWith("/change-password"),
			),
		).toBe(false);
	});

	it("explains that a Google-only account has no password to change", async () => {
		mockApi(signedInServer({ ...USER, has_password: false }));
		renderApp("/account");
		expect(
			await screen.findByText(
				"This account signs in with Google, so there is no password to change.",
			),
		).toBeInTheDocument();
		expect(screen.queryByLabelText("Current password")).not.toBeInTheDocument();
	});
});
