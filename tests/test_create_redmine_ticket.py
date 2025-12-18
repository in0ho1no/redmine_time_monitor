"""create_redmine_ticket モジュールのテスト"""

from unittest.mock import MagicMock

import pytest

import create_redmine_ticket


class TestBuildUserTableRows:
    """_build_user_table_rows 関数のテスト"""

    def test_with_missing_and_ok_users(self):
        """未入力と入力済みユーザーが混在"""
        target_users = {6: '水城 瑞希', 7: '佐藤 陽翔', 8: '高橋 葵'}
        entered_users = {6: 8.0, 8: 6.0}

        # 実行
        missing_rows, ok_rows = create_redmine_ticket._build_user_table_rows(target_users, entered_users)

        # 検証
        assert len(missing_rows) == 1  # ユーザー7
        assert len(ok_rows) == 2  # ユーザー6, 8
        assert '|水城 瑞希|8.00|' in ok_rows
        assert '|佐藤 陽翔|---|' in missing_rows

    def test_all_users_entered(self):
        """全員入力済み"""
        target_users = {6: '水城 瑞希', 7: '佐藤 陽翔'}
        entered_users = {6: 8.0, 7: 7.5}

        # 実行
        missing_rows, ok_rows = create_redmine_ticket._build_user_table_rows(target_users, entered_users)

        # 検証
        assert len(missing_rows) == 0
        assert len(ok_rows) == 2

    def test_no_users_entered(self):
        """全員未入力"""
        target_users = {6: '水城 瑞希', 7: '佐藤 陽翔'}
        entered_users = {}

        # 実行
        missing_rows, ok_rows = create_redmine_ticket._build_user_table_rows(target_users, entered_users)

        # 検証
        assert len(missing_rows) == 2
        assert len(ok_rows) == 0


class TestBuildProjectTableRows:
    """_build_project_table_rows 関数のテスト"""

    def test_with_projects(self):
        """複数プロジェクトの集計"""
        entered_projects = {
            'Project A': 15.5,
            'Project B': 8.0,
            'Project C': 5.5,
        }

        # 実行
        result = create_redmine_ticket._build_project_table_rows(entered_projects)

        # 検証
        assert len(result) == 3
        assert '|Project A|15.50|' in result
        assert '|Project B|8.00|' in result

    def test_empty_projects(self):
        """プロジェクトなし"""
        entered_projects = {}

        # 実行
        result = create_redmine_ticket._build_project_table_rows(entered_projects)

        # 検証
        assert result == []


class TestBuildDescription:
    """_build_description 関数のテスト"""

    def test_with_missing_users(self):
        """未入力者がいる場合"""
        missing_rows = ['|佐藤 陽翔|---|']
        ok_rows = ['|水城 瑞希|8.00|', '|高橋 葵|6.00|']
        project_rows = ['|Project A|14.00|']

        # 実行
        result = create_redmine_ticket._build_description('2025-12-18', missing_rows, ok_rows, project_rows)

        # 検証
        assert 'h3. 対象日: 2025-12-18' in result
        assert 'h4. 未入力のメンバー' in result
        assert 'h4. 入力済みのメンバー' in result
        assert 'h4. プロジェクト別集計' in result
        assert '|佐藤 陽翔|---|' in result

    def test_without_missing_users(self):
        """全員入力済みの場合"""
        missing_rows = []
        ok_rows = ['|水城 瑞希|8.00|']
        project_rows = []

        # 実行
        result = create_redmine_ticket._build_description('2025-12-18', missing_rows, ok_rows, project_rows)

        # 検証
        assert 'h4. 全員の入力が完了しています' in result
        assert 'h4. 未入力のメンバー' not in result


class TestGetSubjectAndPriority:
    """_get_subject_and_priority 関数のテスト"""

    def test_with_missing_users(self):
        """未入力者がいる場合"""
        missing_rows = ['|user|---|']

        # 実行
        subject, priority_id = create_redmine_ticket._get_subject_and_priority(missing_rows, '2025-12-18')

        # 検証
        assert '【未入力あり】' in subject
        assert priority_id == 1  # 実装では両方1に統一されている

    def test_without_missing_users(self):
        """全員入力済みの場合"""
        missing_rows = []

        # 実行
        subject, priority_id = create_redmine_ticket._get_subject_and_priority(missing_rows, '2025-12-18')

        # 検証
        assert '【完了】' in subject
        assert priority_id == 1  # 低め


class TestCreateRedmineTicket:
    """create_redmine_ticket 関数のテスト"""

    def test_success_with_missing_users(self, mock_requests_post, sample_create_issue_response, mock_redmine_api_key, capfd):
        """未入力者がいる場合、チケット作成成功"""
        mock_response = MagicMock()
        mock_response.json.return_value = sample_create_issue_response
        mock_response.raise_for_status.return_value = None
        mock_requests_post.return_value = mock_response

        # データ準備
        target_users = {6: '水城 瑞希', 7: '佐藤 陽翔'}
        entered_users = {6: 8.0}
        entered_projects = {'Project A': 8.0}

        # 実行
        create_redmine_ticket.create_redmine_ticket('2025-12-18', target_users, entered_users, entered_projects)

        # 検証：POST が呼び出されたか
        assert mock_requests_post.called
        call_args = mock_requests_post.call_args

        # チケット内容を確認
        payload = call_args.kwargs['json']
        assert '【未入力あり】' in payload['issue']['subject']
        assert payload['issue']['priority_id'] == 1  # 実装では常に1
        assert 7 in payload['issue']['watcher_user_ids']  # ユーザー7は未入力

        # ログ出力を確認
        captured = capfd.readouterr()
        assert 'チケット作成成功' in captured.out

    def test_success_without_missing_users(self, mock_requests_post, sample_create_issue_response, mock_redmine_api_key):
        """全員入力済み、チケット作成成功"""
        mock_response = MagicMock()
        mock_response.json.return_value = sample_create_issue_response
        mock_response.raise_for_status.return_value = None
        mock_requests_post.return_value = mock_response

        # データ準備
        target_users = {6: '水城 瑞希', 7: '佐藤 陽翔'}
        entered_users = {6: 8.0, 7: 7.5}
        entered_projects = {'Project A': 15.5}

        # 実行
        create_redmine_ticket.create_redmine_ticket('2025-12-18', target_users, entered_users, entered_projects)

        # 検証
        assert mock_requests_post.called
        call_args = mock_requests_post.call_args
        payload = call_args.kwargs['json']

        assert '【完了】' in payload['issue']['subject']
        assert payload['issue']['priority_id'] == 1
        assert payload['issue']['watcher_user_ids'] == []

    def test_api_error(self, mock_requests_post, mock_redmine_api_key, capfd):
        """API エラー時"""
        mock_requests_post.side_effect = Exception('API error')

        # データ準備
        target_users = {6: '水城 瑞希'}
        entered_users = {6: 8.0}
        entered_projects = {'Project A': 8.0}

        # 実行
        create_redmine_ticket.create_redmine_ticket('2025-12-18', target_users, entered_users, entered_projects)

        # 検証：エラーメッセージが出力される
        captured = capfd.readouterr()
        assert 'チケット作成エラー' in captured.out
