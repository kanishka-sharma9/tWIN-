// Fails when dist/ holds anything other than static assets (D-016: no server code).
import { readdirSync, readFileSync } from "node:fs";
import { extname, join } from "node:path";

const allowed = new Set([
	".html",
	".js",
	".css",
	".svg",
	".ico",
	".png",
	".woff2",
	".json",
]);
const bad = [];

function walk(dir) {
	for (const entry of readdirSync(dir, { withFileTypes: true })) {
		const path = join(dir, entry.name);
		if (entry.isDirectory()) walk(path);
		else if (!allowed.has(extname(entry.name))) bad.push(path);
		else if (
			extname(entry.name) === ".js" &&
			readFileSync(path, "utf8").includes("tWIN-DEV-TOKENS")
		)
			bad.push(`${path} (contains the dev-only token showcase)`);
		else if (
			extname(entry.name) === ".css" &&
			/url\((["']?)https?:/.test(readFileSync(path, "utf8"))
		)
			bad.push(`${path} (loads a resource from another origin)`);
	}
}

walk("dist");
if (bad.length > 0) {
	console.error(`dist/ contains non-static files:\n${bad.join("\n")}`);
	process.exit(1);
}
console.log("dist/ holds only static assets");
