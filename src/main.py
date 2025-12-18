import argparse
import datetime

import check_specific_time
import create_redmine_ticket
import user_setting as us


def _validate_data(target_date: str | None, colect_users: dict | None, e_users: dict | None, e_projs: dict | None) -> bool:
    """
    取得したデータが有効かどうかを検証する

    Args:
        target_date: 対象日付
        colect_users: 対象ユーザー辞書
        e_users: 入力済みユーザーの集計
        e_projs: プロジェクト別集計

    Returns:
        全てのデータが有効な場合True、それ以外はFalse
    """
    validation_errors = []

    if target_date is None:
        validation_errors.append('エラー: 対象日付が取得できません')

    if colect_users is None:
        validation_errors.append('エラー: 対象ユーザーリストが取得できません')

    if e_users is None:
        validation_errors.append('エラー: ユーザー別集計が取得できません')

    if e_projs is None:
        validation_errors.append('エラー: プロジェクト別集計が取得できません')

    for error in validation_errors:
        print(error)

    return len(validation_errors) == 0


def main() -> None:
    """メイン処理: 前回チェック日の翌日を対象として、Redmineチケットを作成する"""
    # 前回のチェック対象日の翌日を取得
    specific_date = check_specific_time.get_last_target_date()
    target_date, colect_users, e_users, e_projs = check_specific_time.get_specific_date_time(specific_date)

    # データの妥当性チェック
    if not _validate_data(target_date, colect_users, e_users, e_projs):
        return

    # ターゲットユーザーのみを抽出
    target_user = {k: colect_users[k] for k in us.TARGET_LIST if k in colect_users}

    print(f'チェック対象日: {target_date}')
    print(f'ターゲットユーザー数: {len(target_user)}')
    print(f'入力済みユーザー数: {len(e_users)}')

    # Redmineチケットを作成
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
