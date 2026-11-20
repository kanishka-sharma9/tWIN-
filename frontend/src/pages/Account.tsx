import { type FormEvent, useState } from "react";
import { api, unwrap } from "@/api/client";
import { errorMessage } from "@/api/errors";
import { useUser } from "@/auth/context";
import { Button } from "@/components/ui/Button";
import { FormMessage, PasswordField } from "@/components/ui/Field";

export function Account() {
	const user = useUser();
	const [current, setCurrent] = useState("");
	const [next, setNext] = useState("");
	const [confirm, setConfirm] = useState("");
	const [submitting, setSubmitting] = useState(false);
	const [errors, setErrors] = useState<{
		current?: string;
		next?: string;
		confirm?: string;
		form?: string;
	}>({});
	const [done, setDone] = useState(false);

	async function onSubmit(event: FormEvent) {
		event.preventDefault();
		setDone(false);
		if (next !== confirm) {
			setErrors({ confirm: "The new passwords do not match." });
			return;
		}
		setSubmitting(true);
		setErrors({});
		try {
			await unwrap(
				api.POST("/api/auth/change-password", {
					body: { current_password: current, new_password: next },
				}),
			);
			setCurrent("");
			setNext("");
			setConfirm("");
			setDone(true);
		} catch (error) {
			const code = (error as { code?: string }).code;
			const text = errorMessage(error);
			if (code === "wrong_password") setErrors({ current: text });
			else if (code === "weak_password") setErrors({ next: text });
			else setErrors({ form: text });
		} finally {
			setSubmitting(false);
		}
	}

	return (
		<section className="mx-auto w-full max-w-[420px] space-y-6">
			<h1 className="text-2xl font-semibold">Account</h1>
			<p>
				<span className="text-muted-foreground">Email: </span>
				<span className="font-medium break-all">{user.email}</span>
			</p>
			<div className="border-border bg-surface rounded-lg border p-5">
				<h2 className="mb-4 text-lg font-semibold">Change password</h2>
				{user.has_password ? (
					<form
						onSubmit={(event) => void onSubmit(event)}
						noValidate
						className="space-y-4"
					>
						<PasswordField
							label="Current password"
							name="current_password"
							autoComplete="current-password"
							required
							value={current}
							onChange={(event) => setCurrent(event.target.value)}
							error={errors.current}
						/>
						<PasswordField
							label="New password"
							name="new_password"
							autoComplete="new-password"
							required
							hint="At least 10 characters"
							value={next}
							onChange={(event) => setNext(event.target.value)}
							error={errors.next}
						/>
						<PasswordField
							label="Confirm new password"
							name="confirm_password"
							autoComplete="new-password"
							required
							value={confirm}
							onChange={(event) => setConfirm(event.target.value)}
							error={errors.confirm}
						/>
						<FormMessage>{errors.form}</FormMessage>
						<FormMessage tone="success">
							{done && "Password changed. Your other devices were signed out."}
						</FormMessage>
						<Button type="submit" className="w-full" disabled={submitting}>
							{submitting ? "Saving…" : "Change password"}
						</Button>
					</form>
				) : (
					<p>
						This account signs in with Google, so there is no password to
						change.
					</p>
				)}
			</div>
		</section>
	);
}
