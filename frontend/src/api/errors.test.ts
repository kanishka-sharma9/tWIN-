import { describe, expect, it } from "vitest";
import { ApiError, apiErrorFromResponse, errorMessage } from "./errors";

function response(body: string, status: number) {
	return new Response(body, { status, statusText: "Nope" });
}

describe("apiErrorFromResponse", () => {
	it("keeps the code, message and details of the shared shape", async () => {
		const error = await apiErrorFromResponse(
			response(
				JSON.stringify({
					error: {
						code: "pair_taken",
						message: "Taken.",
						details: { field: "alter" },
					},
				}),
				409,
			),
		);
		expect(error).toBeInstanceOf(ApiError);
		expect(error.status).toBe(409);
		expect(error.code).toBe("pair_taken");
		expect(error.message).toBe("Taken.");
		expect(error.details).toEqual({ field: "alter" });
	});

	it("falls back to http_<status> when the body is not the shared shape", async () => {
		const error = await apiErrorFromResponse(response("<html>", 502));
		expect(error.code).toBe("http_502");
		expect(error.status).toBe(502);
	});
});

describe("errorMessage", () => {
	it("returns English text for a known code", () => {
		expect(errorMessage(new ApiError(409, "pair_taken", "x"))).toBe(
			"A file with this name and alter already exists.",
		);
	});

	it("returns one generic line for an unknown code or a non-API error", () => {
		const generic = errorMessage(new ApiError(418, "teapot", "x"));
		expect(generic).toContain("Something went wrong");
		expect(errorMessage(new Error("x"))).toBe(generic);
	});
});
