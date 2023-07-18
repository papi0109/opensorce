■ 概要
PythonでGoogleClassroomAPIを使用した各種操作用モジュールです。
実際に操作できたものを目的別にコードを分割しました。
前処理でCSVもしくはDB,LDAPの処理の実行を想定したものです。
ClassroomAPIはあまり日本語の説明が落ちていないので、ぜひご参照下さい。

・apikey.py
APIキー取得用

・class_control.py
クラスの操作用（全クラス取得、作成、更新、削除）
※apikey.pyとusers_control.pyも使用

・corsework_control.py
課題の操作用（指定クラス内の全課題取得、作成、削除）
更新はメソッドは合っているが操作できず。
情報があればもらえると嬉しいです。
※apikey.pyを使用

・topic_control.py
トピックの操作用（指定クラス内の全トピック取得、作成、更新、削除）
※apikey.pyを使用

・users_control.py
クラスに参加しているユーザーの操作用（指定クラス内の全生徒と教師の取得、生徒と教師の参加と脱退）
※apikey.pyを使用