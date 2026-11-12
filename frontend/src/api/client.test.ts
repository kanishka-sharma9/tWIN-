import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { errorBody, jsonResponse, mockFetch } from "@/test/fetchMock";
import {
	api,
	getAccessToken,
	onLoggedOut,
	setAccessToken,
	setRefresh,
	unwrap,
} from "./client";
import { ApiError } from "./errors";

const OK = { status: "ok", database: "up" } as const;

function bearer(request: Request) {
	return request.headers.get("Authorization");
}

describe("api client", () => {
	beforeEach(() => {
		setAccessToken(null);
		setRefresh(() => Promise.reject(new Error("no refresh in this test")));
	});

	afterEach(() => {
		vi.unstubAllGlobals();
	});

	it("attaches the access token", async () => {
		setAccessToken("abc");
		const fetchMock = mockFetch(() => jsonResponse(OK));
		await unwrap(api.GET("/api/health"));
		expect(bearer(fetchMock.mock.calls[0]?.[0] as Request)).toBe("Bearer abc");
	});

	it("sends no Authorization header without a token", async () => {
		const fetchMock = mockFetch(() => jsonResponse(OK));
		await unwrap(api.GET("/api/health"));
		expect(bearer(fetchMock.mock.calls[0]?.[0] as Request)).toBeNull();
	});

	it("turns an error response into an ApiError with its code", async () => {
		mockFetch(() =>
			jsonResponse(errorBody("pair_taken", "Taken.", { field: "alter" }), 409),
		);
		const error = await unwrap(api.GET("/api/health")).catch((e: unknown) => e);
		expect(error).toBeInstanceOf(ApiError);
		expect(error).toMatchObject({
			status: 409,
			code: "pair_taken",
			message: "Taken.",
			details: { field: "alter" },
		});
	});

	it("turns a network failure into an ApiError with code network_error", async () => {
		mockFetch(() => Promise.reject(new TypeError("Failed to fetch")));
		const error = await unwrap(api.GET("/api/health")).catch((e: unknown) => e);
		expect(error).toMatchObject({ code: "network_error", status: 0 });
	});

	it("refreshes once on a 401 and retries the request once", async () => {
		setAccessToken("old");
		const refresh = vi.fn(() => Promise.resolve("new"));
		setRefresh(refresh);
		const fetchMock = mockFetch((request) =>
			bearer(request) === "Bearer new"
				? jsonResponse(OK)
				: jsonResponse(errorBody("unauthorized", "No."), 401),
		);

		await expect(unwrap(api.GET("/api/health"))).resolves.toEqual(OK);

		expect(refresh).toHaveBeenCalledTimes(1);
		expect(fetchMock).toHaveBeenCalledTimes(2);
		expect(getAccessToken()).toBe("new");
	});

	it("does not retry a second time when the retry is also refused", async () => {
		const refresh = vi.fn(() => Promise.resolve("new"));
		setRefresh(refresh);
		const fetchMock = mockFetch(() =>
			jsonResponse(errorBody("unauthorized", "No."), 401),
		);

		await expect(unwrap(api.GET("/api/health"))).rejects.toMatchObject({
			code: "unauthorized",
		});
		expect(refresh).toHaveBeenCalledTimes(1);
		expect(fetchMock).toHaveBeenCalledTimes(2);
	});

	it("shares one refresh between simultaneous 401s", async () => {
		setAccessToken("old");
		let resolveRefresh: (token: string) => void = () => {};
		const refresh = vi.fn(
			() =>
				new Promise<string>((resolve) => {
					resolveRefresh = resolve;
				}),
		);
		setRefresh(refresh);
		mockFetch((request) =>
			bearer(request) === "Bearer new"
				? jsonResponse(OK)
				: jsonResponse(errorBody("unauthorized", "No."), 401),
		);

		const both = Promise.all([
			unwrap(api.GET("/api/health")),
			unwrap(api.GET("/api/health")),
		]);
		await vi.waitFor(() => expect(refresh).toHaveBeenCalled());
		resolveRefresh("new");

		await expect(both).resolves.toEqual([OK, OK]);
		expect(refresh).toHaveBeenCalledTimes(1);
	});

	it("clears the token and signals logged out when the refresh fails", async () => {
		setAccessToken("old");
		const loggedOut = vi.fn();
		const unsubscribe = onLoggedOut(loggedOut);
		mockFetch(() => jsonResponse(errorBody("unauthorized", "No."), 401));

		await expect(unwrap(api.GET("/api/health"))).rejects.toMatchObject({
			code: "unauthorized",
		});

		expect(getAccessToken()).toBeNull();
		expect(loggedOut).toHaveBeenCalledTimes(1);
		unsubscribe();
	});
});
