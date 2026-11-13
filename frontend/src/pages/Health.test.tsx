import { screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { errorBody, jsonResponse, mockFetch } from "@/test/fetchMock";
import { renderWithProviders } from "@/test/renderWithProviders";
import { Health } from "./Health";

describe("Health", () => {
	afterEach(() => {
		vi.unstubAllGlobals();
	});

	it("shows API ok", async () => {
		mockFetch(() => jsonResponse({ status: "ok", database: "up" }));
		renderWithProviders(<Health />);
		expect(
			await screen.findByText("API: ok, database: up"),
		).toBeInTheDocument();
	});

	it("shows database down", async () => {
		mockFetch(() => jsonResponse({ status: "ok", database: "down" }));
		renderWithProviders(<Health />);
		expect(
			await screen.findByText("API: ok, database: down"),
		).toBeInTheDocument();
	});

	it("shows a readable error when the network fails, after one retry", async () => {
		const fetchMock = mockFetch(() =>
			Promise.reject(new TypeError("Failed to fetch")),
		);
		renderWithProviders(<Health />);
		expect(await screen.findByRole("alert")).toHaveTextContent(
			"Could not reach the API",
		);
		expect(fetchMock).toHaveBeenCalledTimes(2);
	});

	it("shows the message for an API error code, without retrying", async () => {
		const fetchMock = mockFetch(() =>
			jsonResponse(
				errorBody(
					"pair_taken",
					"A file with this name and alter already exists.",
				),
				409,
			),
		);
		renderWithProviders(<Health />);
		expect(await screen.findByRole("alert")).toHaveTextContent(
			"A file with this name and alter already exists.",
		);
		expect(fetchMock).toHaveBeenCalledTimes(1);
	});

	it("shows a generic line for an unknown error", async () => {
		mockFetch(() => jsonResponse({ detail: "boom" }, 500));
		renderWithProviders(<Health />);
		expect(await screen.findByRole("alert")).toHaveTextContent(
			"Something went wrong",
		);
	});
});
