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
        "WORDPRESS_PASSWORD": "{{your_application_password}}",
        "WORDPRESS_PATH": "{{WordPressのインストールパス}}"
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
  - `WORDPRESS_PATH`: WP CLIを実行するためのWordPressインストールパス。
  - `WP_CLI_PATH`: （Windowsの場合）wp-cli.pharのフルパス。指定しない場合は同じディレクトリのwp-cli.pharを使用します。

### 設定の適用
この設定を用いることで、Claude for Desktop から直接 WordPress に対する操作を行うことができます。設定内容は各自の環境に合わせて適切に調整してください。

### Windowsでの注意事項
Windows環境でWP CLIを使用する場合は、以下の点に注意してください：

1. `WP_CLI_PATH` 環境変数にwp-cli.pharのフルパスを設定することをお勧めします
2. PHPがインストールされており、パスが通っていることを確認してください
3. パスに日本語やスペースが含まれる場合は、パスを引用符で囲むか、短いパス名を使用してください

## WP CLI 機能の使用方法

wp-mcpyは、WP CLI（WordPress Command Line Interface）を利用してWordPressを管理する機能も提供しています。これにより、プラグイン管理、テーマ管理、ユーザー管理、データベース操作などをClaudeから直接実行できます。

### 前提条件

1. WP CLIがインストールされていること
   - Unix/Linux/Mac: `wp` コマンドがシステムパスに設定されていること
   - Windows: `wp-cli.phar` ファイルが実行パスに配置され、PHPがインストールされていること

2. `WORDPRESS_PATH`環境変数にWordPressのインストールパスが設定されていること

### Windows環境での設定方法

Windows環境でWP CLIを使用するには、以下の手順に従ってください：

1. [WP-CLI公式サイト](https://wp-cli.org/#installing)から `wp-cli.phar` ファイルをダウンロード
2. ダウンロードした `wp-cli.phar` ファイルを、`wp-mcpy.py` と同じディレクトリに配置するか、システムパスの通ったディレクトリに配置
3. PHPがインストールされていることを確認
4. 以下のいずれかの方法でWP CLIを実行できます：
   - コマンドライン: `php wp-cli.phar --info`
   - wp-mcpy経由: Claudeから「WordPressの情報を教えてください」などで操作

### 利用可能なWP CLI関連ツール

#### 1. プラグイン管理 (wp_plugin)

プラグインの一覧表示、インストール、有効化、無効化などを行います。

```python
# プラグイン一覧の取得
wp_plugin(action="list")

# プラグインのインストール
wp_plugin(action="install", plugin_name="akismet")

# プラグインの有効化
wp_plugin(action="activate", plugin_name="akismet")

# プラグインの無効化
wp_plugin(action="deactivate", plugin_name="akismet")

# プラグインの削除
wp_plugin(action="delete", plugin_name="hello")
```

#### 2. テーマ管理 (wp_theme)

テーマの一覧表示、インストール、有効化などを行います。

```python
# テーマ一覧の取得
wp_theme(action="list")

# テーマのインストール
wp_theme(action="install", theme_name="twentytwentytwo")

# テーマの有効化
wp_theme(action="activate", theme_name="twentytwentytwo")
```

#### 3. ユーザー管理 (wp_user)

ユーザーの一覧表示、作成、更新、削除などを行います。

```python
# ユーザー一覧の取得
wp_user(action="list")

# ユーザーの作成
wp_user(
    action="create",
    user_args={
        "user_login": "newuser",
        "user_email": "user@example.com",
        "user_pass": "password",
        "role": "author"
    }
)

# ユーザーの更新
wp_user(
    action="update",
    user_args={
        "id": 2,
        "display_name": "New Display Name",
        "role": "editor"
    }
)

# ユーザーの削除
wp_user(action="delete", user_args={"id": 3})
```

#### 4. データベース操作 (wp_db)

データベースのエクスポート、インポート、最適化、修復などを行います。

```python
# データベースの最適化
wp_db(action="optimize")

# データベースの修復
wp_db(action="repair")

# データベースのエクスポート
wp_db(action="export", args={"file": "/path/to/export.sql"})
```

#### 5. 汎用WP CLIコマンド実行 (wp_cli)

上記のツールでカバーされていない任意のWP CLIコマンドを実行できます。

```python
# カスタム投稿タイプの一覧表示
wp_cli(command_str="post-type list")

# サイト情報の取得
wp_cli(command_str="site info")

# メディアファイルの一覧表示
wp_cli(command_str="media list")
```

### 注意事項

- WP CLIコマンドを実行するには、サーバー上にWP CLIがインストールされている必要があります。
- セキュリティとシステム保護のため、許可されたコマンドとパラメーターのみが実行可能です：
  - コマンドグループ: plugin, theme, user, db, site, core, post, option, post-type, taxonomy, menu, media
  - 各コマンドグループで許可されるサブコマンドは、安全な読み取り操作（list, get, info, status, check など）に限定されています。
  - 書き込み操作（create, update, delete, reset など）や危険な操作は禁止されています。
  - 各コマンドで使用できるパラメーターも制限されています。
- 禁止されているパラメーターには以下が含まれます：
  - `--force`: 強制的な操作の実行
  - `--delete`: 削除操作の実行
  - `--allow-root`: ルート権限での実行
  - `--user`: 別のユーザーとしての実行
  - `--skip-plugins`, `--skip-themes`: プラグインやテーマのスキップ
  - `--require`, `--exec`, `--eval`: 追加コードの実行
  - `--debug`: デバッグモードの有効化
- WP CLIコマンドを実行する際は、システムセキュリティに配慮してください。

## 設定ファイル (config.jsonc)

WP CLI の許可コマンドやパラメーターは、`config.jsonc` ファイルで管理されています。このファイルは、以下の構造を持っています：

```jsonc
{
  // WP CLI コマンドの制限設定
  "wp_cli": {
    // ホワイトリストコマンドの設定
    "whitelist_commands": {
      "plugin": ["list", "status", "get", "info"],
      // 他のコマンドグループと許可サブコマンド...
    },

    // コマンド・サブコマンド別の許可パラメーター
    "allowed_parameters": {
      "plugin": {
        "list": ["status", "format", "field", "fields"],
        // 他のパラメーター設定...
      },
      // 他のコマンドグループとパラメーター...
    },

    // 全コマンドで許可されるグローバルパラメーター
    "allowed_global_parameters": ["format", "help", "quiet", "path"],

    // 明示的に禁止するパラメーター（セキュリティリスク）
    "blacklist_parameters": [
      "--force",
      "--delete",
      // 他のブラックリストパラメーター...
    ]
  }
}
```

設定ファイルを編集することで、許可するコマンド、サブコマンド、パラメーターを簡単にカスタマイズできます。JSONCフォーマットはコメントをサポートしているため、設定項目の説明も記述できます。コード中にハードコーディングされた設定を変更する必要はなく、この設定ファイルを更新するだけで済みます。

