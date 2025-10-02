#!/usr/bin/env python3
"""
jQuantsデータの差分更新スクリプト
GitHub Actionsで定期実行され、既存データとの比較による効率的な更新を行う
"""

import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional
import logging

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from unified_system import get_unified_system
from core.config_manager import ConfigManager

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/data_update.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class StockDataUpdater:
    """株価データの差分更新を管理するクラス"""
    
    def __init__(self):
        self.config_manager = ConfigManager()
        self.data_dir = Path("docs/data")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # データファイルのパス
        self.stock_data_file = self.data_dir / "stock_data.json"
        self.update_log_file = self.data_dir / "update_log.json"
        self.metadata_file = self.data_dir / "metadata.json"
        
    def load_existing_data(self) -> Dict[str, Any]:
        """既存のJSONデータを読み込み"""
        if self.stock_data_file.exists():
            try:
                with open(self.stock_data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                logger.info(f"既存データを読み込み: {len(data.get('stocks', {}))}銘柄")
                return data
            except Exception as e:
                logger.error(f"既存データの読み込みエラー: {e}")
                return self._create_empty_data()
        else:
            logger.info("既存データが存在しません。新規作成します。")
            return self._create_empty_data()
    
    def _create_empty_data(self) -> Dict[str, Any]:
        """空のデータ構造を作成"""
        return {
            "metadata": {
                "created_at": datetime.now().isoformat(),
                "version": "1.0",
                "data_source": "jquants",
                "total_stocks": 0
            },
            "stocks": {}
        }
    
    def fetch_latest_data(self) -> Dict[str, Any]:
        """jQuantsから最新データを取得"""
        try:
            logger.info("jQuantsから最新データを取得中...")
            system = get_unified_system("DataUpdater")
            
            # 統合システムでデータ取得・分析を実行
            result = system.run_stock_prediction()
            
            if result and 'stock_data' in result:
                logger.info(f"データ取得完了: {len(result['stock_data'])}銘柄")
                return result['stock_data']
            else:
                logger.warning("データ取得結果が空です")
                return {}
                
        except Exception as e:
            logger.error(f"データ取得エラー: {e}")
            return {}
    
    def update_stock_data_incremental(self, new_data: Dict[str, Any], existing_data: Dict[str, Any]) -> Dict[str, Any]:
        """差分更新ロジック"""
        updated_data = existing_data.copy()
        update_log = {
            "update_time": datetime.now().isoformat(),
            "updated_stocks": [],
            "new_stocks": [],
            "unchanged_stocks": [],
            "errors": []
        }
        
        # メタデータの更新
        updated_data['metadata'].update({
            'last_updated': datetime.now().isoformat(),
            'update_type': 'incremental',
            'total_stocks': len(new_data)
        })
        
        # 株価データの差分更新
        for code, stock_info in new_data.items():
            try:
                if code in updated_data['stocks']:
                    # 既存データとの比較
                    existing_stock = updated_data['stocks'][code]
                    changes = self._detect_changes(existing_stock, stock_info)
                    
                    if changes:
                        # 変更があった場合のみ更新
                        updated_data['stocks'][code].update(stock_info)
                        updated_data['stocks'][code]['updated_at'] = datetime.now().isoformat()
                        updated_data['stocks'][code]['changes'] = changes
                        update_log['updated_stocks'].append({
                            'code': code,
                            'name': stock_info.get('name', ''),
                            'changes': changes
                        })
                        logger.info(f"銘柄 {code} を更新: {changes}")
                    else:
                        update_log['unchanged_stocks'].append(code)
                else:
                    # 新規データを追加
                    stock_info['created_at'] = datetime.now().isoformat()
                    stock_info['updated_at'] = datetime.now().isoformat()
                    updated_data['stocks'][code] = stock_info
                    update_log['new_stocks'].append({
                        'code': code,
                        'name': stock_info.get('name', '')
                    })
                    logger.info(f"新規銘柄 {code} を追加")
                    
            except Exception as e:
                error_msg = f"銘柄 {code} の更新エラー: {e}"
                logger.error(error_msg)
                update_log['errors'].append(error_msg)
        
        # 更新ログを保存
        self._save_update_log(update_log)
        
        return updated_data
    
    def _detect_changes(self, existing: Dict[str, Any], new: Dict[str, Any]) -> List[str]:
        """変更を検出"""
        changes = []
        key_fields = ['last_price', 'volume', 'change', 'change_percent']
        
        for field in key_fields:
            if field in existing and field in new:
                if existing[field] != new[field]:
                    changes.append(f"{field}: {existing[field]} → {new[field]}")
        
        return changes
    
    def _save_update_log(self, update_log: Dict[str, Any]):
        """更新ログを保存"""
        try:
            with open(self.update_log_file, 'w', encoding='utf-8') as f:
                json.dump(update_log, f, ensure_ascii=False, indent=2)
            logger.info("更新ログを保存しました")
        except Exception as e:
            logger.error(f"更新ログの保存エラー: {e}")
    
    def save_updated_data(self, data: Dict[str, Any]):
        """更新されたデータを保存"""
        try:
            # バックアップを作成
            if self.stock_data_file.exists():
                backup_file = self.stock_data_file.with_suffix('.json.backup')
                self.stock_data_file.rename(backup_file)
                logger.info(f"バックアップを作成: {backup_file}")
            
            # データを保存
            with open(self.stock_data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"データを保存しました: {self.stock_data_file}")
            
            # メタデータを個別保存
            metadata = {
                "last_updated": data['metadata']['last_updated'],
                "total_stocks": data['metadata']['total_stocks'],
                "file_size": self.stock_data_file.stat().st_size,
                "update_status": "success"
            }
            
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            logger.error(f"データ保存エラー: {e}")
            raise
    
    def run_update(self):
        """更新処理を実行"""
        try:
            logger.info("=== 株価データ更新開始 ===")
            
            # 既存データを読み込み
            existing_data = self.load_existing_data()
            
            # 最新データを取得
            new_data = self.fetch_latest_data()
            
            if not new_data:
                logger.warning("新しいデータが取得できませんでした")
                return False
            
            # 差分更新を実行
            updated_data = self.update_stock_data_incremental(new_data, existing_data)
            
            # データを保存
            self.save_updated_data(updated_data)
            
            logger.info("=== 株価データ更新完了 ===")
            return True
            
        except Exception as e:
            logger.error(f"更新処理エラー: {e}")
            return False

def main():
    """メイン処理"""
    updater = StockDataUpdater()
    success = updater.run_update()
    
    if success:
        logger.info("データ更新が正常に完了しました")
        sys.exit(0)
    else:
        logger.error("データ更新に失敗しました")
        sys.exit(1)

if __name__ == "__main__":
    main()
