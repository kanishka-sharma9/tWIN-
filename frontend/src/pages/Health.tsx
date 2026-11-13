import { errorMessage } from "@/api/errors";
import { useHealth } from "@/api/useHealth";

export function Health() {
	const { data, error, isPending } = useHealth();

	return (
		<section className="space-y-2">
			<h1 className="text-2xl font-semibold">tWIN!!</h1>
			{isPending && <p>Checking the API…</p>}
			{data && (
				<p>
					API: {data.status}, database: {data.database}
				</p>
			)}
			{error && (
				<p role="alert" className="text-destructive">
					{errorMessage(error)}
				</p>
			)}
		</section>
	);
}
