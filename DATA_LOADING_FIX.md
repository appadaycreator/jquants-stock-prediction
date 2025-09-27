# 🔧 データ読み込み問題の修正

## 🚨 問題の症状

ダッシュボードが表示されるが「データを読み込み中...」のまま停止する。

## 🔍 原因の特定

**❌ 問題のあるコード**:
```javascript
fetch('/data/dashboard_summary.json')  // 絶対パス
```

**GitHub Pagesの静的ホスティング**では：
- `/data/` → サーバーのルートから探すため404エラー
- `./data/` → 相対パスで正しくファイルを見つける

## 🔧 修正内容

### 1. Next.jsアプリのfetchパス修正
**ファイル**: `web-app/src/app/page.tsx`

```javascript
// 修正前
const [summaryRes, stockRes, modelRes, featureRes, predRes] = await Promise.all([
  fetch('/data/dashboard_summary.json'),        // ❌ 絶対パス
  fetch('/data/stock_data.json'),
  fetch('/data/model_comparison.json'),
  fetch('/data/feature_analysis.json'),
  fetch('/data/predictions.json')
])

// 修正後
const [summaryRes, stockRes, modelRes, featureRes, predRes] = await Promise.all([
  fetch('./data/dashboard_summary.json'),       // ✅ 相対パス
  fetch('./data/stock_data.json'),
  fetch('./data/model_comparison.json'),
  fetch('./data/feature_analysis.json'),
  fetch('./data/prediction_results.json')
])
```

### 2. 最新データの更新
```bash
# 最新のJSONデータを生成
python3 generate_web_data.py

# Webアプリをリビルド
cd web-app && npm run build

# 最新ファイルをdocsに配置
cp -r dist ../docs/web-app
cp -r public/data ../docs/web-app/
```

## 📁 修正後のファイル構成

```
docs/web-app/
├── index.html                # メインダッシュボード
├── data/                     # JSONデータ
│   ├── dashboard_summary.json    (164B)
│   ├── stock_data.json          (4.5KB)
│   ├── feature_analysis.json    (319B)
│   ├── performance_metrics.json (173B)
│   ├── prediction_results.json  (398B)
│   ├── model_comparison.json    (166B)
│   └── predictions.json         (14KB)
├── reports/
├── settings/
└── _next/                    # Next.js アセット
```

## 🎯 期待される結果

修正後、ダッシュボードで以下が正常に表示されます：

### 📊 メインダッシュボード
- **株価チャート**: リアルタイム価格推移
- **予測精度**: MAE: 52.85, R²: 0.81
- **特徴量重要度**: SMA_5 (25.1%), SMA_10 (24.6%), SMA_25 (23.4%), SMA_50 (26.9%)
- **モデル性能**: XGBoost使用

### 📈 データ詳細
- **総データポイント**: 16件
- **予測期間**: 2024-09-05 ～ 2024-09-26
- **最終更新**: 2025-09-27 17:04
- **ベストモデル**: XGBoost

### 🔍 可視化機能
- 時系列株価チャート
- 特徴量重要度バーチャート
- 予測精度散布図
- パフォーマンス指標表示

## 🌐 アクセス手順

1. **GitHub Pages設定**: Settings → Pages → Deploy from branch → main + /docs
2. **URL**: `https://appadaycreator.github.io/jquants-stock-prediction/`
3. **表示確認**: 数秒でデータが読み込まれ、チャートが表示される

## 🔄 トラブルシューティング

### まだ「読み込み中」が表示される場合
1. **ブラウザキャッシュクリア** (Ctrl+F5 / Cmd+R)
2. **開発者ツール確認** (F12 → Console でエラーチェック)
3. **ファイル存在確認**: `/docs/web-app/data/` 内のJSONファイル
4. **GitHub Pages設定確認**: 正しく有効化されているか

### ネットワークエラーの場合
- JSONファイルへの直接アクセステスト
- HTTPS接続確認
- CORS設定確認（GitHub Pages では不要）

---

🎉 **これでダッシュボードが完全に動作し、美しいデータ可視化が表示されます！**
