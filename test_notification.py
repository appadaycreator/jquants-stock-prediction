#!/usr/bin/env python3
"""
通知テストスクリプト
メール/Slack通知のテスト機能
"""

import sys
import yaml
import smtplib
import requests
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

def load_notification_config():
    """通知設定の読み込み"""
    try:
        with open('notification_config.yaml', 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        return config.get('notification', {})
    except FileNotFoundError:
        print("設定ファイルが見つかりません")
        return {}
    except Exception as e:
        print(f"設定読み込みエラー: {e}")
        return {}

def test_email_notification(config):
    """メール通知のテスト"""
    email_config = config.get('email', {})
    
    if not email_config.get('enabled', False):
        print("メール通知が無効です")
        return False
    
    try:
        # テストメールの作成
        msg = MIMEMultipart()
        msg['From'] = email_config.get('email_user', '')
        msg['To'] = email_config.get('email_to', '')
        msg['Subject'] = f"株価分析通知テスト - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        
        body = """
これは株価分析システムの通知テストです。

テスト内容:
- メール通知機能の動作確認
- 設定の妥当性チェック
- 送信機能のテスト

このメールが届いていれば、メール通知機能は正常に動作しています。

詳細はダッシュボードでご確認ください。
        """
        
        msg.attach(MIMEText(body, 'plain', 'utf-8'))
        
        # SMTPサーバーに接続してメール送信
        server = smtplib.SMTP(email_config.get('smtp_server', 'smtp.gmail.com'), 
                             email_config.get('smtp_port', 587))
        server.starttls()
        server.login(email_config.get('email_user', ''), 
                     email_config.get('email_password', ''))
        server.send_message(msg)
        server.quit()
        
        print("メール通知テストが成功しました")
        return True
        
    except Exception as e:
        print(f"メール通知テストエラー: {e}")
        return False

def test_slack_notification(config):
    """Slack通知のテスト"""
    slack_config = config.get('slack', {})
    
    if not slack_config.get('enabled', False):
        print("Slack通知が無効です")
        return False
    
    try:
        webhook_url = slack_config.get('webhook_url', '')
        if not webhook_url:
            print("Slack Webhook URLが設定されていません")
            return False
        
        # テストメッセージの作成
        payload = {
            "channel": slack_config.get('channel', '#stock-analysis'),
            "username": slack_config.get('username', '株価分析Bot'),
            "icon_emoji": slack_config.get('icon_emoji', ':chart_with_upwards_trend:'),
            "text": "株価分析通知テスト",
            "attachments": [{
                "color": "good",
                "title": "✅ 通知テスト成功",
                "text": f"テスト実行時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\nこれは株価分析システムの通知テストです。\nこのメッセージが表示されていれば、Slack通知機能は正常に動作しています。",
                "footer": "J-Quants株価予測システム",
                "ts": int(datetime.now().timestamp())
            }]
        }
        
        response = requests.post(webhook_url, json=payload)
        response.raise_for_status()
        
        print("Slack通知テストが成功しました")
        return True
        
    except Exception as e:
        print(f"Slack通知テストエラー: {e}")
        return False

def main():
    """メイン関数"""
    if len(sys.argv) < 2:
        print("使用方法: python3 test_notification.py <email|slack>")
        sys.exit(1)
    
    notification_type = sys.argv[1].lower()
    
    if notification_type not in ['email', 'slack']:
        print("無効な通知タイプです。email または slack を指定してください。")
        sys.exit(1)
    
    # 設定の読み込み
    config = load_notification_config()
    
    if not config:
        print("通知設定を読み込めませんでした")
        sys.exit(1)
    
    # 通知テストの実行
    if notification_type == 'email':
        success = test_email_notification(config)
    elif notification_type == 'slack':
        success = test_slack_notification(config)
    
    if success:
        print(f"{notification_type}通知テストが完了しました")
        sys.exit(0)
    else:
        print(f"{notification_type}通知テストに失敗しました")
        sys.exit(1)

if __name__ == "__main__":
    main()
