#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

const apiDir = path.join(__dirname, '..', 'src', 'app', 'api');
const tempApiDir = path.join(__dirname, '..', 'temp_api');

console.log('APIルートを復元中...');

// 一時的に移動したAPIルートを復元
if (fs.existsSync(tempApiDir)) {
  if (fs.existsSync(apiDir)) {
    fs.rmSync(apiDir, { recursive: true, force: true });
  }
  fs.renameSync(tempApiDir, apiDir);
  console.log('APIルートを復元しました:', apiDir);
} else {
  console.log('復元するAPIルートが見つかりません:', tempApiDir);
}
