"""
Redmineにチケットを作成するモジュール
作業時間入力チェック結果を整形してチケットとして登録する
"""

import requests  # type: ignore
import urllib3

import user_setting as us

# 自己署名証明書の警告(InsecureRequestWarning)を非表示にする設定
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Textile形式の表ヘッダー
USER_TABLE_HEADER = '|_. 氏名 |_. 時間 |\n'
PROJECT_TABLE_HEADER = '|_. プロジェクト名 |_. 合計時間 |\n'


def _build_user_table_rows(target_users: dict, entered_users: dict) -> tuple[list, list]:
    """
    ユーザーの入力状況テーブル行を生成する

    Args:
        target_users: 対象ユーザーの辞書 {ID: 名前}
        entered_users: 入力済みユーザーの辞書 {ID: 時間}

    Returns:
        (未入力者の行リスト, 入力済み者の行リスト)
    """
    missing_rows = []
    ok_rows = []

    for uid, name in target_users.items():
        if uid in entered_users:
            hours = entered_users[uid]
            ok_rows.append(f'|{name}|{hours:.2f}|')
        else:
            missing_rows.append(f'|{name}|---|')

    return missing_rows, ok_rows


def _build_project_table_rows(entered_projects: dict) -> list:
    """
    プロジェクト別集計テーブル行を生成する

    Args:
        entered_projects: プロジェクト別集計の辞書 {プロジェクト名: 時間}

    Returns:
        テーブル行のリスト
    """
    return [f'|{prj_name}|{hours:.2f}|' for prj_name, hours in entered_projects.items()]


def _build_description(date_str: str, missing_rows: list, ok_rows: list, project_rows: list) -> str:
    """
    Redmineチケットの説明欄を生成する

    Args:
        date_str: 対象日付
        missing_rows: 未入力者のテーブル行
        ok_rows: 入力済み者のテーブル行
        project_rows: プロジェクト別集計のテーブル行

    Returns:
        Textile形式の説明文
    """
    description = f'h3. 対象日: {date_str}\n\n'

    # 未入力者セクション
    if missing_rows:
        description += 'h4. 未入力のメンバー\n\n'
        description += '入力お願いします。\n\n'
        description += USER_TABLE_HEADER
        description += '\n'.join(missing_rows) + '\n'
    else:
        description += 'h4. 全員の入力が完了しています\n'

    description += '\n'

    # 入力済み者セクション
    if ok_rows:
        description += 'h4. 入力済みのメンバー\n\n'
        description += USER_TABLE_HEADER
        description += '\n'.join(ok_rows) + '\n'

    # プロジェクト別集計セクション
    if project_rows:
        description += '\n'
        description += 'h4. プロジェクト別集計\n\n'
        description += PROJECT_TABLE_HEADER
        description += '\n'.join(project_rows) + '\n'

    return description


def _get_subject_and_priority(missing_rows: list, date_str: str) -> tuple[str, int]:
    """
    チケットの件名と優先度を決定する

    Args:
        missing_rows: 未入力者のテーブル行
        date_str: 対象日付

    Returns:
        (件名, 優先度ID)
    """
    if missing_rows:
        return f'【未入力あり】{us.SUBJECT_KEYWORD} ({date_str})', 1  # 低め
    else:
        return f'【完了】{us.SUBJECT_KEYWORD} ({date_str})', 1  # 低め


def create_redmine_ticket(
    date_str: str,
    target_users: dict,
    entered_users: dict,
    entered_projects: dict,
) -> None:
    """
    Redmineにチケットを作成し、未入力者をウォッチャーに追加する

    Args:
        date_str: 対象日付 (YYYY-MM-DD形式)
        target_users: チェック対象ユーザー {ID: 名前}
        entered_users: 入力済みユーザー {ID: 時間}
        entered_projects: プロジェクト別集計 {プロジェクト名: 時間}
    """
    # テーブル行の生成
    missing_rows, ok_rows = _build_user_table_rows(target_users, entered_users)
    project_rows = _build_project_table_rows(entered_projects)

    # チケット件名と優先度の決定
    subject, priority_id = _get_subject_and_priority(missing_rows, date_str)

    # 説明文の生成
    description = _build_description(date_str, missing_rows, ok_rows, project_rows)

    # ウォッチャーに追加するユーザーID
    missing_user_ids = [int(uid) for uid, name in target_users.items() if uid not in entered_users]

    # チケット作成リクエストの構築
    payload = {
        'issue': {
            'project_id': us.TARGET_PROJECT_ID,
            'parent_issue_id': us.PARENT_TICKET_ID,
            'tracker_id': us.TRACKER_ID,
            'subject': subject,
            'description': description,
            'priority_id': priority_id,
            'watcher_user_ids': missing_user_ids,
        }
    }

    headers = {
        'X-Redmine-API-Key': us.REDMINE_API_KEY,
        'Content-Type': 'application/json',
    }

    print('Redmineチケットを作成中...')

    try:
        response = requests.post(
            f'{us.REDMINE_URL}/issues.json',
            json=payload,
            headers=headers,
            verify=False,
        )
        response.raise_for_status()

        new_issue = response.json()
        issue_id = new_issue['issue']['id']
        print(f'チケット作成成功! Issue ID: {issue_id}')

        if missing_user_ids:
            print(f'ウォッチャー追加数: {len(missing_user_ids)}名')

    except Exception as e:
        print(f'チケット作成エラー: {e}')
        if 'response' in locals():
            print(response.text)
