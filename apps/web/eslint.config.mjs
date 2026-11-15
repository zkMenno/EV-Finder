import nextPlugin from "@next/eslint-plugin-next";
import reactHooks from "eslint-plugin-react-hooks";
import base, { ignores } from "../../eslint.config.mjs";

export default [
  { ignores: [...ignores, "next-env.d.ts", "playwright-report/**", "test-results/**"] },
  ...base,
  {
    files: ["**/*.{ts,tsx}"],
    plugins: { "@next/next": nextPlugin, "react-hooks": reactHooks },
    rules: {
      ...nextPlugin.configs.recommended.rules,
      ...nextPlugin.configs["core-web-vitals"].rules,
      ...reactHooks.configs.recommended.rules,
    },
  },
];
