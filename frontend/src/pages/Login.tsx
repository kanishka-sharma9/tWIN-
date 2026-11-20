import { type FormEvent, useState } from "react";
import { Link, useSearchParams } from "react-router";
import { api, unwrap } from "@/api/client";
import { errorMessage } from "@/api/errors";
import { useAuth } from "@/auth/context";
import { GoogleSignIn } from "@/auth/GoogleButton";
import { Button } from "@/components/ui/Button";
import { Field, FormMessage, PasswordField } from "@/components/ui/Field";

/** Messages for `/login?error=...`, which the Google callback redirects to. */
const REDIRECT_ERRORS: Record<string, string> = {
	account_exists: "An account with this email already exists.",
	google_failed: "Google sign-in did not work. Please try again.",
};

export function Login() {
	const { signIn } = useAuth();
	const [params] = useSearchParams();
	const [email, setEmail] = useState("");
	const [password, setPassword] = useState("");
	const [submitting, setSubmitting] = useState(false);
	const [message, setMessage] = useState<string | null>(null);

	const redirected = REDIRECT_ERRORS[params.get("error") ?? ""];

	async function onSubmit(event: FormEvent) {
		event.preventDefault();
		setSubmitting(true);
		setMessage(null);
		try {
			signIn(
				await unwrap(
					api.POST("/api/auth/login", { body: { email, password } }),
				),
			);
		} catch (error) {
			setMessage(errorMessage(error));
			setSubmitting(false);
		}
	}

	return (
		<>
			<h2 className="mb-4 text-xl font-semibold">Log in</h2>
			<form
				onSubmit={(event) => void onSubmit(event)}
				noValidate
				className="space-y-4"
			>
				<Field
					label="Email"
					type="email"
					name="email"
					autoComplete="email"
					required
					value={email}
					onChange={(event) => setEmail(event.target.value)}
				/>
				<PasswordField
					label="Password"
					name="password"
					autoComplete="current-password"
					required
					value={password}
					onChange={(event) => setPassword(event.target.value)}
				/>
				<FormMessage>{message ?? redirected}</FormMessage>
				<Button type="submit" className="w-full" disabled={submitting}>
					{submitting ? "Logging in…" : "Log in"}
				</Button>
			</form>
			<GoogleSignIn />
			<p className="mt-5 text-center text-sm">
				New here?{" "}
				<Link
					to="/signup"
					className="text-primary inline-flex min-h-11 items-center underline underline-offset-4"
				>
					Sign up
				</Link>
			</p>
		</>
	);
}
