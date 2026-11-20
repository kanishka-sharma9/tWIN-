import { Eye, EyeOff } from "lucide-react";
import { type InputHTMLAttributes, useId, useState } from "react";
import { cn } from "@/lib/utils";

type FieldProps = Omit<InputHTMLAttributes<HTMLInputElement>, "id"> & {
	label: string;
	hint?: string;
	/** Shown under the field and announced to screen readers when it appears. */
	error?: string | null;
};

const INPUT =
	"block min-h-11 w-full rounded-md border border-border bg-background px-3 text-base text-foreground placeholder:text-muted-foreground aria-[invalid=true]:border-destructive";

function FieldShell({
	id,
	label,
	hint,
	error,
	children,
}: {
	id: string;
	label: string;
	hint?: string;
	error?: string | null;
	children: React.ReactNode;
}) {
	return (
		<div className="space-y-1.5">
			<label htmlFor={id} className="block text-sm font-medium">
				{label}
			</label>
			{children}
			{hint && (
				<p id={`${id}-hint`} className="text-muted-foreground text-sm">
					{hint}
				</p>
			)}
			<div aria-live="polite">
				{error && (
					<p id={`${id}-error`} className="text-destructive text-sm">
						{error}
					</p>
				)}
			</div>
		</div>
	);
}

function describedBy(id: string, hint?: string, error?: string | null) {
	const ids = [hint && `${id}-hint`, error && `${id}-error`].filter(Boolean);
	return ids.length ? ids.join(" ") : undefined;
}

export function Field({ label, hint, error, className, ...input }: FieldProps) {
	const id = useId();
	return (
		<FieldShell id={id} label={label} hint={hint} error={error}>
			<input
				id={id}
				className={cn(INPUT, className)}
				aria-invalid={error ? true : undefined}
				aria-describedby={describedBy(id, hint, error)}
				{...input}
			/>
		</FieldShell>
	);
}

/** A password input with a show/hide toggle. */
export function PasswordField({
	label,
	hint,
	error,
	className,
	...input
}: Omit<FieldProps, "type">) {
	const id = useId();
	const [shown, setShown] = useState(false);
	return (
		<FieldShell id={id} label={label} hint={hint} error={error}>
			<div className="relative">
				<input
					id={id}
					type={shown ? "text" : "password"}
					className={cn(INPUT, "pr-12", className)}
					aria-invalid={error ? true : undefined}
					aria-describedby={describedBy(id, hint, error)}
					{...input}
				/>
				<button
					type="button"
					onClick={() => setShown((value) => !value)}
					aria-pressed={shown}
					aria-label={
						shown
							? `Hide ${label.toLowerCase()}`
							: `Show ${label.toLowerCase()}`
					}
					className="text-muted-foreground hover:text-foreground absolute inset-y-0 right-0 grid w-11 place-items-center rounded-md"
				>
					{shown ? (
						<EyeOff aria-hidden size={20} />
					) : (
						<Eye aria-hidden size={20} />
					)}
				</button>
			</div>
		</FieldShell>
	);
}

/** A message for the whole form: always in the DOM so changes are announced. */
export function FormMessage({
	tone = "error",
	children,
}: {
	tone?: "error" | "success";
	children?: React.ReactNode;
}) {
	return (
		<div aria-live="polite">
			{children && (
				<p
					className={cn(
						"text-sm",
						tone === "error" ? "text-destructive" : "text-primary",
					)}
				>
					{children}
				</p>
			)}
		</div>
	);
}
