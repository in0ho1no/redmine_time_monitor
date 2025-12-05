import requests  # type: ignore
import urllib3

import user_setting as us

# 自己署名証明書の警告(InsecureRequestWarning)を非表示にする設定
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def create_redmine_ticket(date_str: str, target_users: dict, entered_users: dict) -> None:
    """Redmineにチケットを作成する"""

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
        priority_id = 2  # 通常(2)
    else:
        subject = f'【完了】作業時間入力チェック ({date_str})'
        priority_id = 1  # 低め(1)

    # 説明文
    description = f'h3. 対象日: {date_str}\n\n'

    if missing_names:
        description += 'h4. ⚠️ 未入力のメンバー\n\n'
        description += '\n'.join(missing_names) + '\n\n'
        description += '入力お願いします。\n\n'
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
