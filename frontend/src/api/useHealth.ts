import { useQuery } from "@tanstack/react-query";
import { api, unwrap } from "./client";

export function useHealth() {
	return useQuery({
		queryKey: ["health"],
		queryFn: () => unwrap(api.GET("/api/health")),
	});
}
