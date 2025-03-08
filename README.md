# wp-mcpy

## Claude for Desktop での MCP サーバー設定

本プロジェクトでは、Claude for Desktop における MCP サーバーとして利用できる設定を提供しています。設定ファイルは以下のパスに配置してください:

```
code $env:AppData\Claude\claude_desktop_config.json
```

### 設定ファイルの内容例

```json
{
  "mcpServers": {
    "wp-mcpy": {
      "command": "uv",
      "args": [
        "--directory",
        "C:/{{ディレクトリまでのパス}}"
        "run",
        "wp-mcpy.py"
      ],
      "env": {
        "WORDPRESS_SITE_URL": "https://example.com",
        "WORDPRESS_USERNAME": "{{your_username}}",
        "WORDPRESS_PASSWORD": "{{your_application_password}}"
      }
    }
  }
}
```

### 設定項目の説明

- **`"command"`**: 実行するコマンド名（`python` を指定しています）。
- **`"args"`**: コマンドの引数。
  - プロジェクトのディレクトリパスを指定し、その後実行するスクリプト名 (`wp-mcpy.py`) を記述します。
- **`"env"`**: WordPress サイトへの接続に利用する環境変数。
  - `WORDPRESS_SITE_URL`: WordPress のサイト URL。
  - `WORDPRESS_USERNAME`: WordPress API にアクセスするためのユーザー名。
  - `WORDPRESS_PASSWORD`: `Application Passwords` で生成したパスワード。

### 設定の適用
この設定を用いることで、Claude for Desktop から直接 WordPress に対する操作を行うことができます。設定内容は各自の環境に合わせて適切に調整してください。

