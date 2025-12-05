import requests  # type: ignore
import urllib3

import user_setting as us

# 自己署名証明書の警告(InsecureRequestWarning)を非表示にする設定
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def create_redmine_ticket(date_str: str, target_users: dict, entered_users: dict) -> None:
    """Redmineにチケットを作成する"""

    missing_table_rows = []
    ok_table_rows = []

    for uid, name in target_users.items():
        if uid in entered_users:
            hours = entered_users[uid]
            # Textile形式の表の行を作成 (| 名前 | 時間 |)
            # 時間は .2f で小数2桁固定
            ok_table_rows.append(f'|{name}|{hours:.2f}|')
        else:
            missing_table_rows.append(f'|{name}|---|')

    # --- チケットの内容を作成 ---

    # 件名: 未入力者がいるかどうかで変える
    if missing_table_rows:
        subject = f'【未入力あり】作業時間入力チェック ({date_str})'
        priority_id = 2  # 通常(2)
    else:
        subject = f'【完了】作業時間入力チェック ({date_str})'
        priority_id = 1  # 低め(1)

    # 説明文
    description = f'h3. 対象日: {date_str}\n\n'

    header_row = '|_. 氏名 |_. 時間 |\n'

    if missing_table_rows:
        description += 'h4. ⚠️ 未入力のメンバー\n\n'
        description += '入力お願いします。\n\n'
        description += header_row
        description += '\n'.join(missing_table_rows) + '\n'
    else:
        description += 'h4. 🎉 全員の入力が完了しています\n'

    description += '\n'

    if ok_table_rows:
        description += 'h4. ✅ 入力済みのメンバー\n\n'
        description += '入力ありがとうございます。\n\n'
        description += header_row
        description += '\n'.join(ok_table_rows) + '\n'

    # --- チケット作成リクエスト ---
    payload = {
        'issue': {
            'project_id': us.TARGET_PROJECT_ID,
            'parent_issue_id': us.PARENT_TICKET_ID,
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
