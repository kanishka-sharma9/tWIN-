import { render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { Health } from "./Health";

function mockFetch(impl: () => Promise<Response>) {
	vi.stubGlobal("fetch", vi.fn(impl));
}

function json(body: unknown, status = 200) {
	return Promise.resolve(
		new Response(JSON.stringify(body), {
			status,
			headers: { "Content-Type": "application/json" },
		}),
	);
}

describe("Health", () => {
	afterEach(() => {
		vi.unstubAllGlobals();
	});

	it("shows API ok", async () => {
		mockFetch(() => json({ status: "ok", database: "up" }));
		render(<Health />);
		expect(
			await screen.findByText("API: ok, database: up"),
		).toBeInTheDocument();
	});

	it("shows database down", async () => {
		mockFetch(() => json({ status: "ok", database: "down" }));
		render(<Health />);
		expect(
			await screen.findByText("API: ok, database: down"),
		).toBeInTheDocument();
	});

	it("shows a readable error when the network fails", async () => {
		mockFetch(() => Promise.reject(new TypeError("Failed to fetch")));
		render(<Health />);
		expect(await screen.findByRole("alert")).toHaveTextContent(
			"Could not reach the API",
		);
	});

	it("shows the status when the API answers with an error", async () => {
		mockFetch(() => json({ detail: "boom" }, 500));
		render(<Health />);
		expect(await screen.findByRole("alert")).toHaveTextContent("status 500");
	});
});
