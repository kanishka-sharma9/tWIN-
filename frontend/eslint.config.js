// Biome formats and lints (D-038). ESLint holds only what Biome cannot do:
// type-aware typescript-eslint rules and the react-hooks rules.
import reactHooks from "eslint-plugin-react-hooks";
import tseslint from "typescript-eslint";

export default tseslint.config(
	{
		ignores: ["dist", "node_modules", "e2e/test-results", "playwright-report"],
	},
	{
		files: ["**/*.{ts,tsx}"],
		languageOptions: {
			parser: tseslint.parser,
			parserOptions: {
				projectService: true,
				tsconfigRootDir: import.meta.dirname,
			},
		},
		plugins: {
			"@typescript-eslint": tseslint.plugin,
			"react-hooks": reactHooks,
		},
		rules: {
			"@typescript-eslint/no-floating-promises": "error",
			"@typescript-eslint/no-misused-promises": "error",
			"react-hooks/rules-of-hooks": "error",
			"react-hooks/exhaustive-deps": "error",
		},
	},
);
