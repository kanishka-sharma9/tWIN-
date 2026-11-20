export type ErrorDetails = Record<string, unknown>;

/** Every failed API call reaches the UI as one of these, with the server's code intact. */
export class ApiError extends Error {
	readonly status: number;
	readonly code: string;
	readonly details: ErrorDetails;

	constructor(
		status: number,
		code: string,
		message: string,
		details: ErrorDetails = {},
	) {
		super(message);
		this.name = "ApiError";
		this.status = status;
		this.code = code;
		this.details = details;
	}
}

/** Builds an ApiError from a non-2xx response, using the shared error shape when present. */
export async function apiErrorFromResponse(
	response: Response,
	parsed?: unknown,
): Promise<ApiError> {
	let body: unknown = parsed;
	if (body === undefined || typeof body === "string") {
		try {
			body = await response.clone().json();
		} catch {
			body = undefined;
		}
	}
	const error = (body as { error?: Record<string, unknown> } | undefined)
		?.error;
	if (error && typeof error.code === "string") {
		const details = { ...((error.details as ErrorDetails | undefined) ?? {}) };
		const header = Number(response.headers.get("Retry-After"));
		if (details.retry_after === undefined && header > 0) {
			details.retry_after = header;
		}
		return new ApiError(
			response.status,
			error.code,
			typeof error.message === "string" ? error.message : response.statusText,
			details,
		);
	}
	return new ApiError(
		response.status,
		`http_${response.status}`,
		response.statusText,
	);
}

export function networkError(): ApiError {
	return new ApiError(0, "network_error", "Could not reach the API.");
}

const MESSAGES: Record<string, string> = {
	network_error: "Could not reach the API. Check that it is running.",
	validation_error: "Some of the details are not valid.",
	unauthorized: "Please sign in to continue.",
	forbidden: "You do not have access to that.",
	not_found: "That could not be found.",
	method_not_allowed: "That action is not supported.",
	internal_error: "Something went wrong on our side. Please try again.",
	pair_taken: "A file with this name and alter already exists.",
	email_taken: "An account with this email already exists.",
	account_exists: "An account with this email already exists.",
	weak_password: "Use a password of 10 to 128 characters.",
	invalid_credentials: "That email and password do not match.",
	wrong_password: "The current password is not correct.",
	rate_limited: "Too many attempts. Please wait a little and try again.",
};

const GENERIC_MESSAGE = "Something went wrong. Please try again.";

/** Seconds to wait before retrying, from `details.retry_after` (filled from `Retry-After`). */
export function retryAfterSeconds(error: ApiError): number | undefined {
	const value = error.details.retry_after;
	return typeof value === "number" && value > 0 ? Math.ceil(value) : undefined;
}

/** English text for a known error code, and one generic line otherwise. */
export function errorMessage(error: unknown): string {
	if (error instanceof ApiError) {
		const seconds = retryAfterSeconds(error);
		if (error.code === "rate_limited" && seconds !== undefined) {
			return `Too many attempts. Try again in ${seconds} ${seconds === 1 ? "second" : "seconds"}.`;
		}
		return MESSAGES[error.code] ?? GENERIC_MESSAGE;
	}
	return GENERIC_MESSAGE;
}
