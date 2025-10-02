#!/usr/bin/env python3
"""
上場銘柄インデックスファイルを更新するスクリプト
全銘柄ファイルから情報を収集してlisted_index.jsonを再生成
"""

import json
import os
import glob
from datetime import datetime
from typing import List, Dict, Any

def load_stock_files() -> List[Dict[str, Any]]:
    """個別銘柄ファイルからデータを読み込み"""
    stocks_dir = "docs/data/stocks"
    stock_files = glob.glob(os.path.join(stocks_dir, "*_listed.json"))
    
    stocks = []
    for file_path in stock_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if 'stock' in data:
                    stock_info = data['stock']
                    stocks.append({
                        "code": stock_info.get("code", ""),
                        "name": stock_info.get("name", ""),
                        "sector": stock_info.get("sector", ""),
                        "market": stock_info.get("market", ""),
                        "updated_at": data.get("metadata", {}).get("generated_at", ""),
                        "file_path": f"stocks/{os.path.basename(file_path)}"
                    })
        except Exception as e:
            print(f"ファイル読み込みエラー {file_path}: {e}")
            continue
    
    return stocks

def update_listed_index():
    """listed_index.jsonを更新"""
    print("銘柄ファイルの読み込み開始...")
    stocks = load_stock_files()
    
    print(f"読み込み完了: {len(stocks)}銘柄")
    
    # メタデータの更新
    metadata = {
        "generated_at": datetime.now().isoformat(),
        "version": "2.0",
        "total_stocks": len(stocks),
        "last_updated": datetime.now().isoformat(),
        "data_type": "listed_info"
    }
    
    # 新しいlisted_index.jsonを作成
    listed_data = {
        "metadata": metadata,
        "stocks": stocks
    }
    
    # ファイルに保存
    output_path = "docs/data/listed_index.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(listed_data, f, ensure_ascii=False, indent=2)
    
    print(f"更新完了: {output_path}")
    print(f"総銘柄数: {len(stocks)}")
    
    # 統計情報を表示
    markets = {}
    sectors = {}
    
    for stock in stocks:
        market = stock.get("market", "不明")
        sector = stock.get("sector", "不明")
        
        markets[market] = markets.get(market, 0) + 1
        sectors[sector] = sectors.get(sector, 0) + 1
    
    print("\n市場別銘柄数:")
    for market, count in sorted(markets.items()):
        print(f"  {market}: {count}銘柄")
    
    print("\nセクター別銘柄数:")
    for sector, count in sorted(sectors.items()):
        print(f"  {sector}: {count}銘柄")

if __name__ == "__main__":
    update_listed_index()
