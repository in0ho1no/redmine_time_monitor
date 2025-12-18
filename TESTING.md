# テスト実行ガイド

## 前準備

### 2. Python パスの確認

`pytest.ini` で `pythonpath = src` に設定されているため、`src` 以下のモジュールが自動的にインポートパスに追加されます。

---

## テスト実行方法

### 全テストを実行

```bash
pytest
```

### 特定のテストファイルを実行

```bash
# check_specific_time のテストのみ
pytest tests/test_check_specific_time.py

# create_redmine_ticket のテストのみ
pytest tests/test_create_redmine_ticket.py

# main のテストのみ
pytest tests/test_main.py
```

### 特定のテストクラス/関数を実行

```bash
# テストクラスを指定
pytest tests/test_check_specific_time.py::TestGetProjectMembers

# テスト関数を指定
pytest tests/test_check_specific_time.py::TestGetProjectMembers::test_success
```

### 詳細なログ出力

```bash
# 詳細な出力（-v フラグ）
pytest -v

# print 文の出力も表示（-s フラグ）
pytest -s

# 組み合わせ
pytest -v -s
```

### カバレッジレポート（オプション）

coverage をインストールした場合：

```bash
# インストール
pip install pytest-cov

# カバレッジ測定
pytest --cov=src --cov-report=html

# レポートは htmlcov/index.html で確認できます
```

---

## テスト内容

### test_check_specific_time.py

Redmine API のデータ取得機能をテスト：

- **TestGetProjectMembers**: プロジェクトメンバー取得
  - `test_success`: API 正常応答
  - `test_api_error`: API エラーハンドリング

- **TestGetTimeEntries**: 作業時間エントリ取得
  - `test_success`: API 正常応答
  - `test_api_error`: API エラーハンドリング

- **TestAggregateEntries**: 作業時間の集計ロジック
  - `test_aggregate`: 正常な集計
  - `test_aggregate_empty_entries`: 空データの処理
  - `test_aggregate_filters_non_target_users`: フィルタリング

- **TestGetSpecificDateTime**: 日付指定でのデータ一括取得
  - `test_success`: 正常な取得
  - `test_member_fetch_error`: エラーハンドリング

- **TestGetLastTargetDate**: 前回のチェック日付取得
  - `test_success`: 正常な取得
  - `test_no_previous_ticket`: チケットがない場合
  - `test_api_error`: API エラーハンドリング

### test_create_redmine_ticket.py

Redmine チケット作成機能をテスト：

- **TestBuildUserTableRows**: ユーザーテーブル行生成
  - `test_with_missing_and_ok_users`: 混在パターン
  - `test_all_users_entered`: 全員入力済み
  - `test_no_users_entered`: 全員未入力

- **TestBuildProjectTableRows**: プロジェクト別集計テーブル生成
  - `test_with_projects`: 複数プロジェクト
  - `test_empty_projects`: プロジェクトなし

- **TestBuildDescription**: Textile 形式の説明文生成
  - `test_with_missing_users`: 未入力者がいる場合
  - `test_without_missing_users`: 全員入力済みの場合

- **TestGetSubjectAndPriority**: チケット件名と優先度決定
  - `test_with_missing_users`: 未入力者がいる場合
  - `test_without_missing_users`: 全員入力済みの場合

- **TestCreateRedmineTicket**: メインのチケット作成処理
  - `test_success_with_missing_users`: 未入力者がいる場合の成功
  - `test_success_without_missing_users`: 全員入力済みの場合の成功
  - `test_api_error`: API エラーハンドリング

### test_main.py

メイン処理とエントリポイントのテスト：

- **TestMain**: main 関数
  - `test_success_with_all_data`: 正常系（エンドツーエンド）
  - `test_data_fetch_error`: エラーハンドリング

- **TestMainWithArgumentParsing**: コマンドライン引数パース
  - `test_api_key_argument`: APIキー引数の設定

---

## モック と フィクスチャ

### conftest.py で定義されているフィクスチャ

- `mock_redmine_api_key`: API キーのモック設定
- `mock_requests_get`: `requests.get` のモック
- `mock_requests_post`: `requests.post` のモック
- `sample_members_response`: プロジェクトメンバーの応答サンプル
- `sample_time_entries_response`: 作業時間エントリの応答サンプル
- `sample_issues_response`: チケット検索の応答サンプル
- `sample_create_issue_response`: チケット作成の応答サンプル

---

## トラブルシューティング

### モジュールが見つからない

`src` ディレクトリが Python パスに追加されていることを確認：

```bash
# pytest.ini が以下を含むか確認
# pythonpath = src
```

### API 呼び出しが失敗する（モック関連）

モックの戻り値が正しく設定されているか確認：

```python
mock_response = MagicMock()
mock_response.json.return_value = {"key": "value"}
mock_response.raise_for_status.return_value = None
```

### テスト実行時の import エラー

仮想環境が有効になっていることを確認：

```bash
# Windows PowerShell
.venv\Scripts\Activate.ps1

# Linux/macOS
source .venv/bin/activate
```
