import datetime
import re

import requests  # type: ignore
import urllib3

import user_setting as us

# 自己署名証明書の警告(InsecureRequestWarning)を非表示にする設定
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def get_specific_date_time(specific_date: datetime.date) -> tuple[str | None, dict | None, dict | None, dict | None]:
    """
    特定プロジェクトのメンバーと指定日の作業時間を取得する
    Return: (日付文字列, 対象ユーザーdict, ユーザー別集計dict, プロジェクト別集計dict)
    """

    headers = {'X-Redmine-API-Key': us.REDMINE_API_KEY}
    request_opts = {'headers': headers, 'verify': False}

    str_date = specific_date.strftime('%Y-%m-%d')
    print(f'--- {str_date} のデータを取得中 ---')

    try:
        # メンバー取得
        members_resp = requests.get(f'{us.REDMINE_URL}/projects/{us.TARGET_PROJECT_ID}/memberships.json', params={'limit': 100}, **request_opts)
        members_resp.raise_for_status()

        target_users: dict = {}
        for m in members_resp.json()['memberships']:
            if 'user' in m:
                target_users[m['user']['id']] = m['user']['name']

        # 作業時間取得
        entries_resp = requests.get(f'{us.REDMINE_URL}/time_entries.json', params={'spent_on': str_date, 'limit': 100}, **request_opts)
        entries_resp.raise_for_status()
        entries = entries_resp.json()['time_entries']

    except Exception as e:
        print(f'データ取得エラー: {e}')
        return None, None, None, None

    # --- 集計 ---
    entered_users: dict = {}
    project_totals: dict = {}

    for entry in entries:
        uid = entry['user']['id']

        # ターゲットプロジェクトのメンバーによる入力のみを集計対象とする
        if uid in target_users:
            hours = entry['hours']

            # 1. ユーザー単位の集計
            entered_users[uid] = entered_users.get(uid, 0) + hours

            # 2. プロジェクト単位の集計
            prj_name = entry['project']['name']
            project_totals[prj_name] = project_totals.get(prj_name, 0) + hours

    return str_date, target_users, entered_users, project_totals


def get_last_target_date() -> datetime.date:
    """Redmine上の最新のチェックチケットから、最後にチェックした日付を取得する"""
    headers = {'X-Redmine-API-Key': us.REDMINE_API_KEY}

    # 件名にキーワードを含み、作成日時の降順で1件だけ取得
    params = {
        'project_id': us.TARGET_PROJECT_ID,
        'subject': f'~{us.SUBJECT_KEYWORD}',  # ~ は「含む」検索
        'tracker_id': us.TRACKER_ID,
        'limit': 1,
        'sort': 'created_on:desc',
    }

    yesterday = datetime.date.today() - datetime.timedelta(days=1)

    try:
        resp = requests.get(f'{us.REDMINE_URL}/issues.json', headers=headers, params=params, verify=False)
        resp.raise_for_status()
        issues = resp.json()['issues']

        if not issues:
            print('過去のチェックチケットが見つかりません。デフォルトとして「昨日」を返します。')
            return yesterday

        # 最新チケットの件名
        subject = issues[0]['subject']
        # 正規表現で (yyyy-mm-dd) を抽出
        match = re.search(r'\((\d{4}-\d{2}-\d{2})\)', subject)

        if match:
            last_date_str = match.group(1)
            print(f'前回のチェック対象日を特定しました: {last_date_str}')

            # 前回作成から次の日を対象とする
            last_date = datetime.datetime.strptime(last_date_str, '%Y-%m-%d').date() + datetime.timedelta(days=1)
            if last_date == datetime.date.today():
                # 今日になってしまった場合は昨日の日付を返す
                last_date = yesterday
            return last_date
        else:
            print('チケットは見つかりましたが、日付の解析に失敗しました。昨日を返します。')
            return yesterday

    except Exception as e:
        print(f'前回日付の取得エラー: {e}')
        # エラー時は安全のため「昨日」のみチェックするようにする
        return yesterday
