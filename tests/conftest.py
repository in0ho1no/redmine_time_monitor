"""pytest の共通設定とフィクスチャ"""

import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

# src ディレクトリを Python パスに追加
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

import user_setting as us


@pytest.fixture
def mock_redmine_api_key():
    """Redmine API キーのモック設定"""
    original_key = us.REDMINE_API_KEY
    us.REDMINE_API_KEY = 'test_api_key_12345'
    yield
    us.REDMINE_API_KEY = original_key


@pytest.fixture
def mock_requests_get(monkeypatch):
    """requests.get をモック"""
    mock_get = MagicMock()
    monkeypatch.setattr('requests.get', mock_get)
    return mock_get


@pytest.fixture
def mock_requests_post(monkeypatch):
    """requests.post をモック"""
    mock_post = MagicMock()
    monkeypatch.setattr('requests.post', mock_post)
    return mock_post


@pytest.fixture
def sample_members_response():
    """プロジェクトメンバーのレスポンスサンプル"""
    return {
        'memberships': [
            {'user': {'id': 6, 'name': '水城 瑞希'}},
            {'user': {'id': 7, 'name': '佐藤 陽翔'}},
            {'user': {'id': 8, 'name': '高橋 葵'}},
            {'user': {'id': 9, 'name': '山田 蓮'}},
            {'user': {'id': 10, 'name': '中村 光'}},
        ]
    }


@pytest.fixture
def sample_time_entries_response():
    """作業時間エントリのレスポンスサンプル"""
    return {
        'time_entries': [
            {'user': {'id': 6}, 'hours': 8.0, 'project': {'name': 'Project A'}},
            {'user': {'id': 7}, 'hours': 7.5, 'project': {'name': 'Project A'}},
            {'user': {'id': 8}, 'hours': 6.0, 'project': {'name': 'Project B'}},
            {'user': {'id': 6}, 'hours': 2.0, 'project': {'name': 'Project B'}},
        ]
    }


@pytest.fixture
def sample_issues_response():
    """Redmine チケット検索レスポンスサンプル"""
    return {
        'issues': [
            {
                'id': 100,
                'subject': '【完了】作業時間入力チェック (2025-12-17)',
                'created_on': '2025-12-17T10:00:00Z',
            }
        ]
    }


@pytest.fixture
def sample_create_issue_response():
    """チケット作成レスポンスサンプル"""
    return {
        'issue': {
            'id': 101,
            'subject': '【未入力あり】作業時間入力チェック (2025-12-18)',
            'created_on': '2025-12-18T10:00:00Z',
        }
    }
