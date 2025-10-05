#!/usr/bin/env node

const fs = require("fs");
const path = require("path");

const apiDir = path.join(__dirname, "..", "src", "app", "api");
const tempApiDir = path.join(__dirname, "..", "temp_api");

console.log("本番ビルド用にAPIルートを一時的に移動中...");

// APIルートディレクトリが存在する場合、一時的に移動
if (fs.existsSync(apiDir)) {
  if (fs.existsSync(tempApiDir)) {
    fs.rmSync(tempApiDir, { recursive: true, force: true });
  }
  fs.renameSync(apiDir, tempApiDir);
  console.log("APIルートを一時的に移動しました:", tempApiDir);
} else {
  console.log("APIルートディレクトリが見つかりません:", apiDir);
}
