import check_yesterday_time


def main() -> None:
    target_date, t_users, e_users = check_yesterday_time.get_redmine_data()

    if target_date is None:
        print('target_date is None')
        return

    if t_users is None:
        print('target_date is None')
        return

    if e_users is None:
        print('target_date is None')
        return

    print(target_date, t_users, e_users)


if __name__ == '__main__':
    main()
