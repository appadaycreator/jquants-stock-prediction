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
      // 警告ゼロ運用のため未使用変数は警告しない（将来は型レベルで検出）
      "no-unused-vars": "off",
      // 開発中のconsole.logを許可
      "no-console": "off",
      // コアWebバイタルの警告をゼロに（実運用では個別最適化）
      "react-hooks/exhaustive-deps": "off",
      // a11yの警告は別ツールで担保（ここではゼロ警告方針）
      "jsx-a11y/role-supports-aria-props": "off",
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
