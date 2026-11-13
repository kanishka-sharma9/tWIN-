import { Home, Search, Settings } from "lucide-react";

// Dev-only showcase (route /dev/tokens). Excluded from the production build.
const DEV_MARKER = "tWIN-DEV-TOKENS";

const SEMANTIC_TOKENS = [
	["background", "bg-background"],
	["foreground", "bg-foreground"],
	["surface", "bg-surface"],
	["navbar", "bg-navbar"],
	["navbar-foreground", "bg-navbar-foreground"],
	["hover", "bg-hover"],
	["hover-foreground", "bg-hover-foreground"],
	["primary", "bg-primary"],
	["primary-foreground", "bg-primary-foreground"],
	["ring", "bg-ring"],
	["selection", "bg-selection"],
	["border", "bg-border"],
	["muted-foreground", "bg-muted-foreground"],
	["destructive", "bg-destructive"],
] as const;

export function DevTokens() {
	return (
		<div data-marker={DEV_MARKER} className="space-y-8">
			<h1 className="text-2xl font-semibold">Theme tokens</h1>

			<section aria-labelledby="swatches" className="space-y-3">
				<h2 id="swatches" className="text-lg font-semibold">
					Semantic tokens
				</h2>
				<ul className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-4">
					{SEMANTIC_TOKENS.map(([name, swatch]) => (
						<li key={name} className="min-w-0 space-y-1">
							<div className={`h-10 rounded-sm border ${swatch}`} />
							<code className="block truncate font-mono text-xs">--{name}</code>
						</li>
					))}
				</ul>
			</section>

			<section aria-labelledby="pairings" className="space-y-3">
				<h2 id="pairings" className="text-lg font-semibold">
					Text on background
				</h2>
				<div className="space-y-2">
					<p className="bg-background text-foreground rounded-sm border p-3">
						foreground on background
					</p>
					<p className="bg-surface text-foreground rounded-sm border p-3">
						foreground on surface
					</p>
					<p className="bg-background text-muted-foreground rounded-sm border p-3">
						muted-foreground on background
					</p>
					<p className="bg-background text-primary rounded-sm border p-3">
						primary on background
					</p>
					<p className="bg-background text-destructive rounded-sm border p-3">
						destructive on background
					</p>
					<p className="bg-primary text-primary-foreground rounded-sm p-3">
						primary-foreground on primary
					</p>
				</div>
			</section>

			<section aria-labelledby="focus" className="space-y-3">
				<h2 id="focus" className="text-lg font-semibold">
					Focus ring and hover row
				</h2>
				<button
					type="button"
					className="bg-primary text-primary-foreground min-h-11 rounded-sm px-4"
				>
					Focus me
				</button>
				<ul className="border-border divide-border divide-y rounded-sm border">
					<li className="p-3">A plain row</li>
					<li className="bg-hover text-hover-foreground p-3">A hovered row</li>
					<li className="bg-selection border-l-primary border-l-4 p-3">
						A selected row
					</li>
				</ul>
			</section>

			<section aria-labelledby="navbar" className="space-y-3">
				<h2 id="navbar" className="text-lg font-semibold">
					Navbar
				</h2>
				<nav className="navbar bg-navbar text-navbar-foreground flex items-center gap-4 rounded-sm p-2">
					<a
						href="#navbar"
						className="inline-flex min-h-11 items-center gap-2 border-b-2 px-2"
					>
						<Home size={20} aria-hidden="true" /> Home
					</a>
					<a
						href="#navbar"
						className="inline-flex min-h-11 items-center gap-2 px-2"
					>
						<Search size={20} aria-hidden="true" /> Search
					</a>
					<a
						href="#navbar"
						className="inline-flex min-h-11 items-center gap-2 px-2"
					>
						<Settings size={20} aria-hidden="true" /> Settings
					</a>
				</nav>
			</section>
		</div>
	);
}
