import argparse
import datetime

import check_specific_time
import create_redmine_ticket
import user_setting as us

TARGET_LIST = [
    6,  # '水城 瑞希
    7,  # '佐藤 陽翔'
    8,  # '高橋 葵'
    9,  # '山田 蓮'
    10,  # '中村 光'
]


def get_yesterday() -> datetime.date:
    """昨日のdatetime.dateオブジェクトを取得する"""
    return datetime.date.today() - datetime.timedelta(days=1)


def get_specific_date(year: int, month: int, day: int) -> datetime.date:
    """指定された年・月・日のdatetime.dateオブジェクトを取得する"""
    return datetime.date(year, month, day)


def main() -> None:
    # specific_date = get_yesterday()
    specific_date = check_specific_time.get_last_target_date()
    target_date, colect_users, e_users, e_projs = check_specific_time.get_specific_date_time(specific_date)

    if target_date is None:
        print('target_date is None')
        return

    if colect_users is None:
        print('t_usecolect_usersrs is None')
        return

    target_user = {k: colect_users[k] for k in TARGET_LIST if k in colect_users}
    if target_user is None:
        print('target_user is None')
        return

    if e_users is None:
        print('e_users is None')
        return

    if e_projs is None:
        print('e_projs is None')
        return

    print(target_date, target_user, e_users)
    create_redmine_ticket.create_redmine_ticket(target_date, target_user, e_users, e_projs)


if __name__ == '__main__':
    # 引数の解析処理
    parser = argparse.ArgumentParser(description='Redmine作業時間チェックツール')
    parser.add_argument('api_key', help='RedmineのAPIキーを指定してください')

    try:
        args = parser.parse_args()

        # 取得した引数で更新
        us.REDMINE_API_KEY = args.api_key

        # メイン処理実行
        main()

    except SystemExit:
        # 引数不足などで終了した場合
        pass
