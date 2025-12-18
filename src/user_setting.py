"""
Redmineタイム監視ツールの設定ファイル
全体で使用される定数やAPI設定をここに集約する
"""

# === Redmine接続設定 ===
REDMINE_URL = 'https://your-redmine-url.com'  # RedmineのURL
REDMINE_API_KEY = 'YOUR_API_KEY'  # RedmineのAPIキー

# === プロジェクト設定 ===
# 対象プロジェクトの識別子 (URLの projects/ の後ろにある文字列)
# 例: https://.../projects/system_dev/settings -> 'system_dev'
TARGET_PROJECT_ID = 'test251115'

# === ターゲットユーザー設定 ===
# チェック対象のユーザーID(ユーザーは定期的に作業時間を入力すべき対象者)
TARGET_LIST = [
    6,  # 水城 瑞希
    7,  # 佐藤 陽翔
    8,  # 高橋 葵
    9,  # 山田 蓮
    10,  # 中村 光
]

# === チケット作成設定 ===
# 新規チケット作成時のトラッカーID
TRACKER_ID = 3

# 親チケットにしたいチケットID
PARENT_TICKET_ID = 44

# チケットの件名キーワード
SUBJECT_KEYWORD = '作業時間入力チェック'
