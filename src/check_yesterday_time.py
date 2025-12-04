import datetime

import requests
import urllib3

import user_setting as us

# 自己署名証明書の警告(InsecureRequestWarning)を非表示にする設定
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def get_redmine_data():
    """特定プロジェクトのメンバーと昨日の作業時間を取得する"""
    headers = {'X-Redmine-API-Key': us.REDMINE_API_KEY}
    request_opts = {'headers': headers, 'verify': False}

    yesterday = datetime.date.today() - datetime.timedelta(days=1)
    str_date = yesterday.strftime('%Y-%m-%d')

    print(f'--- {str_date} のデータを取得中 ---')

    try:
        # メンバー取得
        members_resp = requests.get(f'{us.REDMINE_URL}/projects/{us.TARGET_PROJECT_ID}/memberships.json', params={'limit': 100}, **request_opts)
        members_resp.raise_for_status()

        target_users = {}
        for m in members_resp.json()['memberships']:
            if 'user' in m:
                target_users[m['user']['id']] = m['user']['name']

        # 作業時間取得
        entries_resp = requests.get(f'{us.REDMINE_URL}/time_entries.json', params={'spent_on': str_date, 'limit': 100}, **request_opts)
        entries_resp.raise_for_status()
        entries = entries_resp.json()['time_entries']

    except Exception as e:
        print(f'データ取得エラー: {e}')
        return None, None, None

    # 集計
    entered_users = {}
    for entry in entries:
        uid = entry['user']['id']
        if uid in target_users:
            entered_users[uid] = entered_users.get(uid, 0) + entry['hours']

    return str_date, target_users, entered_users


def create_redmine_ticket(date_str, target_users, entered_users):
    """Redmineにチケットを作成する"""
    if target_users is None:
        return

    missing_names = []
    ok_lines = []

    for uid, name in target_users.items():
        if uid in entered_users:
            hours = entered_users[uid]
            ok_lines.append(f'- {name}: {hours}h')
        else:
            missing_names.append(f'- {name}')

    # --- チケットの内容を作成 ---

    # 件名: 未入力者がいるかどうかで変える
    if missing_names:
        subject = f'【未入力あり】作業時間入力チェック ({date_str})'
        priority_id = 2  # 通常(2) または 高め(3)
    else:
        subject = f'【完了】作業時間入力チェック ({date_str})'
        priority_id = 1  # 低め(1) ※環境によります

    # 説明文 (RedmineはTextile記法が標準ですが、Markdownの場合もあります。シンプルな箇条書きにします)
    description = f'h3. 対象日: {date_str}\n\n'

    if missing_names:
        description += 'h4. ⚠️ 未入力のメンバー\n\n'
        description += '\n'.join(missing_names) + '\n\n'
        description += '※速やかに入力をお願いします。\n\n'
    else:
        description += 'h4. 🎉 全員の入力が完了しています\n\n'

    if ok_lines:
        description += 'h4. ✅ 入力済みのメンバー\n\n'
        description += '\n'.join(ok_lines) + '\n'

    # --- チケット作成リクエスト ---
    payload = {
        'issue': {
            'project_id': us.TARGET_PROJECT_ID,
            'tracker_id': us.TRACKER_ID,
            'subject': subject,
            'description': description,
            'priority_id': priority_id,
        }
    }

    headers = {'X-Redmine-API-Key': us.REDMINE_API_KEY, 'Content-Type': 'application/json'}

    print('Redmineチケットを作成中...')

    try:
        response = requests.post(f'{us.REDMINE_URL}/issues.json', json=payload, headers=headers, verify=False)
        response.raise_for_status()

        new_issue = response.json()
        print(f'チケット作成成功! Issue ID: {new_issue["issue"]["id"]}')

    except Exception as e:
        print(f'チケット作成エラー: {e}')
        if 'response' in locals():
            print(response.text)


if __name__ == '__main__':
    target_date, t_users, e_users = get_redmine_data()
    if target_date:
        create_redmine_ticket(target_date, t_users, e_users)
