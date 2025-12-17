# Step of create work enviromental

## UVによる環境作成

### 新規作成

適当なフォルダにて以下でプロジェクトを作成する

    uv init redmine_time_monitor -p 313

### パッケージ追加

パッケージを追加する場合は以下

    uv add <パッケージ名>

今回は以下利用

    uv add requests

バージョン指定が必要なら以下

    uv add "<パッケージ名>==<バージョン>"

### パッケージ削除

パッケージを取り除くなら以下

    uv remove <パッケージ名>

### 作成済み環境の同期

pyproject.tomlの存在するフォルダ内で以下コマンドを実行する

    uv sync

## redmineの情報取得

`trackers.json`の指定でtracker情報を取得できる。

    https: //localhost/redmineKome/trackers.json

## タスクスケジューラの設定

1. Windowsメニューで「タスクスケジューラ」と検索して起動する
1. 右側のメニューから「基本タスクの作成」をクリックする
    - 名前: 日時入力確認
    - トリガー: 毎日
    - 開始日時: 9:00
    - 間隔: 1日
    - 操作: プログラムの開始
1. プログラム/スクリプト:  
Pythonの実行ファイルパス  
→ 仮想環境内のexeを指定する(venv\Scripts\python.exe)
1. 引数の追加:  
→ スクリプトのパスを指定する(\src\main.py)  
→→ さらにAPIキーも指定するならそれぞれダブルクォーテーションで括って併記する
