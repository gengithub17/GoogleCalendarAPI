# Google Calendar API
Google APIを用いて、Googleカレンダーの予定を追加できるようにしました。  
主に本家に実装されていない、不定期のイベントを複数同時に追加できる機能が使えます。

今後はイベントのテンプレート化や、複数アカウントの管理、パスワードの暗号化を実装していく予定です。

## Requirements
- docker
- docker-compose

## Preparation
### GCP API
- [Google Cloud Platform](https://console.cloud.google.com/)にアクセスし、プロジェクトを作成。
- APIとサービス > ライブラリよりGoogle Calendar APIを有効化、認証情報を作成。
  - スコープには .../auth/calendar を選択。
  - OAuthクライアントIDの「アプリケーションの種類」では「デスクトップアプリ」を選択。(ウェブアプリケーションを選択する場合はサーバー側で別途リダイレクトURI等の設定が必要)
- APIとサービス > 認証情報より、作成したOAuth2.0クライアントIDを選択し、クライアントシークレットをcred.jsonとしてダウンロード。
### Local
- app/.creds配下に以下のファイルを作成
  - cred.json : GCPからダウンロードしたクライアントシークレット
  - account.json :  
  ```
  {
      "account" : "example@gmail.com",
      "password" : "password"
  }
  ```

- dockerコンテナを起動
  - デフォルトではポート8000
  ```
  docker-compose up -d
  ```

## Notes
- JavaScriptでプルダウンの背景色変更していますが、MacOSだと反映されないようです。