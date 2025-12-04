import datetime
from collections import defaultdict

import requests

import user_setting as us


def get_yesterday_time_entries():
    # 昨日の日付を取得
    yesterday = datetime.date.today() - datetime.timedelta(days=1)
    str_date = yesterday.strftime('%Y-%m-%d')

    print(f'--- {str_date} (昨日) の作業時間を取得中 ---')

    headers = {'X-Redmine-API-Key': us.API_KEY}

    # APIパラメータ: spent_onで日付指定, limit=100で多めに取得
    params = {'spent_on': str_date, 'limit': 100}

    try:
        response = requests.get(f'{us.REDMINE_URL}/time_entries.json', headers=headers, params=params)
        response.raise_for_status()
        data = response.json()

        entries = data['time_entries']

        if not entries:
            print('昨日の作業時間の入力はありません。')
            return

        # ユーザーごとの合計時間を集計
        user_totals = defaultdict(float)

        print(f'\n{"ユーザー名":<15} | {"プロジェクト":<15} | {"時間":<5} | {"コメント"}')
        print('-' * 60)

        for entry in entries:
            user_name = entry['user']['name']
            project_name = entry['project']['name']
            hours = entry['hours']
            comments = entry.get('comments', '')

            # 詳細出力
            print(f'{user_name:<15} | {project_name:<15} | {hours:<5} | {comments}')

            # 集計
            user_totals[user_name] += hours

        print('\n--- ユーザー別合計時間 ---')
        for user, total in user_totals.items():
            print(f'{user}: {total} 時間')

            # 8時間未満の場合に警告を出すなどのロジックも追加可能
            if total < 8.0:
                print(f'  -> ⚠️ {user} さんの入力時間が8時間未満です')

    except requests.exceptions.RequestException as e:
        print(f'エラーが発生しました: {e}')


if __name__ == '__main__':
    get_yesterday_time_entries()
