from typing import Any, Dict, Optional
import base64
import httpx
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
            return {
                "error": f"WordPress APIエラー: {e.response.status_code} {e.response.text}"
            }


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


if __name__ == "__main__":
    mcp.run(transport="stdio")
