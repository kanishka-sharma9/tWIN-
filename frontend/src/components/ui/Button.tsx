import type { ButtonHTMLAttributes } from "react";
import { cn } from "@/lib/utils";

type Variant = "primary" | "outline";

const VARIANTS: Record<Variant, string> = {
	primary: "bg-primary text-primary-foreground hover:bg-primary/85",
	outline:
		"border border-border bg-transparent hover:bg-hover hover:text-hover-foreground",
};

export const BUTTON_BASE =
	"inline-flex min-h-11 items-center justify-center gap-2 rounded-md px-4 text-sm font-semibold transition-colors disabled:cursor-not-allowed disabled:opacity-60";

export function buttonClass(variant: Variant = "primary", className?: string) {
	return cn(BUTTON_BASE, VARIANTS[variant], className);
}

export function Button({
	variant = "primary",
	className,
	type = "button",
	...props
}: ButtonHTMLAttributes<HTMLButtonElement> & { variant?: Variant }) {
	return (
		<button
			type={type}
			className={buttonClass(variant, className)}
			{...props}
		/>
	);
}
