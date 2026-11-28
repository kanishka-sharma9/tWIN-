import { buttonClass } from "@/components/ui/Button";
import { useProviders } from "./useProviders";

/**
 * "Continue with Google", below an "or" divider, only when the API reports Google as on.
 * It is a plain navigation: the browser leaves for Google and the API handles the tokens.
 */
export function GoogleSignIn() {
	const { data } = useProviders();
	if (!data?.google) return null;
	return (
		<>
			<div className="text-muted-foreground my-5 flex items-center gap-3 text-sm">
				<span className="bg-border h-px flex-1" />
				or
				<span className="bg-border h-px flex-1" />
			</div>
			<a
				href="/api/auth/google/start"
				className={buttonClass("outline", "w-full")}
			>
				Continue with Google
			</a>
		</>
	);
}
