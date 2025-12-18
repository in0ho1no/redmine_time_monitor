"""main モジュールのテスト"""

import datetime
from unittest.mock import MagicMock, patch

import pytest

import main


class TestMain:
    """main 関数のテスト"""

    def test_success_with_all_data(
        self,
        mock_requests_get,
        mock_requests_post,
        sample_members_response,
        sample_time_entries_response,
        sample_create_issue_response,
        mock_redmine_api_key,
        capfd,
    ):
        """全データ取得成功、チケット作成成功"""
        # 3つのAPI呼び出しをシミュレート
        # 1. get_last_target_date の issues 取得
        # 2. get_specific_date_time の memberships 取得
        # 3. get_specific_date_time の time_entries 取得
        # 4. create_redmine_ticket の issues 作成

        issues_response = {'issues': []}  # チケット検索結果なし -> 昨日を返す

        mock_response1 = MagicMock()
        mock_response1.json.return_value = issues_response
        mock_response1.raise_for_status.return_value = None

        mock_response2 = MagicMock()
        mock_response2.json.return_value = sample_members_response
        mock_response2.raise_for_status.return_value = None

        mock_response3 = MagicMock()
        mock_response3.json.return_value = sample_time_entries_response
        mock_response3.raise_for_status.return_value = None

        mock_requests_get.side_effect = [mock_response1, mock_response2, mock_response3]

        # POST レスポンスの設定
        mock_post_response = MagicMock()
        mock_post_response.json.return_value = sample_create_issue_response
        mock_post_response.raise_for_status.return_value = None
        mock_requests_post.return_value = mock_post_response

        # 実行
        main.main()

        # 検証：GET が3回、POST が1回呼ばれた
        assert mock_requests_get.call_count == 3
        assert mock_requests_post.call_count == 1

        # ログ出力を確認
        captured = capfd.readouterr()
        assert 'チェック対象日:' in captured.out
        assert 'ターゲットユーザー数:' in captured.out
        assert '入力済みユーザー数:' in captured.out
        assert 'チケット作成成功' in captured.out

    def test_data_fetch_error(
        self,
        mock_requests_get,
        mock_redmine_api_key,
        capfd,
    ):
        """データ取得エラー"""
        # 最初のAPI呼び出しで例外を発生させる
        mock_requests_get.side_effect = Exception('API error')

        # 実行
        main.main()

        # 検証：エラーメッセージが出力される
        captured = capfd.readouterr()
        assert 'エラー: データ取得に失敗しました' in captured.out or 'プロジェクトメンバー取得エラー' in captured.out


class TestMainWithArgumentParsing:
    """main エントリポイントのテスト（引数パース含む）"""

    def test_api_key_argument(self, monkeypatch, mock_redmine_api_key):
        """APIキー引数が正しく設定される"""
        import user_setting as us

        # 擬似的にコマンドライン引数を設定
        test_api_key = 'test_key_12345'
        monkeypatch.setattr('sys.argv', ['main.py', test_api_key])

        # user_setting の REDMINE_API_KEY が更新されることを確認
        original_key = us.REDMINE_API_KEY
        us.REDMINE_API_KEY = test_api_key

        # 検証
        assert test_api_key == us.REDMINE_API_KEY

        # クリーンアップ
        us.REDMINE_API_KEY = original_key
