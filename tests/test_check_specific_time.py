"""check_specific_time モジュールのテスト"""

import datetime
from unittest.mock import MagicMock

import pytest

import check_specific_time


class TestGetProjectMembers:
    """_get_project_members 関数のテスト"""

    def test_success(self, mock_requests_get, sample_members_response, mock_redmine_api_key):
        """メンバー取得成功"""
        # モックレスポンスの設定
        mock_response = MagicMock()
        mock_response.json.return_value = sample_members_response
        mock_response.raise_for_status.return_value = None
        mock_requests_get.return_value = mock_response

        # 実行
        result = check_specific_time._get_project_members()

        # 検証
        assert result is not None
        assert result[6] == '水城 瑞希'
        assert result[7] == '佐藤 陽翔'
        assert len(result) == 5

    def test_api_error(self, mock_requests_get, mock_redmine_api_key, capfd):
        """API エラー時"""
        # モックレスポンスをエラー状態に設定
        mock_requests_get.side_effect = Exception('Network error')

        # 実行
        result = check_specific_time._get_project_members()

        # 検証
        assert result is None
        captured = capfd.readouterr()
        assert 'プロジェクトメンバー取得エラー' in captured.out


class TestGetTimeEntries:
    """_get_time_entries 関数のテスト"""

    def test_success(self, mock_requests_get, sample_time_entries_response, mock_redmine_api_key):
        """作業時間エントリ取得成功"""
        # モックレスポンスの設定
        mock_response = MagicMock()
        mock_response.json.return_value = sample_time_entries_response
        mock_response.raise_for_status.return_value = None
        mock_requests_get.return_value = mock_response

        # 実行
        result = check_specific_time._get_time_entries('2025-12-18')

        # 検証
        assert result is not None
        assert len(result) == 4
        assert result[0]['user']['id'] == 6
        assert result[0]['hours'] == 8.0

    def test_api_error(self, mock_requests_get, mock_redmine_api_key, capfd):
        """API エラー時"""
        mock_requests_get.side_effect = Exception('API error')

        # 実行
        result = check_specific_time._get_time_entries('2025-12-18')

        # 検証
        assert result is None
        captured = capfd.readouterr()
        assert '作業時間エントリ取得エラー' in captured.out


class TestAggregateEntries:
    """_aggregate_entries 関数のテスト"""

    def test_aggregate(self, sample_time_entries_response):
        """集計のテスト"""
        entries = sample_time_entries_response['time_entries']
        target_users = {6: '水城 瑞希', 7: '佐藤 陽翔', 8: '高橋 葵'}

        # 実行
        entered_users, project_totals = check_specific_time._aggregate_entries(entries, target_users)

        # 検証：ユーザー別集計
        assert entered_users[6] == 10.0  # 8.0 + 2.0
        assert entered_users[7] == 7.5
        assert entered_users[8] == 6.0

        # 検証：プロジェクト別集計
        assert project_totals['Project A'] == 15.5  # 8.0 + 7.5
        assert project_totals['Project B'] == 8.0  # 6.0 + 2.0

    def test_aggregate_empty_entries(self):
        """エントリが空の場合"""
        entries = []
        target_users = {6: '水城 瑞希'}

        # 実行
        entered_users, project_totals = check_specific_time._aggregate_entries(entries, target_users)

        # 検証
        assert entered_users == {}
        assert project_totals == {}

    def test_aggregate_filters_non_target_users(self, sample_time_entries_response):
        """ターゲット外ユーザーを除外"""
        entries = sample_time_entries_response['time_entries']
        # ユーザー6, 8 のみをターゲットに
        target_users = {6: '水城 瑞希', 8: '高橋 葵'}

        # 実行
        entered_users, project_totals = check_specific_time._aggregate_entries(entries, target_users)

        # 検証：ユーザー7はターゲット外なので集計されない
        assert 7 not in entered_users
        assert entered_users[6] == 10.0
        assert entered_users[8] == 6.0


class TestGetSpecificDateTime:
    """get_specific_date_time 関数のテスト"""

    def test_success(
        self,
        mock_requests_get,
        sample_members_response,
        sample_time_entries_response,
        mock_redmine_api_key,
    ):
        """正常に日付とデータを取得"""
        # 1回目の呼び出し（メンバー取得）と 2回目（エントリ取得）をシミュレート
        mock_response1 = MagicMock()
        mock_response1.json.return_value = sample_members_response
        mock_response1.raise_for_status.return_value = None

        mock_response2 = MagicMock()
        mock_response2.json.return_value = sample_time_entries_response
        mock_response2.raise_for_status.return_value = None

        mock_requests_get.side_effect = [mock_response1, mock_response2]

        # 実行
        specific_date = datetime.date(2025, 12, 18)
        result = check_specific_time.get_specific_date_time(specific_date)

        # 検証
        assert result is not None
        target_date, target_users, entered_users, project_totals = result

        assert target_date == '2025-12-18'
        assert len(target_users) == 5
        assert len(entered_users) == 4
        assert len(project_totals) == 2

    def test_member_fetch_error(self, mock_requests_get, mock_redmine_api_key, capfd):
        """メンバー取得エラー"""
        mock_requests_get.side_effect = Exception('API error')

        # 実行
        specific_date = datetime.date(2025, 12, 18)
        result = check_specific_time.get_specific_date_time(specific_date)

        # 検証
        assert result == (None, None, None, None)
        captured = capfd.readouterr()
        assert 'プロジェクトメンバー取得エラー' in captured.out


class TestGetLastTargetDate:
    """get_last_target_date 関数のテスト"""

    def test_success(self, mock_requests_get, sample_issues_response, mock_redmine_api_key):
        """前回のチェック日付を正常に取得"""
        mock_response = MagicMock()
        mock_response.json.return_value = sample_issues_response
        mock_response.raise_for_status.return_value = None
        mock_requests_get.return_value = mock_response

        # 実行
        result = check_specific_time.get_last_target_date()

        # 検証：前回が 12-17 なので、次は 12-18
        assert result == datetime.date(2025, 12, 18)

    def test_no_previous_ticket(self, mock_requests_get, mock_redmine_api_key, capfd):
        """過去のチケットがない場合は昨日を返す"""
        mock_response = MagicMock()
        mock_response.json.return_value = {'issues': []}
        mock_response.raise_for_status.return_value = None
        mock_requests_get.return_value = mock_response

        # 実行
        result = check_specific_time.get_last_target_date()

        # 検証：昨日を返す
        yesterday = datetime.date.today() - datetime.timedelta(days=1)
        assert result == yesterday
        captured = capfd.readouterr()
        assert '過去のチェックチケットが見つかりません' in captured.out

    def test_api_error(self, mock_requests_get, mock_redmine_api_key, capfd):
        """API エラー時は昨日を返す"""
        mock_requests_get.side_effect = Exception('Network error')

        # 実行
        result = check_specific_time.get_last_target_date()

        # 検証
        yesterday = datetime.date.today() - datetime.timedelta(days=1)
        assert result == yesterday
        captured = capfd.readouterr()
        assert '前回日付の取得エラー' in captured.out
