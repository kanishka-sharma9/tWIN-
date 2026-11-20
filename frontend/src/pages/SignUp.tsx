import { type FormEvent, useState } from "react";
import { Link } from "react-router";
import { api, unwrap } from "@/api/client";
import { ApiError, errorMessage } from "@/api/errors";
import { useAuth } from "@/auth/context";
import { GoogleSignIn } from "@/auth/GoogleButton";
import { Button } from "@/components/ui/Button";
import { Field, FormMessage, PasswordField } from "@/components/ui/Field";

type Problem = {
	email?: string;
	password?: string;
	form?: string;
	emailTaken?: boolean;
};

/** Turns an API error into messages under the right field (details.fields) or the form. */
function problemFrom(error: unknown): Problem {
	if (!(error instanceof ApiError)) return { form: errorMessage(error) };
	if (error.code === "email_taken") {
		return { email: errorMessage(error), emailTaken: true };
	}
	if (error.code === "weak_password") return { password: errorMessage(error) };
	if (error.code === "validation_error") {
		const fields = error.details.fields;
		const problem: Problem = {};
		if (Array.isArray(fields)) {
			for (const item of fields as { field?: string }[]) {
				if (item.field === "email")
					problem.email = "Enter a valid email address.";
				if (item.field === "password") problem.password = "Enter a password.";
			}
		}
		return problem.email || problem.password
			? problem
			: { form: errorMessage(error) };
	}
	return { form: errorMessage(error) };
}

export function SignUp() {
	const { signIn } = useAuth();
	const [email, setEmail] = useState("");
	const [password, setPassword] = useState("");
	const [submitting, setSubmitting] = useState(false);
	const [problem, setProblem] = useState<Problem>({});

	async function onSubmit(event: FormEvent) {
		event.preventDefault();
		setSubmitting(true);
		setProblem({});
		try {
			const tokens = await unwrap(
				api.POST("/api/auth/signup", { body: { email, password } }),
			);
			// Signing in makes the router open the vault.
			signIn(tokens);
		} catch (error) {
			setProblem(problemFrom(error));
			setSubmitting(false);
		}
	}

	return (
		<>
			<h2 className="mb-4 text-xl font-semibold">Create your account</h2>
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
					error={problem.email}
				/>
				{problem.emailTaken && (
					<p className="text-sm">
						<Link
							to="/login"
							className="text-primary underline underline-offset-4"
						>
							Log in
						</Link>{" "}
						instead.
					</p>
				)}
				<PasswordField
					label="Password"
					name="password"
					autoComplete="new-password"
					required
					hint="At least 10 characters"
					value={password}
					onChange={(event) => setPassword(event.target.value)}
					error={problem.password}
				/>
				<FormMessage>{problem.form}</FormMessage>
				<Button type="submit" className="w-full" disabled={submitting}>
					{submitting ? "Creating account…" : "Sign up"}
				</Button>
			</form>
			<GoogleSignIn />
			<p className="mt-5 text-center text-sm">
				Already have an account?{" "}
				<Link to="/login" className="text-primary underline underline-offset-4">
					Log in
				</Link>
			</p>
		</>
	);
}
