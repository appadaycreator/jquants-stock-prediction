#!/usr/bin/env python3
"""
ユーザーフレンドリーなエラーメッセージシステム
技術的なエラーメッセージを分かりやすい日本語に変換
"""

from typing import Dict, Any, Optional, List
from enum import Enum
from dataclasses import dataclass
import re


class ErrorType(Enum):
    """エラータイプの定義"""
    
    CONNECTION_ERROR = "connection_error"
    DATA_ERROR = "data_error"
    MODEL_ERROR = "model_error"
    FILE_ERROR = "file_error"
    AUTHENTICATION_ERROR = "authentication_error"
    VALIDATION_ERROR = "validation_error"
    SYSTEM_ERROR = "system_error"
    API_ERROR = "api_error"
    NETWORK_ERROR = "network_error"
    PERMISSION_ERROR = "permission_error"


@dataclass
class UserFriendlyMessage:
    """ユーザーフレンドリーなメッセージ"""
    
    title: str
    description: str
    solution: str
    prevention: str
    severity: str
    icon: str


class UserFriendlyErrorMessages:
    """ユーザーフレンドリーなエラーメッセージシステム"""
    
    def __init__(self):
        """初期化"""
        self.error_messages = self._initialize_error_messages()
        self.patterns = self._initialize_error_patterns()
    
    def _initialize_error_messages(self) -> Dict[ErrorType, UserFriendlyMessage]:
        """エラーメッセージの初期化"""
        return {
            ErrorType.CONNECTION_ERROR: UserFriendlyMessage(
                title="接続エラーが発生しました",
                description="インターネット接続またはサーバーとの通信に問題があります。",
                solution="1. インターネット接続を確認してください\n2. しばらく時間をおいてから再度お試しください\n3. VPNを使用している場合は、一度切断してみてください",
                prevention="安定したインターネット環境でご利用ください",
                severity="medium",
                icon="🌐"
            ),
            ErrorType.DATA_ERROR: UserFriendlyMessage(
                title="データの処理に問題があります",
                description="株価データの読み込みや処理中にエラーが発生しました。",
                solution="1. データファイルが正しい形式か確認してください\n2. ファイルが破損していないか確認してください\n3. 必要に応じてデータを再取得してください",
                prevention="定期的にデータの整合性を確認してください",
                severity="high",
                icon="📊"
            ),
            ErrorType.MODEL_ERROR: UserFriendlyMessage(
                title="予測モデルの実行に問題があります",
                description="AI予測モデルの学習や予測処理中にエラーが発生しました。",
                solution="1. モデルの再学習を実行してください\n2. 入力データの形式を確認してください\n3. システム管理者にお問い合わせください",
                prevention="定期的にモデルの性能を監視してください",
                severity="high",
                icon="🤖"
            ),
            ErrorType.FILE_ERROR: UserFriendlyMessage(
                title="ファイルの操作に問題があります",
                description="ファイルの読み込み、書き込み、または削除中にエラーが発生しました。",
                solution="1. ファイルの存在とアクセス権限を確認してください\n2. ディスク容量が十分か確認してください\n3. ファイルが他のプログラムで使用されていないか確認してください",
                prevention="定期的にディスク容量とファイル権限を確認してください",
                severity="medium",
                icon="📁"
            ),
            ErrorType.AUTHENTICATION_ERROR: UserFriendlyMessage(
                title="認証に問題があります",
                description="APIキーや認証情報に問題があります。",
                solution="1. APIキーが正しいか確認してください\n2. 認証情報の有効期限を確認してください\n3. 必要に応じて新しい認証情報を取得してください",
                prevention="認証情報は安全に管理し、定期的に更新してください",
                severity="high",
                icon="🔐"
            ),
            ErrorType.VALIDATION_ERROR: UserFriendlyMessage(
                title="入力データに問題があります",
                description="入力されたデータの形式や内容に問題があります。",
                solution="1. 入力データの形式を確認してください\n2. 必須項目がすべて入力されているか確認してください\n3. データの範囲や制限を確認してください",
                prevention="入力時に入力チェック機能を活用してください",
                severity="low",
                icon="✅"
            ),
            ErrorType.SYSTEM_ERROR: UserFriendlyMessage(
                title="システムエラーが発生しました",
                description="システム内部で予期しないエラーが発生しました。",
                solution="1. システムを再起動してください\n2. しばらく時間をおいてから再度お試しください\n3. 問題が続く場合は、システム管理者にお問い合わせください",
                prevention="定期的にシステムのメンテナンスを実行してください",
                severity="critical",
                icon="⚠️"
            ),
            ErrorType.API_ERROR: UserFriendlyMessage(
                title="API呼び出しに問題があります",
                description="外部APIとの通信中にエラーが発生しました。",
                solution="1. APIの利用制限に達していないか確認してください\n2. APIのサービス状況を確認してください\n3. しばらく時間をおいてから再度お試しください",
                prevention="APIの利用制限を監視し、適切な間隔でリクエストを送信してください",
                severity="medium",
                icon="🔌"
            ),
            ErrorType.NETWORK_ERROR: UserFriendlyMessage(
                title="ネットワークエラーが発生しました",
                description="ネットワーク接続に問題があります。",
                solution="1. インターネット接続を確認してください\n2. ファイアウォール設定を確認してください\n3. プロキシ設定を確認してください",
                prevention="安定したネットワーク環境でご利用ください",
                severity="medium",
                icon="🌍"
            ),
            ErrorType.PERMISSION_ERROR: UserFriendlyMessage(
                title="アクセス権限に問題があります",
                description="ファイルやディレクトリへのアクセス権限が不足しています。",
                solution="1. ファイルのアクセス権限を確認してください\n2. 管理者権限で実行してください\n3. 必要に応じて権限を変更してください",
                prevention="適切なアクセス権限を設定してください",
                severity="medium",
                icon="🔒"
            )
        }
    
    def _initialize_error_patterns(self) -> Dict[str, ErrorType]:
        """エラーパターンの初期化"""
        return {
            # 接続エラー
            r".*connection.*error.*": ErrorType.CONNECTION_ERROR,
            r".*connection.*refused.*": ErrorType.CONNECTION_ERROR,
            r".*connection.*timeout.*": ErrorType.CONNECTION_ERROR,
            r".*connection.*reset.*": ErrorType.CONNECTION_ERROR,
            r".*connection.*aborted.*": ErrorType.CONNECTION_ERROR,
            r".*connection.*lost.*": ErrorType.CONNECTION_ERROR,
            r".*connection.*failed.*": ErrorType.CONNECTION_ERROR,
            r".*connection.*closed.*": ErrorType.CONNECTION_ERROR,
            r".*connection.*broken.*": ErrorType.CONNECTION_ERROR,
            r".*connection.*terminated.*": ErrorType.CONNECTION_ERROR,
            
            # データエラー
            r".*data.*error.*": ErrorType.DATA_ERROR,
            r".*data.*not.*found.*": ErrorType.DATA_ERROR,
            r".*data.*corrupted.*": ErrorType.DATA_ERROR,
            r".*data.*invalid.*": ErrorType.DATA_ERROR,
            r".*data.*format.*": ErrorType.DATA_ERROR,
            r".*data.*type.*": ErrorType.DATA_ERROR,
            r".*data.*missing.*": ErrorType.DATA_ERROR,
            r".*data.*empty.*": ErrorType.DATA_ERROR,
            r".*data.*null.*": ErrorType.DATA_ERROR,
            r".*data.*nan.*": ErrorType.DATA_ERROR,
            
            # モデルエラー
            r".*model.*error.*": ErrorType.MODEL_ERROR,
            r".*model.*not.*found.*": ErrorType.MODEL_ERROR,
            r".*model.*failed.*": ErrorType.MODEL_ERROR,
            r".*model.*training.*": ErrorType.MODEL_ERROR,
            r".*model.*prediction.*": ErrorType.MODEL_ERROR,
            r".*model.*inference.*": ErrorType.MODEL_ERROR,
            r".*model.*loading.*": ErrorType.MODEL_ERROR,
            r".*model.*saving.*": ErrorType.MODEL_ERROR,
            r".*model.*serialization.*": ErrorType.MODEL_ERROR,
            r".*model.*deserialization.*": ErrorType.MODEL_ERROR,
            
            # ファイルエラー
            r".*file.*error.*": ErrorType.FILE_ERROR,
            r".*file.*not.*found.*": ErrorType.FILE_ERROR,
            r".*file.*permission.*": ErrorType.FILE_ERROR,
            r".*file.*access.*": ErrorType.FILE_ERROR,
            r".*file.*read.*": ErrorType.FILE_ERROR,
            r".*file.*write.*": ErrorType.FILE_ERROR,
            r".*file.*open.*": ErrorType.FILE_ERROR,
            r".*file.*close.*": ErrorType.FILE_ERROR,
            r".*file.*delete.*": ErrorType.FILE_ERROR,
            r".*file.*create.*": ErrorType.FILE_ERROR,
            
            # 認証エラー
            r".*authentication.*error.*": ErrorType.AUTHENTICATION_ERROR,
            r".*auth.*error.*": ErrorType.AUTHENTICATION_ERROR,
            r".*login.*error.*": ErrorType.AUTHENTICATION_ERROR,
            r".*password.*error.*": ErrorType.AUTHENTICATION_ERROR,
            r".*token.*error.*": ErrorType.AUTHENTICATION_ERROR,
            r".*key.*error.*": ErrorType.AUTHENTICATION_ERROR,
            r".*credential.*error.*": ErrorType.AUTHENTICATION_ERROR,
            r".*unauthorized.*": ErrorType.AUTHENTICATION_ERROR,
            r".*forbidden.*": ErrorType.AUTHENTICATION_ERROR,
            r".*access.*denied.*": ErrorType.AUTHENTICATION_ERROR,
            
            # バリデーションエラー
            r".*validation.*error.*": ErrorType.VALIDATION_ERROR,
            r".*invalid.*input.*": ErrorType.VALIDATION_ERROR,
            r".*invalid.*parameter.*": ErrorType.VALIDATION_ERROR,
            r".*invalid.*argument.*": ErrorType.VALIDATION_ERROR,
            r".*invalid.*value.*": ErrorType.VALIDATION_ERROR,
            r".*invalid.*format.*": ErrorType.VALIDATION_ERROR,
            r".*invalid.*type.*": ErrorType.VALIDATION_ERROR,
            r".*invalid.*range.*": ErrorType.VALIDATION_ERROR,
            r".*invalid.*length.*": ErrorType.VALIDATION_ERROR,
            r".*invalid.*size.*": ErrorType.VALIDATION_ERROR,
            
            # システムエラー
            r".*system.*error.*": ErrorType.SYSTEM_ERROR,
            r".*internal.*error.*": ErrorType.SYSTEM_ERROR,
            r".*server.*error.*": ErrorType.SYSTEM_ERROR,
            r".*runtime.*error.*": ErrorType.SYSTEM_ERROR,
            r".*fatal.*error.*": ErrorType.SYSTEM_ERROR,
            r".*critical.*error.*": ErrorType.SYSTEM_ERROR,
            r".*unexpected.*error.*": ErrorType.SYSTEM_ERROR,
            r".*unknown.*error.*": ErrorType.SYSTEM_ERROR,
            r".*general.*error.*": ErrorType.SYSTEM_ERROR,
            r".*default.*error.*": ErrorType.SYSTEM_ERROR,
            
            # APIエラー
            r".*api.*error.*": ErrorType.API_ERROR,
            r".*api.*failed.*": ErrorType.API_ERROR,
            r".*api.*timeout.*": ErrorType.API_ERROR,
            r".*api.*limit.*": ErrorType.API_ERROR,
            r".*api.*quota.*": ErrorType.API_ERROR,
            r".*api.*rate.*": ErrorType.API_ERROR,
            r".*api.*throttle.*": ErrorType.API_ERROR,
            r".*api.*blocked.*": ErrorType.API_ERROR,
            r".*api.*banned.*": ErrorType.API_ERROR,
            r".*api.*suspended.*": ErrorType.API_ERROR,
            
            # ネットワークエラー
            r".*network.*error.*": ErrorType.NETWORK_ERROR,
            r".*network.*timeout.*": ErrorType.NETWORK_ERROR,
            r".*network.*unreachable.*": ErrorType.NETWORK_ERROR,
            r".*network.*unavailable.*": ErrorType.NETWORK_ERROR,
            r".*network.*down.*": ErrorType.NETWORK_ERROR,
            r".*network.*offline.*": ErrorType.NETWORK_ERROR,
            r".*network.*disconnected.*": ErrorType.NETWORK_ERROR,
            r".*network.*interrupted.*": ErrorType.NETWORK_ERROR,
            r".*network.*unstable.*": ErrorType.NETWORK_ERROR,
            r".*network.*slow.*": ErrorType.NETWORK_ERROR,
            
            # 権限エラー
            r".*permission.*error.*": ErrorType.PERMISSION_ERROR,
            r".*permission.*denied.*": ErrorType.PERMISSION_ERROR,
            r".*access.*denied.*": ErrorType.PERMISSION_ERROR,
            r".*unauthorized.*": ErrorType.PERMISSION_ERROR,
            r".*forbidden.*": ErrorType.PERMISSION_ERROR,
            r".*restricted.*": ErrorType.PERMISSION_ERROR,
            r".*blocked.*": ErrorType.PERMISSION_ERROR,
            r".*locked.*": ErrorType.PERMISSION_ERROR,
            r".*protected.*": ErrorType.PERMISSION_ERROR,
            r".*secure.*": ErrorType.PERMISSION_ERROR
        }
    
    def get_user_friendly_message(self, error_message: str, error_type: Optional[ErrorType] = None) -> UserFriendlyMessage:
        """
        エラーメッセージからユーザーフレンドリーなメッセージを取得
        
        Args:
            error_message: 元のエラーメッセージ
            error_type: エラータイプ（指定された場合）
            
        Returns:
            UserFriendlyMessage: ユーザーフレンドリーなメッセージ
        """
        # エラータイプが指定されていない場合は自動判定
        if error_type is None:
            error_type = self._detect_error_type(error_message)
        
        # エラータイプに対応するメッセージを取得
        if error_type in self.error_messages:
            return self.error_messages[error_type]
        
        # デフォルトのシステムエラーメッセージ
        return self.error_messages[ErrorType.SYSTEM_ERROR]
    
    def _detect_error_type(self, error_message: str) -> ErrorType:
        """
        エラーメッセージからエラータイプを自動判定
        
        Args:
            error_message: エラーメッセージ
            
        Returns:
            ErrorType: 判定されたエラータイプ
        """
        error_message_lower = error_message.lower()
        
        # パターンマッチングでエラータイプを判定
        for pattern, error_type in self.patterns.items():
            if re.search(pattern, error_message_lower):
                return error_type
        
        # デフォルトはシステムエラー
        return ErrorType.SYSTEM_ERROR
    
    def format_error_message(self, error_message: str, error_type: Optional[ErrorType] = None) -> str:
        """
        エラーメッセージをフォーマット
        
        Args:
            error_message: 元のエラーメッセージ
            error_type: エラータイプ
            
        Returns:
            str: フォーマットされたエラーメッセージ
        """
        user_friendly = self.get_user_friendly_message(error_message, error_type)
        
        formatted_message = f"""
{user_friendly.icon} {user_friendly.title}

{user_friendly.description}

🔧 解決方法:
{user_friendly.solution}

🛡️ 予防策:
{user_friendly.prevention}

重要度: {user_friendly.severity.upper()}
        """.strip()
        
        return formatted_message
    
    def get_error_guidance(self, error_message: str, error_type: Optional[ErrorType] = None) -> Dict[str, Any]:
        """
        エラーガイダンスを取得
        
        Args:
            error_message: 元のエラーメッセージ
            error_type: エラータイプ
            
        Returns:
            Dict[str, Any]: エラーガイダンス情報
        """
        user_friendly = self.get_user_friendly_message(error_message, error_type)
        
        return {
            "title": user_friendly.title,
            "description": user_friendly.description,
            "solution": user_friendly.solution,
            "prevention": user_friendly.prevention,
            "severity": user_friendly.severity,
            "icon": user_friendly.icon,
            "original_error": error_message,
            "error_type": error_type.value if error_type else "unknown"
        }


# グローバルインスタンス
_user_friendly_error_messages = None


def get_user_friendly_error_messages() -> UserFriendlyErrorMessages:
    """
    ユーザーフレンドリーなエラーメッセージシステムの取得
    
    Returns:
        UserFriendlyErrorMessages: ユーザーフレンドリーなエラーメッセージシステム
    """
    global _user_friendly_error_messages
    
    if _user_friendly_error_messages is None:
        _user_friendly_error_messages = UserFriendlyErrorMessages()
    
    return _user_friendly_error_messages


def format_error_for_user(error_message: str, error_type: Optional[ErrorType] = None) -> str:
    """
    エラーメッセージをユーザーフレンドリーにフォーマット
    
    Args:
        error_message: 元のエラーメッセージ
        error_type: エラータイプ
        
    Returns:
        str: フォーマットされたエラーメッセージ
    """
    error_messages = get_user_friendly_error_messages()
    return error_messages.format_error_message(error_message, error_type)


def get_error_guidance_for_user(error_message: str, error_type: Optional[ErrorType] = None) -> Dict[str, Any]:
    """
    ユーザー向けエラーガイダンスを取得
    
    Args:
        error_message: 元のエラーメッセージ
        error_type: エラータイプ
        
    Returns:
        Dict[str, Any]: エラーガイダンス情報
    """
    error_messages = get_user_friendly_error_messages()
    return error_messages.get_error_guidance(error_message, error_type)


if __name__ == "__main__":
    # テスト実行
    error_messages = get_user_friendly_error_messages()
    
    # テストケース
    test_errors = [
        "ConnectionError: Failed to establish connection",
        "FileNotFoundError: No such file or directory",
        "ValueError: Invalid data format",
        "AuthenticationError: Invalid API key",
        "ModelError: Failed to load model",
        "NetworkError: Connection timeout",
        "PermissionError: Access denied",
        "ValidationError: Invalid input parameter",
        "APIError: Rate limit exceeded",
        "SystemError: Unexpected internal error"
    ]
    
    print("🧪 ユーザーフレンドリーなエラーメッセージテスト")
    print("=" * 60)
    
    for error in test_errors:
        print(f"\n元のエラー: {error}")
        print("-" * 40)
        formatted = error_messages.format_error_message(error)
        print(formatted)
        print("=" * 60)
