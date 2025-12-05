import datetime

import check_specific_time
import create_redmine_ticket

EXCLUDE_LIST = [
    5,  # new User1
]


def get_yesterday() -> datetime.date:
    """昨日のdatetime.dateオブジェクトを取得する"""
    return datetime.date.today() - datetime.timedelta(days=1)


def get_specific_date(year: int, month: int, day: int) -> datetime.date:
    """指定された年・月・日のdatetime.dateオブジェクトを取得する"""
    return datetime.date(year, month, day)


def main() -> None:
    specific_date = get_yesterday()
    target_date, t_users, e_users, e_projs = check_specific_time.get_specific_date_time(specific_date)

    if target_date is None:
        print('target_date is None')
        return

    if t_users is None:
        print('t_users is None')
        return

    for ex in EXCLUDE_LIST:
        if ex in t_users:
            t_users.pop(ex)

    if e_users is None:
        print('e_users is None')
        return

    if e_projs is None:
        print('e_projs is None')
        return

    print(target_date, t_users, e_users)
    create_redmine_ticket.create_redmine_ticket(target_date, t_users, e_users, e_projs)


if __name__ == '__main__':
    main()
