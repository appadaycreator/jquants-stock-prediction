import { dirname } from "path";
import { fileURLToPath } from "url";
import { FlatCompat } from "@eslint/eslintrc";

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const compat = new FlatCompat({
  baseDirectory: __dirname,
});

const eslintConfig = [
  ...compat.extends("next/core-web-vitals"),
  {
    rules: {
      "quotes": ["error", "double"],
      "semi": ["error", "always"],
      "comma-dangle": ["error", "always-multiline"],
      "no-unused-vars": "warn",
      "no-console": "off", // 開発中のconsole.logを許可
    },
  },
  {
    ignores: [
      "node_modules/**",
      ".next/**",
      "out/**",
      "build/**",
      "next-env.d.ts",
      "dist/**",
      "coverage/**",
      "**/*.d.ts",
      "**/static/**",
      "**/chunks/**",
    ],
  },
];

export default eslintConfig;
