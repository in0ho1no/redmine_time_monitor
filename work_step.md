# Step of create work enviromental

## UVによる環境作成

### 新規作成

適当なフォルダにて以下でプロジェクトを作成する

    uv init redmine_time_monitor -p 313

### パッケージ追加

パッケージを追加する場合は以下

    uv add <パッケージ名>

バージョン指定が必要なら以下

    uv add "<パッケージ名>==<バージョン>"

### パッケージ削除

パッケージを取り除くなら以下

    uv remove <パッケージ名>

### 作成済み環境の同期

pyproject.tomlの存在するフォルダ内で以下コマンドを実行する

    uv sync
