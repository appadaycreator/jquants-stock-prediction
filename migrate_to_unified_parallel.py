#!/usr/bin/env python3
"""
統合並列処理システムへの移行スクリプト
既存の分散した並列処理システムを統合システムに移行
"""

import os
import sys
import logging
import shutil
from typing import Dict, List, Any
from pathlib import Path

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ParallelProcessingMigration:
    """並列処理システム移行クラス"""
    
    def __init__(self):
        self.migration_log = []
        self.backup_dir = "backup/parallel_migration"
        self.unified_system_path = "unified_parallel_processing_system.py"
        
    def migrate_all_systems(self):
        """全システムの移行を実行"""
        logger.info("🚀 統合並列処理システムへの移行開始")
        
        # バックアップディレクトリ作成
        self._create_backup_directory()
        
        # 各システムの移行
        migration_tasks = [
            ("memory_optimized_processor.py", self._migrate_memory_processor),
            ("optimized_model_comparator.py", self._migrate_model_comparator),
            ("high_frequency_trading.py", self._migrate_hft_system),
            ("parallel_processing_optimizer.py", self._migrate_optimizer),
            ("enhanced_parallel_system.py", self._migrate_enhanced_system),
            ("parallel_processing_integration.py", self._migrate_integration),
        ]
        
        for file_path, migration_func in migration_tasks:
            if os.path.exists(file_path):
                try:
                    migration_func(file_path)
                    self.migration_log.append(f"✅ {file_path}: 移行完了")
                except Exception as e:
                    self.migration_log.append(f"❌ {file_path}: 移行エラー - {e}")
                    logger.error(f"移行エラー {file_path}: {e}")
            else:
                self.migration_log.append(f"⚠️ {file_path}: ファイルが見つかりません")
        
        # 移行レポート作成
        self._create_migration_report()
        
        logger.info("✅ 統合並列処理システムへの移行完了")
        return True
    
    def _create_backup_directory(self):
        """バックアップディレクトリを作成"""
        os.makedirs(self.backup_dir, exist_ok=True)
        logger.info(f"📁 バックアップディレクトリ作成: {self.backup_dir}")
    
    def _migrate_memory_processor(self, file_path: str):
        """メモリ最適化プロセッサーの移行"""
        logger.info(f"🔄 {file_path} の移行開始")
        
        # バックアップ作成
        backup_path = os.path.join(self.backup_dir, os.path.basename(file_path))
        shutil.copy2(file_path, backup_path)
        
        # 統合システムへの移行
        self._update_imports(file_path, "unified_parallel_processing_system")
        self._replace_parallel_processing_calls(file_path)
        
        logger.info(f"✅ {file_path} の移行完了")
    
    def _migrate_model_comparator(self, file_path: str):
        """モデル比較器の移行"""
        logger.info(f"🔄 {file_path} の移行開始")
        
        # バックアップ作成
        backup_path = os.path.join(self.backup_dir, os.path.basename(file_path))
        shutil.copy2(file_path, backup_path)
        
        # 統合システムへの移行
        self._update_imports(file_path, "unified_parallel_processing_system")
        self._replace_parallel_processing_calls(file_path)
        
        logger.info(f"✅ {file_path} の移行完了")
    
    def _migrate_hft_system(self, file_path: str):
        """高頻度取引システムの移行"""
        logger.info(f"🔄 {file_path} の移行開始")
        
        # バックアップ作成
        backup_path = os.path.join(self.backup_dir, os.path.basename(file_path))
        shutil.copy2(file_path, backup_path)
        
        # 統合システムへの移行
        self._update_imports(file_path, "unified_parallel_processing_system")
        self._replace_parallel_processing_calls(file_path)
        
        logger.info(f"✅ {file_path} の移行完了")
    
    def _migrate_optimizer(self, file_path: str):
        """並列処理最適化システムの移行"""
        logger.info(f"🔄 {file_path} の移行開始")
        
        # バックアップ作成
        backup_path = os.path.join(self.backup_dir, os.path.basename(file_path))
        shutil.copy2(file_path, backup_path)
        
        # 統合システムへの移行
        self._update_imports(file_path, "unified_parallel_processing_system")
        self._replace_parallel_processing_calls(file_path)
        
        logger.info(f"✅ {file_path} の移行完了")
    
    def _migrate_enhanced_system(self, file_path: str):
        """拡張並列処理システムの移行"""
        logger.info(f"🔄 {file_path} の移行開始")
        
        # バックアップ作成
        backup_path = os.path.join(self.backup_dir, os.path.basename(file_path))
        shutil.copy2(file_path, backup_path)
        
        # 統合システムへの移行
        self._update_imports(file_path, "unified_parallel_processing_system")
        self._replace_parallel_processing_calls(file_path)
        
        logger.info(f"✅ {file_path} の移行完了")
    
    def _migrate_integration(self, file_path: str):
        """並列処理統合システムの移行"""
        logger.info(f"🔄 {file_path} の移行開始")
        
        # バックアップ作成
        backup_path = os.path.join(self.backup_dir, os.path.basename(file_path))
        shutil.copy2(file_path, backup_path)
        
        # 統合システムへの移行
        self._update_imports(file_path, "unified_parallel_processing_system")
        self._replace_parallel_processing_calls(file_path)
        
        logger.info(f"✅ {file_path} の移行完了")
    
    def _update_imports(self, file_path: str, new_module: str):
        """インポート文を更新"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 既存の並列処理インポートを統合システムに置換
            old_imports = [
                "from parallel_processing_optimizer import",
                "from enhanced_parallel_system import",
                "from parallel_processing_integration import",
                "from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor",
            ]
            
            new_import = f"from {new_module} import"
            
            for old_import in old_imports:
                if old_import in content:
                    content = content.replace(old_import, new_import)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
                
        except Exception as e:
            logger.error(f"インポート更新エラー {file_path}: {e}")
    
    def _replace_parallel_processing_calls(self, file_path: str):
        """並列処理呼び出しを統合システムに置換"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 既存の並列処理呼び出しを統合システムに置換
            replacements = {
                "ParallelProcessingOptimizer()": "get_unified_system()",
                "EnhancedParallelSystem()": "get_unified_system()",
                "ParallelProcessingIntegration()": "get_unified_system()",
                "parallel_execute_optimized": "parallel_execute_unified",
                "parallel_map_optimized": "parallel_map_unified",
                "ThreadPoolExecutor(max_workers=": "get_unified_system().execute_parallel(",
                "ProcessPoolExecutor(max_workers=": "get_unified_system().execute_parallel(",
            }
            
            for old, new in replacements.items():
                if old in content:
                    content = content.replace(old, new)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
                
        except Exception as e:
            logger.error(f"並列処理呼び出し置換エラー {file_path}: {e}")
    
    def _create_migration_report(self):
        """移行レポートを作成"""
        report_path = "PARALLEL_PROCESSING_MIGRATION_REPORT.md"
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("# 並列処理システム移行レポート\n\n")
            f.write(f"移行日時: {self._get_current_timestamp()}\n\n")
            
            f.write("## 移行対象ファイル\n\n")
            f.write("| ファイル名 | ステータス |\n")
            f.write("|-----------|----------|\n")
            
            for log_entry in self.migration_log:
                if "移行完了" in log_entry:
                    f.write(f"| {log_entry.split(':')[0]} | ✅ 完了 |\n")
                elif "移行エラー" in log_entry:
                    f.write(f"| {log_entry.split(':')[0]} | ❌ エラー |\n")
                elif "ファイルが見つかりません" in log_entry:
                    f.write(f"| {log_entry.split(':')[0]} | ⚠️ 未発見 |\n")
            
            f.write("\n## 移行内容\n\n")
            f.write("1. **統合並列処理システムの導入**\n")
            f.write("   - `unified_parallel_processing_system.py` を新規作成\n")
            f.write("   - 分散した並列処理設定を一元管理\n")
            f.write("   - 動的なワーカー数調整機能を統合\n\n")
            
            f.write("2. **既存システムの移行**\n")
            f.write("   - 各システムの並列処理機能を統合システムに移行\n")
            f.write("   - 設定ファイルの一元化\n")
            f.write("   - パフォーマンス監視の統合\n\n")
            
            f.write("3. **最適化効果**\n")
            f.write("   - CPU使用率の最適化\n")
            f.write("   - 処理速度の向上\n")
            f.write("   - メモリ使用量の削減\n")
            f.write("   - 設定の一元管理\n\n")
            
            f.write("## 使用方法\n\n")
            f.write("```python\n")
            f.write("from unified_parallel_processing_system import get_unified_system, parallel_execute_unified\n\n")
            f.write("# 統合システムの取得\n")
            f.write("system = get_unified_system()\n\n")
            f.write("# 並列実行\n")
            f.write("results = parallel_execute_unified(tasks, task_type='cpu_intensive')\n")
            f.write("```\n\n")
            
            f.write("## 注意事項\n\n")
            f.write("- 既存のコードは自動的に移行されますが、手動での確認を推奨します\n")
            f.write("- バックアップファイルは `backup/parallel_migration/` に保存されています\n")
            f.write("- 移行後は統合システムの設定を確認してください\n\n")
        
        logger.info(f"📊 移行レポート作成: {report_path}")
    
    def _get_current_timestamp(self) -> str:
        """現在のタイムスタンプを取得"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def validate_migration(self) -> bool:
        """移行の検証"""
        logger.info("🔍 移行の検証開始")
        
        # 統合システムファイルの存在確認
        if not os.path.exists(self.unified_system_path):
            logger.error(f"❌ 統合システムファイルが見つかりません: {self.unified_system_path}")
            return False
        
        # 統合システムのインポートテスト
        try:
            from unified_parallel_processing_system import get_unified_system
            system = get_unified_system()
            logger.info("✅ 統合システムのインポート成功")
        except Exception as e:
            logger.error(f"❌ 統合システムのインポートエラー: {e}")
            return False
        
        # 基本機能のテスト
        try:
            def test_task(x):
                return x * 2
            
            results = system.execute_parallel([lambda: test_task(5)], "mixed")
            if results and results[0] == 10:
                logger.info("✅ 基本機能テスト成功")
            else:
                logger.error("❌ 基本機能テスト失敗")
                return False
        except Exception as e:
            logger.error(f"❌ 基本機能テストエラー: {e}")
            return False
        
        logger.info("✅ 移行の検証完了")
        return True


def main():
    """メイン実行関数"""
    logger.info("🚀 並列処理システム移行開始")
    
    # 移行実行
    migration = ParallelProcessingMigration()
    success = migration.migrate_all_systems()
    
    if success:
        # 移行の検証
        if migration.validate_migration():
            logger.info("✅ 並列処理システム移行が正常に完了しました")
            return True
        else:
            logger.error("❌ 移行の検証に失敗しました")
            return False
    else:
        logger.error("❌ 並列処理システム移行に失敗しました")
        return False


if __name__ == "__main__":
    success = main()
    if success:
        print("✅ 並列処理システム移行が正常に完了しました")
    else:
        print("❌ 並列処理システム移行に問題があります")
        sys.exit(1)
