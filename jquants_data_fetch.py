import requests
import pandas as pd
import os
from dotenv import load_dotenv
from config_loader import get_config

# 環境変数から認証情報を読み込み
load_dotenv()
EMAIL = os.getenv("JQUANTS_EMAIL")
PASSWORD = os.getenv("JQUANTS_PASSWORD")

if not EMAIL or not PASSWORD:
    print("エラー: 環境変数 JQUANTS_EMAIL と JQUANTS_PASSWORD を設定してください。")
    print(".env ファイルを作成し、認証情報を設定してください。")
    exit(1)

# 1. リフレッシュトークンの取得
auth_url = "https://api.jquants.com/v1/token/auth_user"
auth_payload = {"mailaddress": EMAIL, "password": PASSWORD}
auth_response = requests.post(auth_url, json=auth_payload)

if auth_response.status_code != 200:
    print(f"リフレッシュトークン取得失敗: {auth_response.json()}")
    exit(1)

auth_data = auth_response.json()
if "refreshToken" not in auth_data:
    print(f"リフレッシュトークンが取得できませんでした。レスポンス: {auth_data}")
    exit(1)

refresh_token = auth_data["refreshToken"]
print("リフレッシュトークンを取得しました。")

# 2. IDトークンの取得
id_token_url = "https://api.jquants.com/v1/token/auth_refresh"
id_token_params = {"refreshtoken": refresh_token}
id_token_response = requests.post(id_token_url, params=id_token_params)

if id_token_response.status_code != 200:
    print(f"IDトークン取得失敗: {id_token_response.json()}")
    exit(1)

id_token_data = id_token_response.json()
if "idToken" not in id_token_data:
    print(f"IDトークンが取得できませんでした。レスポンス: {id_token_data}")
    exit(1)

id_token = id_token_data["idToken"]
print("IDトークンを取得しました。")

# 設定ファイルを読み込み
config = get_config()
jquants_config = config.get_jquants_config()
data_fetch_config = config.get_data_fetch_config()

# 3. 株価データの取得
headers = {"Authorization": f"Bearer {id_token}"}
price_url = f"{jquants_config.get('base_url', 'https://api.jquants.com/v1')}/prices/daily_quotes"
params = {"date": data_fetch_config.get('target_date', '20240301')}

print(f"データ取得を開始します: {params['date']}")
response = requests.get(price_url, headers=headers, params=params)

if response.status_code != 200:
    print(f"データ取得失敗: {response.json()}")
    exit(1)

data = response.json()
df = pd.DataFrame(data["daily_quotes"])
output_file = data_fetch_config.get('output_file', 'stock_data.csv')
df.to_csv(output_file, index=False)
print(f"データを '{output_file}' に保存しました。取得件数: {len(df)}件")
