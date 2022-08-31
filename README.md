# info-squares-notifer
InfoSquares の check list を解析し, slack にメッセージを通知する

## 前提条件
本スクリプトを実行するためには[ChromeDriver](https://chromedriver.chromium.org/downloads)が必要です.
ドライバーをインストールしたら, インストール先のパスを`info-squares-notifer/src/main.py`の`CHROMEDRIVER_PATH`に設定してください.

また, 本スクリプトでは Webhook を使用して Slack にメッセージを送信しています.
[Slack app](https://api.slack.com/apps)より独自アプリを作成し, incoming webhook を作成していください.
incoming webhook で作成された URL を`info-squares-notifer/src/main.py`の`WEBHOOK_URL`に設定してください.
