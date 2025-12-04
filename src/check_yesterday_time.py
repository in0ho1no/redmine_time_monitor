import datetime

import requests
import urllib3

import user_setting as us

# 自己署名証明書の警告(InsecureRequestWarning)を非表示にする設定
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def get_redmine_data():
    """特定プロジェクトのメンバーと昨日の作業時間を取得する"""
    headers = {'X-Redmine-API-Key': us.REDMINE_API_KEY}

    # 証明書検証無効化オプション
    request_opts = {'headers': headers, 'verify': False}

    yesterday = datetime.date.today() - datetime.timedelta(days=1)
    str_date = yesterday.strftime('%Y-%m-%d')

    print(f'--- {str_date} のデータを取得中 (対象プロジェクト: {us.TARGET_PROJECT_ID}) ---')

    try:
        # 1. プロジェクトメンバーの取得
        # limit=100でメンバーを取得します
        members_resp = requests.get(f'{us.REDMINE_URL}/projects/{us.TARGET_PROJECT_ID}/memberships.json', params={'limit': 100}, **request_opts)
        members_resp.raise_for_status()

        # メンバーリストの作成
        # "user"キーがあるものだけ抽出(グループがメンバーの場合は除外または調整が必要)
        target_users = {}
        for m in members_resp.json()['memberships']:
            if 'user' in m:
                target_users[m['user']['id']] = m['user']['name']

        print(f'対象メンバー数: {len(target_users)} 名')

        # 2. 昨日の作業時間を取得
        # プロジェクトを絞らず、その人が「昨日どこかで作業したか」を見たい場合は project_id 指定なし
        # そのプロジェクトの作業のみを見たい場合は paramsに 'project_id': TARGET_PROJECT_ID を追加
        entries_resp = requests.get(f'{us.REDMINE_URL}/time_entries.json', params={'spent_on': str_date, 'limit': 100}, **request_opts)
        entries_resp.raise_for_status()
        entries = entries_resp.json()['time_entries']

    except Exception as e:
        print(f'Redmineデータ取得エラー: {e}')
        # 詳細なレスポンス内容を表示(デバッグ用)
        if 'members_resp' in locals() and members_resp.status_code != 200:
            print(f'Member API Response: {members_resp.text}')
        return None, None, None

    # 集計処理
    entered_users = {}  # {user_id: total_hours}
    for entry in entries:
        uid = entry['user']['id']
        hours = entry['hours']
        # 取得したメンバーリストに含まれる人のデータのみを集計
        if uid in target_users:
            entered_users[uid] = entered_users.get(uid, 0) + hours

    return str_date, target_users, entered_users
