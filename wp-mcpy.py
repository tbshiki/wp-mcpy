from typing import Any, Dict, Optional, List
import base64
import httpx
import asyncio
import shlex
import json
from mcp.server.fastmcp import FastMCP

# MCP サーバーを初期化
mcp = FastMCP("wordpress")


# 環境変数からデフォルトのWordPressクレデンシャルを取得
def get_default_credentials() -> Dict[str, str]:
    from os import getenv

    return {
        "site_url": getenv("WORDPRESS_SITE_URL", ""),
        "username": getenv("WORDPRESS_USERNAME", ""),
        "password": getenv("WORDPRESS_PASSWORD", ""),
        "path": getenv("WORDPRESS_PATH", ""),
    }


# WordPress API リクエスト関数
async def make_wp_request(
    endpoint: str,
    method: str = "GET",
    data: Optional[Dict[str, Any]] = None,
    site_url: str = "",
    username: str = "",
    password: str = "",
) -> Any:
    if not site_url or not username or not password:
        raise ValueError("WordPressのクレデンシャルが不足しています。")

    auth = base64.b64encode(f"{username}:{password}".encode()).decode()
    headers = {
        "Authorization": f"Basic {auth}",
        "Content-Type": "application/json",
    }
    url = f"{site_url}/wp-json/wp/v2{endpoint}"
    async with httpx.AsyncClient() as client:
        try:
            if method == "POST":
                response = await client.post(url, json=data, headers=headers)
            elif method == "PUT":
                response = await client.put(url, json=data, headers=headers)
            else:
                response = await client.get(url, params=data, headers=headers)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            return {"error": f"WordPress APIエラー: {e.response.status_code} {e.response.text}"}


# 記事の作成
@mcp.tool()
async def create_post(title: str, content: str, status: str = "draft") -> Any:
    """WordPressに記事を作成する"""
    creds = get_default_credentials()
    return await make_wp_request(
        "/posts",
        "POST",
        {"title": title, "content": content, "status": status},
        creds["site_url"],
        creds["username"],
        creds["password"],
    )


# 記事の取得
@mcp.tool()
async def get_posts(per_page: int = 10, page: int = 1) -> Any:
    """WordPressから記事一覧を取得する"""
    creds = get_default_credentials()
    return await make_wp_request(
        "/posts",
        "GET",
        {"per_page": per_page, "page": page},
        creds["site_url"],
        creds["username"],
        creds["password"],
    )


# 記事の更新
@mcp.tool()
async def update_post(
    post_id: int,
    title: Optional[str] = None,
    content: Optional[str] = None,
    status: Optional[str] = None,
) -> Any:
    """WordPressの記事を更新する"""
    creds = get_default_credentials()
    data = {}
    if title:
        data["title"] = title
    if content:
        data["content"] = content
    if status:
        data["status"] = status
    return await make_wp_request(
        f"/posts/{post_id}",
        "POST",
        data,
        creds["site_url"],
        creds["username"],
        creds["password"],
    )


# WP CLIコマンドを実行する関数
async def run_wp_cli_command(command: List[str], wordpress_path: str = "") -> Dict[str, Any]:
    """
    WP CLIコマンドを実行する

    Args:
        command: WP CLIコマンドとその引数（例: ["plugin", "list", "--format=json"]）
        wordpress_path: WordPressのインストールパス。指定しない場合は環境変数から取得

    Returns:
        コマンドの実行結果
    """
    from os import getenv

    # WordPressのパスが指定されていない場合は環境変数から取得
    if not wordpress_path:
        wordpress_path = getenv("WORDPRESS_PATH", "")
        if not wordpress_path:
            return {"error": "WordPressのパスが指定されていません。環境変数 WORDPRESS_PATH を設定してください。"}

    # WP CLIコマンドの構築
    full_command = ["wp"] + command

    if "--format=json" not in full_command:
        # 標準で JSON 形式で出力するように設定
        full_command.append("--format=json")

    # パスが指定されている場合は--pathオプションを追加
    if wordpress_path and "--path" not in " ".join(full_command):
        full_command.extend(["--path", wordpress_path])

    try:
        # サブプロセスでコマンドを実行
        process = await asyncio.create_subprocess_exec(*full_command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)

        # 実行結果を取得
        stdout, stderr = await process.communicate()

        if process.returncode != 0:
            # エラーが発生した場合
            return {"success": False, "error": stderr.decode("utf-8").strip(), "command": " ".join(full_command), "return_code": process.returncode}

        # 標準出力を取得してJSONに変換
        output = stdout.decode("utf-8").strip()
        try:
            # JSON形式の場合はパース
            result = json.loads(output)
            return {"success": True, "result": result, "command": " ".join(full_command)}
        except json.JSONDecodeError:
            # JSON形式でない場合はそのまま返す
            return {"success": True, "result": output, "command": " ".join(full_command)}

    except Exception as e:
        return {"success": False, "error": str(e), "command": " ".join(full_command)}


# WP CLIのプラグイン関連コマンド
@mcp.tool()
async def wp_plugin(action: str, plugin_name: str = "", wordpress_path: str = "") -> Any:
    """
    WordPress プラグインを管理する

    Args:
        action: 実行するアクション（list, install, activate, deactivate, update, delete）
        plugin_name: プラグインの名前またはスラッグ（アクションがlistの場合は省略可能）
        wordpress_path: WordPressのインストールパス（省略可能）

    Returns:
        コマンドの実行結果
    """
    valid_actions = ["list", "install", "activate", "deactivate", "update", "delete"]

    if action not in valid_actions:
        return {"success": False, "error": f"無効なアクションです。有効なアクション: {', '.join(valid_actions)}"}

    command = ["plugin", action]

    if action != "list" and not plugin_name:
        return {"success": False, "error": "プラグイン名を指定してください"}

    if plugin_name:
        command.append(plugin_name)

    return await run_wp_cli_command(command, wordpress_path)


# WP CLIのテーマ関連コマンド
@mcp.tool()
async def wp_theme(action: str, theme_name: str = "", wordpress_path: str = "") -> Any:
    """
    WordPress テーマを管理する

    Args:
        action: 実行するアクション（list, install, activate, delete）
        theme_name: テーマの名前またはスラッグ（アクションがlistの場合は省略可能）
        wordpress_path: WordPressのインストールパス（省略可能）

    Returns:
        コマンドの実行結果
    """
    valid_actions = ["list", "install", "activate", "delete"]

    if action not in valid_actions:
        return {"success": False, "error": f"無効なアクションです。有効なアクション: {', '.join(valid_actions)}"}

    command = ["theme", action]

    if action != "list" and not theme_name:
        return {"success": False, "error": "テーマ名を指定してください"}

    if theme_name:
        command.append(theme_name)

    return await run_wp_cli_command(command, wordpress_path)


# WP CLIのユーザー関連コマンド
@mcp.tool()
async def wp_user(action: str, user_args: Dict[str, Any] = None, wordpress_path: str = "") -> Any:
    """
    WordPress ユーザーを管理する

    Args:
        action: 実行するアクション（list, create, delete, update）
        user_args: ユーザー情報（IDや属性など）
        wordpress_path: WordPressのインストールパス（省略可能）

    Returns:
        コマンドの実行結果
    """
    valid_actions = ["list", "create", "delete", "update", "get"]

    if action not in valid_actions:
        return {"success": False, "error": f"無効なアクションです。有効なアクション: {', '.join(valid_actions)}"}

    command = ["user", action]

    # ユーザー引数の処理
    if user_args:
        if action == "get" or action == "delete":
            if "id" in user_args:
                command.append(str(user_args["id"]))
        elif action == "create":
            if "user_login" in user_args and "user_email" in user_args:
                command.append(user_args["user_login"])
                command.append(user_args["user_email"])

                # その他のオプション
                for key, value in user_args.items():
                    if key not in ["user_login", "user_email"]:
                        command.append(f"--{key}={value}")
            else:
                return {"success": False, "error": "ユーザー作成にはuser_loginとuser_emailが必要です"}
        elif action == "update":
            if "id" in user_args:
                command.append(str(user_args["id"]))
                # 更新用のオプション
                for key, value in user_args.items():
                    if key != "id":
                        command.append(f"--{key}={value}")
            else:
                return {"success": False, "error": "ユーザー更新にはIDが必要です"}

    return await run_wp_cli_command(command, wordpress_path)


# WP CLIの一般的なコマンド実行
@mcp.tool()
async def wp_cli(command_str: str, wordpress_path: str = "") -> Any:
    """
    任意のWP CLIコマンドを実行する

    Args:
        command_str: 実行するWP CLIコマンド（例: "plugin list"）
        wordpress_path: WordPressのインストールパス（省略可能）

    Returns:
        コマンドの実行結果
    """
    # コマンド文字列をリストに分割
    try:
        command = shlex.split(command_str)
        return await run_wp_cli_command(command, wordpress_path)
    except Exception as e:
        return {"success": False, "error": f"コマンドの解析エラー: {str(e)}"}


# WP CLIのデータベース関連コマンド
@mcp.tool()
async def wp_db(action: str, args: Dict[str, Any] = None, wordpress_path: str = "") -> Any:
    """
    WordPress データベースを管理する

    Args:
        action: 実行するアクション（export, import, optimize, repair, reset, check）
        args: データベース操作の引数
        wordpress_path: WordPressのインストールパス（省略可能）

    Returns:
        コマンドの実行結果
    """
    valid_actions = ["export", "import", "optimize", "repair", "reset", "check"]

    if action not in valid_actions:
        return {"success": False, "error": f"無効なアクションです。有効なアクション: {', '.join(valid_actions)}"}

    command = ["db", action]

    # 引数の処理
    if args:
        for key, value in args.items():
            if isinstance(value, bool):
                if value:
                    command.append(f"--{key}")
            else:
                command.append(f"--{key}={value}")

    return await run_wp_cli_command(command, wordpress_path)


if __name__ == "__main__":
    mcp.run(transport="stdio")
