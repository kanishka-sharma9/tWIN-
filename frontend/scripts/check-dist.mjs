// Fails when dist/ holds anything other than static assets (D-016: no server code).
import { readdirSync } from "node:fs";
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
	}
}

walk("dist");
if (bad.length > 0) {
	console.error(`dist/ contains non-static files:\n${bad.join("\n")}`);
	process.exit(1);
}
console.log("dist/ holds only static assets");
