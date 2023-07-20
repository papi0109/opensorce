<<< CSV de OpenLDAP操作 >>>

<< 概要 >>
CSVでOpenLDAPを操作するPythonスクリプトです。
想定としては共有フォルダをサーバにマウントして、
その対象のディレクトリ(/mnt/import)内にある「auto_operation.csv」を
cronでスケジュール実行して取り込んで、OpenLDAPへのアカウントの操作を開始。
処理し終わったCSVファイルは末尾にタイムスタンプを付けてリネームして処理を終了します。

共有フォルダにCSVを入れてスケジュールで自動取り込みして
LDAPのアカウントを操作するのは実際に案件であったもので、
その経験をベースに作りました。

以下のLDAPの用語についてはGoogle先生かChatGPT等にお聞き下さい。

< ファイル内容 >
pyLdapOpe.py（実行ファイル）
./modules/openldapConfig.ini（設定ファイル）
./modules/openLdapControl.py（モジュール）
./samplecsv(操作用のサンプルCSVを格納しているフォルダ)

< CSVファイルに必須の列 >
changeType   ...『操作識別用』 実際のldifでも必要 ※当スクリプト専用の値は moddn と attrdel
cn           ...『一般名』    objectClassがpersonの為、必須属性値。entry作成でもスクリプト上の値としても使用
sn           ...『姓』        objectClassがpersonの為、必須属性値
userPassword ...『パスワード』セキュリティ上必要な為、スクリプト上で必須属性値としている
joined       ...『組織単位(OU)』  dnの指定の為にスクリプト上で必要な値(属性値ではない)
※その他、設定できる属性値の確認はgoogle先生にて

_ moddn操作で必要な列
newOu        ... 移動先のOU

< changeTypeで使える値と処理の説明 >
add     ... エントリ追加
modify  ... エントリの指定した属性の値を更新
delete  ... エントリ削除
moddn   ... ユーザーのOU移動（エントリのDN変更）
attrdel ... エントリの指定した属性の値を削除

< 設定ファイルの説明 >
[ldap]
suffix  -> ベースとなるDNを指定します。
rootdn  -> ルートユーザーのDNを指定します。
bindpwd -> ルートユーザーのパスワードを指定します。
server  -> OpenLDAPのIPもしくはドメイン名を指定します
port    -> 暗号通信するのであれば636、通常は389を指定します。
objectclass -> オブジェクトクラスを指定します。※カンマ区切りで複数指定可

[setou] -> 取り扱うOUを指定して下さい。
ou1 = test1
ou2 = test2
ou3 = test3
...
※連番にすれば複数のOUの指定が可能