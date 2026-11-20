/** The empty vault. E08-S01 replaces this with the file explorer. */
export function Home() {
	return (
		<section>
			<h1 className="sr-only">Vault</h1>
			<p className="border-border text-muted-foreground rounded-lg border border-dashed p-8 text-center">
				This vault is empty. Files will appear here.
			</p>
		</section>
	);
}
