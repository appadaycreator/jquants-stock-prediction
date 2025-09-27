#!/usr/bin/env python3
"""
エラーハンドリングシステム移行スクリプト
既存の複数のエラーハンドリングシステムを統合システムに移行

移行対象:
- unified_error_handler.py (旧統合システム)
- unified_error_logging_system.py (新統合システム)
- enhanced_logging.py (強化ログシステム)
"""

import os
import sys
import re
import shutil
from pathlib import Path
from typing import List, Dict, Tuple
import logging

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ErrorHandlingMigration:
    """エラーハンドリングシステム移行クラス"""

    def __init__(self, project_root: str):
        """
        初期化

        Args:
            project_root: プロジェクトルートディレクトリ
        """
        self.project_root = Path(project_root)
        self.backup_dir = self.project_root / "backup" / "error_handling_migration"
        self.migration_log = []
        
        # 移行対象ファイル
        self.legacy_files = [
            "unified_error_handler.py",
            "unified_error_logging_system.py"
        ]
        
        # 統合後ファイル
        self.new_file = "unified_error_handling_system.py"
        
        # 影響を受けるファイルのパターン
        self.affected_patterns = [
            r"from unified_error_handler import",
            r"from unified_error_logging_system import",
            r"import unified_error_handler",
            r"import unified_error_logging_system",
            r"get_unified_error_handler",
            r"get_unified_error_logging_system"
        ]

    def create_backup(self):
        """バックアップの作成"""
        logger.info("📦 バックアップを作成中...")
        
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        for file_name in self.legacy_files:
            source_file = self.project_root / file_name
            if source_file.exists():
                backup_file = self.backup_dir / file_name
                shutil.copy2(source_file, backup_file)
                logger.info(f"✅ バックアップ作成: {file_name}")
                self.migration_log.append(f"バックアップ作成: {file_name}")

    def analyze_usage(self) -> Dict[str, List[str]]:
        """使用状況の分析"""
        logger.info("🔍 使用状況を分析中...")
        
        usage_analysis = {
            'unified_error_handler': [],
            'unified_error_logging_system': [],
            'enhanced_logging': []
        }
        
        # Pythonファイルの検索
        for py_file in self.project_root.rglob("*.py"):
            if py_file.name in ["error_handling_migration.py", "unified_error_handling_system.py"]:
                continue
                
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # unified_error_handler の使用チェック
                if "unified_error_handler" in content:
                    usage_analysis['unified_error_handler'].append(str(py_file))
                
                # unified_error_logging_system の使用チェック
                if "unified_error_logging_system" in content:
                    usage_analysis['unified_error_logging_system'].append(str(py_file))
                
                # enhanced_logging の使用チェック
                if "enhanced_logging" in content:
                    usage_analysis['enhanced_logging'].append(str(py_file))
                    
            except Exception as e:
                logger.warning(f"⚠️ ファイル読み込みエラー: {py_file} - {e}")
        
        # 分析結果のログ出力
        for system, files in usage_analysis.items():
            if files:
                logger.info(f"📊 {system} を使用しているファイル: {len(files)}個")
                for file_path in files[:5]:  # 最初の5個のみ表示
                    logger.info(f"  - {file_path}")
                if len(files) > 5:
                    logger.info(f"  ... 他 {len(files) - 5}個")
        
        return usage_analysis

    def generate_migration_guide(self, usage_analysis: Dict[str, List[str]]):
        """移行ガイドの生成"""
        logger.info("📋 移行ガイドを生成中...")
        
        guide_content = f"""# エラーハンドリングシステム移行ガイド

## 移行概要

このガイドは、複数のエラーハンドリングシステムを統合システムに移行するための手順を説明します。

## 移行対象システム

### 1. unified_error_handler.py (旧統合システム)
- 使用ファイル数: {len(usage_analysis['unified_error_handler'])}
- 状態: 廃止予定

### 2. unified_error_logging_system.py (新統合システム)
- 使用ファイル数: {len(usage_analysis['unified_error_logging_system'])}
- 状態: 統合対象

### 3. enhanced_logging.py (強化ログシステム)
- 使用ファイル数: {len(usage_analysis['enhanced_logging'])}
- 状態: 機能統合

## 新しい統合システム

### unified_error_handling_system.py
統合されたエラーハンドリングシステムの特徴:
- 統一されたエラー分類とハンドリング
- 構造化ログ出力
- エラー復旧機能
- パフォーマンス監視
- セキュリティ監査

## 移行手順

### 1. インポート文の更新

#### 旧形式:
```python
from unified_error_handler import get_unified_error_handler
from unified_error_logging_system import get_unified_error_logging_system
from unified_logging_config import get_system_logger
```

#### 新形式:
```python
from unified_error_handling_system import (
    get_unified_error_handler,
    ErrorCategory,
    ErrorSeverity,
    error_handler,
    error_context,
    log_api_error,
    log_data_error,
    log_model_error,
    log_file_error
)
```

### 2. エラーハンドリングの更新

#### 旧形式:
```python
error_handler = get_unified_error_handler()
error_handler.log_error(error, "エラー説明")
```

#### 新形式:
```python
from unified_error_handling_system import get_unified_error_handler, ErrorCategory, ErrorSeverity

error_handler = get_unified_error_handler()
error_handler.log_error(
    error=error,
    category=ErrorCategory.API,
    severity=ErrorSeverity.HIGH,
    operation="API呼び出し"
)
```

### 3. デコレータの使用

#### 新機能:
```python
from unified_error_handling_system import error_handler, ErrorCategory, ErrorSeverity

@error_handler(ErrorCategory.API, ErrorSeverity.HIGH, "API呼び出し")
def api_call():
    # API呼び出し処理
    pass
```

### 4. コンテキストマネージャーの使用

#### 新機能:
```python
from unified_error_handling_system import error_context, ErrorCategory, ErrorSeverity

with error_context("データ処理", ErrorCategory.DATA, ErrorSeverity.MEDIUM) as error_handler:
    # データ処理
    pass
```

## 影響を受けるファイル

### unified_error_handler を使用しているファイル:
"""
        
        for file_path in usage_analysis['unified_error_handler']:
            guide_content += f"- {file_path}\n"
        
        guide_content += f"""
### unified_error_logging_system を使用しているファイル:
"""
        
        for file_path in usage_analysis['unified_error_logging_system']:
            guide_content += f"- {file_path}\n"
        
        guide_content += f"""
### enhanced_logging を使用しているファイル:
"""
        
        for file_path in usage_analysis['enhanced_logging']:
            guide_content += f"- {file_path}\n"
        
        guide_content += """
## 移行後の確認事項

1. すべてのインポート文が更新されているか
2. エラーハンドリングの動作が正常か
3. ログ出力が期待通りか
4. パフォーマンスに問題がないか

## ロールバック手順

移行に問題が発生した場合:

1. バックアップファイルの復元
2. 旧システムの再有効化
3. 問題の調査と修正

## サポート

移行に関する質問や問題がある場合は、開発チームに連絡してください。
"""
        
        # 移行ガイドの保存
        guide_file = self.project_root / "ERROR_HANDLING_MIGRATION_GUIDE.md"
        with open(guide_file, 'w', encoding='utf-8') as f:
            f.write(guide_content)
        
        logger.info(f"✅ 移行ガイドを生成しました: {guide_file}")
        self.migration_log.append(f"移行ガイド生成: {guide_file}")

    def create_migration_script(self, usage_analysis: Dict[str, List[str]]):
        """移行スクリプトの作成"""
        logger.info("🔧 移行スクリプトを作成中...")
        
        script_content = f'''#!/usr/bin/env python3
"""
自動移行スクリプト
エラーハンドリングシステムの自動移行を実行
"""

import os
import re
from pathlib import Path

def migrate_imports(file_path: str):
    """インポート文の移行"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 旧インポート文の置換
    replacements = [
        (
            r"from unified_error_handler import.*",
            "from unified_error_handling_system import get_unified_error_handler, ErrorCategory, ErrorSeverity"
        ),
        (
            r"from unified_error_logging_system import.*",
            "from unified_error_handling_system import get_unified_error_handler, ErrorCategory, ErrorSeverity"
        ),
        (
            r"import unified_error_handler",
            "from unified_error_handling_system import get_unified_error_handler, ErrorCategory, ErrorSeverity"
        ),
        (
            r"import unified_error_logging_system",
            "from unified_error_handling_system import get_unified_error_handler, ErrorCategory, ErrorSeverity"
        )
    ]
    
    modified = False
    for pattern, replacement in replacements:
        if re.search(pattern, content):
            content = re.sub(pattern, replacement, content)
            modified = True
    
    if modified:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ 移行完了: {{file_path}}")
        return True
    
    return False

def main():
    """メイン処理"""
    project_root = Path(__file__).parent
    
    # 移行対象ファイル
    target_files = [
'''
        
        # 影響を受けるファイルの追加
        all_files = set()
        for files in usage_analysis.values():
            all_files.update(files)
        
        for file_path in sorted(all_files):
            script_content += f'        "{file_path}",\n'
        
        script_content += '''    ]
    
    migrated_count = 0
    for file_path in target_files:
        if os.path.exists(file_path):
            if migrate_imports(file_path):
                migrated_count += 1
    
    print(f"移行完了: {migrated_count}ファイル")
    print("移行後は手動でエラーハンドリングロジックを確認してください。")

if __name__ == "__main__":
    main()
'''
        
        # 移行スクリプトの保存
        script_file = self.project_root / "migrate_error_handling.py"
        with open(script_file, 'w', encoding='utf-8') as f:
            f.write(script_content)
        
        # 実行権限の付与
        os.chmod(script_file, 0o755)
        
        logger.info(f"✅ 移行スクリプトを作成しました: {script_file}")
        self.migration_log.append(f"移行スクリプト作成: {script_file}")

    def deprecate_legacy_files(self):
        """レガシーファイルの廃止処理"""
        logger.info("🗑️ レガシーファイルを廃止中...")
        
        for file_name in self.legacy_files:
            source_file = self.project_root / file_name
            if source_file.exists():
                # 廃止警告を追加
                deprecated_content = f'''#!/usr/bin/env python3
"""
⚠️ このファイルは廃止予定です

統合エラーハンドリングシステムへの移行が完了しました。
新しいシステム: unified_error_handling_system.py

移行ガイド: ERROR_HANDLING_MIGRATION_GUIDE.md
"""

import warnings

warnings.warn(
    "このファイルは廃止予定です。unified_error_handling_system.py を使用してください。",
    DeprecationWarning,
    stacklevel=2
)

# 旧システムのインポート（後方互換性のため）
try:
    from unified_error_handling_system import (
        get_unified_error_handler,
        ErrorCategory,
        ErrorSeverity
    )
except ImportError:
    # フォールバック処理
    def get_unified_error_handler():
        raise ImportError(
            "unified_error_handling_system.py が見つかりません。"
            "統合エラーハンドリングシステムをインストールしてください。"
        )
'''
                
                with open(source_file, 'w', encoding='utf-8') as f:
                    f.write(deprecated_content)
                
                logger.info(f"✅ 廃止処理完了: {file_name}")
                self.migration_log.append(f"廃止処理: {file_name}")

    def run_migration(self):
        """移行の実行"""
        logger.info("🚀 エラーハンドリングシステム移行を開始...")
        
        try:
            # 1. バックアップの作成
            self.create_backup()
            
            # 2. 使用状況の分析
            usage_analysis = self.analyze_usage()
            
            # 3. 移行ガイドの生成
            self.generate_migration_guide(usage_analysis)
            
            # 4. 移行スクリプトの作成
            self.create_migration_script(usage_analysis)
            
            # 5. レガシーファイルの廃止処理
            self.deprecate_legacy_files()
            
            # 6. 移行ログの保存
            self.save_migration_log()
            
            logger.info("✅ 移行処理が完了しました")
            logger.info("📋 次のステップ:")
            logger.info("  1. ERROR_HANDLING_MIGRATION_GUIDE.md を確認")
            logger.info("  2. migrate_error_handling.py を実行")
            logger.info("  3. 手動でエラーハンドリングロジックを確認")
            
        except Exception as e:
            logger.error(f"❌ 移行処理でエラーが発生しました: {e}")
            raise

    def save_migration_log(self):
        """移行ログの保存"""
        log_file = self.project_root / "error_handling_migration.log"
        
        with open(log_file, 'w', encoding='utf-8') as f:
            f.write("# エラーハンドリングシステム移行ログ\n\n")
            for log_entry in self.migration_log:
                f.write(f"- {log_entry}\n")
        
        logger.info(f"📝 移行ログを保存しました: {log_file}")


def main():
    """メイン処理"""
    project_root = os.getcwd()
    migration = ErrorHandlingMigration(project_root)
    migration.run_migration()


if __name__ == "__main__":
    main()
