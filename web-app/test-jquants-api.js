// J-Quants API接続テスト
const fetch = require("node-fetch");

const EMAIL = process.env.NEXT_PUBLIC_JQUANTS_EMAIL;
const PASSWORD = process.env.NEXT_PUBLIC_JQUANTS_PASSWORD;
const TOKEN = process.env.NEXT_PUBLIC_JQUANTS_ID_TOKEN;
const BASE_URL = process.env.NEXT_PUBLIC_JQUANTS_BASE_URL || "https://api.jquants.com/v1";

console.log("=== J-Quants API接続テスト ===");
console.log("BASE_URL:", BASE_URL);
console.log("EMAIL:", EMAIL ? "設定あり" : "設定なし");
console.log("PASSWORD:", PASSWORD ? "設定あり" : "設定なし");
console.log("TOKEN:", TOKEN ? "設定あり (長さ: " + TOKEN.length + ")" : "設定なし");

async function testAPI() {
  try {
    // 1. トークンテスト
    console.log("\n--- トークンで銘柄一覧を取得 ---");
    const listsResponse = await fetch(`${BASE_URL}/listed/info`, {
      headers: {
        "Authorization": `Bearer ${TOKEN}`,
      },
    });
    
    console.log("Status:", listsResponse.status, listsResponse.statusText);
    const listsData = await listsResponse.json();
    console.log("Response keys:", Object.keys(listsData));
    console.log("銘柄数:", listsData.info?.length || 0);
    
    if (listsData.info && listsData.info.length > 0) {
      console.log("最初の銘柄:", JSON.stringify(listsData.info[0], null, 2));
    }
    
    // 2. 株価データ取得テスト（トヨタ: 7203）
    console.log("\n--- 株価データ取得テスト (7203: トヨタ) ---");
    const today = new Date().toISOString().split("T")[0];
    const yesterday = new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString().split("T")[0];
    
    const params = new URLSearchParams({
      code: "7203",
      from: yesterday,
      to: today,
    });
    
    const pricesResponse = await fetch(`${BASE_URL}/prices/daily_quotes?${params}`, {
      headers: {
        "Authorization": `Bearer ${TOKEN}`,
      },
    });
    
    console.log("Status:", pricesResponse.status, pricesResponse.statusText);
    const pricesData = await pricesResponse.json();
    console.log("Response keys:", Object.keys(pricesData));
    console.log("データ数:", pricesData.daily_quotes?.length || 0);
    
    if (pricesData.daily_quotes && pricesData.daily_quotes.length > 0) {
      console.log("最初のデータ:", JSON.stringify(pricesData.daily_quotes[0], null, 2));
    }
    
  } catch (error) {
    console.error("エラー:", error.message);
  }
}

testAPI();
