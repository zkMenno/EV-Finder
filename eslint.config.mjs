// Shared base ESLint flat config. Packages may import it from their own
// eslint.config.mjs and extend it (e.g. apps/web adds Next.js rules).
import js from "@eslint/js";
import prettier from "eslint-config-prettier";
import tseslint from "typescript-eslint";

export const ignores = [
  "**/node_modules/**",
  "**/.next/**",
  "**/out/**",
  "**/dist/**",
  "**/coverage/**",
  "**/generated/**",
  "pipeline/**",
  "data/**",
];

export default tseslint.config(
  { ignores },
  js.configs.recommended,
  ...tseslint.configs.recommended,
  prettier,
);
