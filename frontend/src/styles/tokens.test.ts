import { readdirSync, readFileSync, statSync } from "node:fs";
import { extname, join, relative } from "node:path";
import { describe, expect, it } from "vitest";

const SRC = join(import.meta.dirname, "..");
const TOKENS = join(import.meta.dirname, "tokens.css");
const tokensCss = readFileSync(TOKENS, "utf8");

/** All `--name: value;` declarations in tokens.css. */
function declarations(css: string): Map<string, string> {
	const map = new Map<string, string>();
	for (const match of css.matchAll(/--([\w-]+)\s*:\s*([^;]+);/g)) {
		const [, name, value] = match;
		if (name && value) map.set(name, value.trim());
	}
	return map;
}

const tokens = declarations(tokensCss);

/** Follows var(--x) references until a literal colour is reached. */
function resolve(name: string): string {
	let value = tokens.get(name);
	for (let hops = 0; value?.startsWith("var("); hops++) {
		if (hops > 10) throw new Error(`Reference loop at --${name}`);
		const next = /var\(--([\w-]+)\)/.exec(value)?.[1];
		if (!next) throw new Error(`Bad reference in --${name}`);
		value = tokens.get(next);
	}
	if (!value) throw new Error(`Unknown token --${name}`);
	return value;
}

function luminance(hex: string): number {
	const m = /^#([0-9a-f]{6})$/i.exec(hex);
	if (!m?.[1]) throw new Error(`Not a 6-digit hex colour: ${hex}`);
	const channels = [0, 2, 4].map((i) => {
		const c = Number.parseInt(m[1]?.slice(i, i + 2) ?? "0", 16) / 255;
		return c <= 0.03928 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4;
	});
	const [r = 0, g = 0, b = 0] = channels;
	return 0.2126 * r + 0.7152 * g + 0.0722 * b;
}

function contrast(foreground: string, background: string): number {
	const a = luminance(resolve(foreground));
	const b = luminance(resolve(background));
	return (Math.max(a, b) + 0.05) / (Math.min(a, b) + 0.05);
}

/**
 * Every text-on-background pairing in use. A new pairing is added here in the same change.
 * 4.5 for body text, 3 for large text and UI icons.
 */
const PAIRINGS: [foreground: string, background: string, minimum: number][] = [
	["foreground", "background", 4.5],
	["foreground", "surface", 4.5],
	["muted-foreground", "background", 4.5],
	["muted-foreground", "surface", 4.5],
	["primary", "background", 4.5],
	["primary", "surface", 4.5],
	["primary", "selection", 3],
	["foreground", "selection", 4.5],
	["destructive", "background", 4.5],
	["destructive", "surface", 4.5],
	["primary-foreground", "primary", 4.5],
	["navbar-foreground", "navbar", 4.5],
	["hover-foreground", "hover", 4.5],
	// Focus rings: cyan on the oxblood page, oxblood inside the rose navbar.
	["ring", "background", 3],
	["ring", "surface", 3],
	["navbar-foreground", "navbar", 3],
];

describe("contrast", () => {
	it.each(PAIRINGS)(
		"%s on %s is at least %d:1",
		(foreground, background, minimum) => {
			expect(contrast(foreground, background)).toBeGreaterThanOrEqual(minimum);
		},
	);

	it("never pairs cyan text or icons with a rose surface", () => {
		const roseSurfaces = ["navbar", "hover", "foreground"].filter(
			(name) => resolve(name) === resolve("rose"),
		);
		for (const [foreground, background] of PAIRINGS) {
			if (roseSurfaces.includes(background)) {
				expect(resolve(foreground), `${foreground} on ${background}`).not.toBe(
					resolve("cyan"),
				);
			}
		}
		// The rose navbar and hover tokens use oxblood content.
		expect(resolve("navbar-foreground")).toBe(resolve("oxblood"));
		expect(resolve("hover-foreground")).toBe(resolve("oxblood"));
	});
});

describe("recolouring", () => {
	const semantic = [
		"background",
		"foreground",
		"surface",
		"navbar",
		"navbar-foreground",
		"hover",
		"hover-foreground",
		"primary",
		"primary-foreground",
		"ring",
		"selection",
		"border",
		"muted-foreground",
		"destructive",
	];

	it("defines every semantic token as a reference, never a literal colour", () => {
		for (const name of semantic) {
			expect(tokens.get(name), `--${name}`).toMatch(/^var\(--[\w-]+\)$/);
		}
	});

	it("builds the identity from the three base tokens", () => {
		const used = new Set(
			semantic.flatMap(
				(name) => /var\(--([\w-]+)\)/.exec(tokens.get(name) ?? "")?.[1] ?? [],
			),
		);
		expect(used.has("cyan")).toBe(true);
		expect(used.has("oxblood")).toBe(true);
		expect(used.has("rose")).toBe(true);
	});
});

function sourceFiles(dir: string): string[] {
	return readdirSync(dir).flatMap((entry) => {
		const path = join(dir, entry);
		if (statSync(path).isDirectory()) return sourceFiles(path);
		return [".ts", ".tsx", ".css"].includes(extname(path)) ? [path] : [];
	});
}

describe("hygiene", () => {
	const files = sourceFiles(SRC).filter(
		(f) => f !== TOKENS && !/\.test\.tsx?$/.test(f),
	);
	const literalColour =
		/#[0-9a-fA-F]{3,8}\b|\b(rgb|rgba|hsl|hsla|oklch|oklab|lab|lch)\(/;
	const builtInClass =
		/\b(?:bg|text|border|ring|fill|stroke|from|via|to|outline|divide|decoration|shadow|accent|caret)-(?:slate|gray|zinc|neutral|stone|red|orange|amber|yellow|lime|green|emerald|teal|cyan|sky|blue|indigo|violet|purple|fuchsia|pink|rose|white|black)(?:-\d+)?\b/;

	it("finds source files to check", () => {
		expect(files.length).toBeGreaterThan(3);
	});

	it("has no colour values outside tokens.css", () => {
		const offenders = files.filter((f) =>
			literalColour.test(readFileSync(f, "utf8")),
		);
		expect(offenders.map((f) => relative(SRC, f))).toEqual([]);
	});

	it("uses no Tailwind built-in colour classes", () => {
		const offenders = files.filter((f) =>
			builtInClass.test(readFileSync(f, "utf8")),
		);
		expect(offenders.map((f) => relative(SRC, f))).toEqual([]);
	});

	it("requests no font from another origin", () => {
		const offenders = files.filter((f) =>
			/https?:\/\/[^\s)]*font/i.test(readFileSync(f, "utf8")),
		);
		expect(offenders.map((f) => relative(SRC, f))).toEqual([]);
	});
});
