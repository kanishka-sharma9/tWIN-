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
		return new ApiError(
			response.status,
			error.code,
			typeof error.message === "string" ? error.message : response.statusText,
			(error.details as ErrorDetails | undefined) ?? {},
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
};

const GENERIC_MESSAGE = "Something went wrong. Please try again.";

/** English text for a known error code, and one generic line otherwise. */
export function errorMessage(error: unknown): string {
	if (error instanceof ApiError) {
		return MESSAGES[error.code] ?? GENERIC_MESSAGE;
	}
	return GENERIC_MESSAGE;
}
