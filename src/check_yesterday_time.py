import datetime

import requests
import urllib3

import user_setting as us

# 自己署名証明書の警告(InsecureRequestWarning)を非表示にする設定
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def get_redmine_data():
    """Redmineからユーザーと昨日の作業時間を取得する"""
    headers = {'X-Redmine-API-Key': us.REDMINE_API_KEY}

    yesterday = datetime.date.today() - datetime.timedelta(days=1)
    str_date = yesterday.strftime('%Y-%m-%d')

    # 共通の接続オプション (verify=False が重要)
    request_opts = {
        'headers': headers,
        'verify': False,  # <--- ここを追加！SSL証明書の検証を無視します
    }

    print(f'--- {str_date} のデータを取得中 ---')

    try:
        # 全アクティブユーザー取得
        users_resp = requests.get(
            f'{us.REDMINE_URL}/users.json',
            params={'status': 1, 'limit': 100},
            **request_opts,  # オプションを適用
        )
        users_resp.raise_for_status()
        all_users = {u['id']: f'{u["lastname"]} {u["firstname"]}' for u in users_resp.json()['users']}

        # 昨日の作業時間取得
        entries_resp = requests.get(
            f'{us.REDMINE_URL}/time_entries.json',
            params={'spent_on': str_date, 'limit': 100},
            **request_opts,  # オプションを適用
        )
        entries_resp.raise_for_status()
        entries = entries_resp.json()['time_entries']

    except Exception as e:
        print(f'Redmineデータ取得エラー: {e}')
        return None, None, None

    entered_users = {}  # {user_id: total_hours}
    for entry in entries:
        uid = entry['user']['id']
        hours = entry['hours']
        entered_users[uid] = entered_users.get(uid, 0) + hours

    return str_date, all_users, entered_users
