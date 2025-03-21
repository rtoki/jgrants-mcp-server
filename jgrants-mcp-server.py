import sys
import json
from mcp.server.fastmcp import FastMCP
import httpx

# MCPサーバーの初期化（サーバー名 "jgrants-mcp-server" として定義）
mcp = FastMCP("jgrants-mcp-server")

@mcp.tool()
async def list_subsidies(keyword: str = "補助金") -> str:
    """
    指定したキーワードで公募中の補助金一覧を取得します。
    ・キーワード、締切日の昇順、応募受付中の条件で検索を行い、
      JSON形式の文字列として結果を返します。
    ・キーワードを入力できるようにしており、デフォルトは「補助金」です。
    """
    params = {
        "keyword": keyword,
        "sort": "acceptance_end_datetime",
        "order": "ASC",
        "acceptance": "1"
    }
    url = "https://api.jgrants-portal.go.jp/exp/v1/public/subsidies"
    try:
        async with httpx.AsyncClient() as client:
            res = await client.get(url, params=params)
    except Exception as e:
        print(f"Error fetching subsidies list: {e}", file=sys.stderr)
        return f"Error fetching subsidies list: {e}"
    if res.status_code != 200:
        print(f"Non-200 response in list_subsidies: {res.status_code}", file=sys.stderr)
        return f"Error: {res.status_code}"
    data = res.json()
    return json.dumps(data, ensure_ascii=False, indent=2)

@mcp.tool()
async def get_subsidy_detail(subsidy_id: str) -> dict:
    """
    指定した補助金の詳細情報を取得します。
    ※引数 subsidy_id には、補助金の title ではなく id を指定してください。
    
    API のレスポンス形式は以下のようになっています:
    
    {
      "metadata": { ... },
      "result": [ { <補助金詳細情報> } ]
    }
    
    本ツールでは、result 配列の最初の要素について、
    ・添付文書（application_guidelines、outline_of_grant、application_form）の base64 データを除去し、
    ・各添付文書に対して、補助金の id を利用したダウンロード用 URL を付与します。
    
    返却形式は MCP 用に以下のような形式となります:
    
    {
      "content": [
         {
           "type": "text",
           "text": "<詳細情報の文字列表現>"
         }
      ]
    }
    """
    url = f"https://api.jgrants-portal.go.jp/exp/v1/public/subsidies/id/{subsidy_id}"
    try:
        async with httpx.AsyncClient() as client:
            res = await client.get(url)
    except Exception as e:
        print(f"Error fetching subsidy detail: {e}", file=sys.stderr)
        return {"content": [{"type": "text", "text": f"Error fetching subsidy detail: {e}"}]}
    if res.status_code != 200:
        print(f"Non-200 response in get_subsidy_detail: {res.status_code}", file=sys.stderr)
        return {"content": [{"type": "text", "text": f"Error: {res.status_code}"}]}
    detail_data = res.json()
    if "result" not in detail_data or len(detail_data["result"]) == 0:
        return {"content": [{"type": "text", "text": f"指定された補助金ID {subsidy_id} は見つかりませんでした。"}]}
    subsidy_info = detail_data["result"][0]
    # 添付文書について、base64データを除去し、ダウンロード用 URL を付与（必ず id 項目を使用）
    attachment_categories = ["application_guidelines", "outline_of_grant", "application_form"]
    for category in attachment_categories:
        if category in subsidy_info and subsidy_info[category]:
            for idx, attachment in enumerate(subsidy_info[category]):
                download_url = f"https://your-mcp-server.example.com/subsidies/{subsidy_info['id']}/{category}/{idx}"
                attachment["url"] = download_url
                attachment.pop("data", None)
    text_representation = json.dumps(subsidy_info, ensure_ascii=False, indent=2)
    return {"content": [{"type": "text", "text": text_representation}]}

@mcp.tool()
async def download_attachment(subsidy_id: str, category: str, index: int) -> dict:
    """
    指定した補助金の添付文書について、base64 のファイルデータは返さず、
    代わりにダウンロード用 URL を返します。
    
    ※引数 subsidy_id には、必ず id を指定してください。
    """
    url = f"https://api.jgrants-portal.go.jp/exp/v1/public/subsidies/id/{subsidy_id}"
    try:
        async with httpx.AsyncClient() as client:
            res = await client.get(url)
    except Exception as e:
        print(f"Error fetching subsidy detail for attachment: {e}", file=sys.stderr)
        return {"content": [{"type": "text", "text": f"Error fetching subsidy detail: {e}"}]}
    if res.status_code != 200:
        print(f"Non-200 response in download_attachment: {res.status_code}", file=sys.stderr)
        return {"content": [{"type": "text", "text": f"Error: {res.status_code}"}]}
    detail_data = res.json()
    if "result" not in detail_data or len(detail_data["result"]) == 0:
        return {"content": [{"type": "text", "text": f"指定された補助金ID {subsidy_id} は見つかりませんでした。"}]}
    subsidy_info = detail_data["result"][0]
    if category not in subsidy_info or not subsidy_info[category]:
        return {"content": [{"type": "text", "text": f"添付文書カテゴリ '{category}' は存在しません。"}]}
    attachments = subsidy_info[category]
    if index < 0 or index >= len(attachments):
        return {"content": [{"type": "text", "text": f"添付文書のインデックス {index} は無効です。"}]}
    download_url = f"https://your-mcp-server.example.com/subsidies/{subsidy_info['id']}/{category}/{index}"
    return {"content": [{"type": "text", "text": f"Attachment download URL: {download_url}"}]}

if __name__ == "__main__":
    mcp.run()