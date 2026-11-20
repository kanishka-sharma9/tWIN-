import { useQuery } from "@tanstack/react-query";
import { api, unwrap } from "@/api/client";

/** Which sign-in methods the server offers; the Google button shows only when `google` is true. */
export function useProviders() {
	return useQuery({
		queryKey: ["auth", "providers"],
		queryFn: () => unwrap(api.GET("/api/auth/providers")),
	});
}
