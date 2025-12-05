REDMINE_URL = 'https://your-redmine-url.com'  # RedmineのURL
REDMINE_API_KEY = 'YOUR_API_KEY'  # RedmineのAPIキー

# 対象プロジェクトの識別子 (URLの projects/ の後ろにある文字列)
# 例: https://.../projects/system_dev/settings -> 'system_dev'
TARGET_PROJECT_ID = 'projects'

# 新規チケット作成する際のトラッカー指定
TRACKER_ID = 3

# requestのオプション
HEADERS = {'X-Redmine-API-Key': REDMINE_API_KEY}
REQUEST_OPTS = {'headers': HEADERS, 'verify': False}
