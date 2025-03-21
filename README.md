# jgrants-mcp-server
Jグランツ(デジタル庁が運営する国や自治体の補助金電子申請システム)の公開APIを利用した MCP Server
FastMCPライブラリを利用して、以下のMCPツールを提供します。

- **list_subsidies**  
  キーワード（デフォルトは「補助金」）を指定して、応募受付中の補助金一覧を検索・取得します。

- **get_subsidy_detail**  
  補助金の詳細情報を補助金のIDを用いて取得します。取得時、添付文書の巨大なbase64データは除去し、代わりにダウンロード用URLを付与します。

- **download_attachment**  
  指定した補助金の添付文書（カテゴリ、インデックス指定）のダウンロード用URLを返します。  
  ※実際のファイルデータ（base64）は返さず、URL経由で直接ダウンロード可能とします。

> **注意：**  
> すべてのツールで、補助金の識別にはタイトルではなく必ず `id` 項目を利用してください（例："a0WJ200000CDIUiMAP"）。

## 特徴

- **非同期処理：**  
  `httpx` ライブラリを利用して非同期でJグランツAPIにアクセスします。

- **MCPツール：**  
  FastMCPを使用して、以下の3つのツールがMCP形式で公開されています。
  - `list_subsidies(keyword: str = "補助金")`
  - `get_subsidy_detail(subsidy_id: str)`
  - `download_attachment(subsidy_id: str, category: str, index: int)`

- **軽量なレスポンス：**  
  補助金の詳細情報取得時、添付文書のbase64データは除去され、ダウンロード用URLが生成されるため、レスポンスが軽量になります。

## 必要環境

- Python 3.7 以降
- [httpx](https://www.python-httpx.org/)
- [FastMCP](https://modelcontextprotocol.io/quickstart/server)  
  ※または、MCPランチャーが提供するライブラリ
- （オプション）FastAPI, Uvicorn（ローカルテスト用）

## インストール手順

1. **リポジトリのクローン**

   ```bash
   git clone <your-repository-url>
   cd <repository-directory>
   ```

2. **仮想環境の作成と依存パッケージのインストール**
```python -m venv venv
source venv/bin/activate   # Windowsの場合: venv\Scripts\activate
pip install httpx fastmcp fastapi uvicorn
```


## ツールの使い方

**list_subsidies**
-	概要：
  指定したキーワードで応募受付中の補助金一覧を取得します。デフォルトは「補助金」ですが、任意のキーワードを入力可能です。
-	入力パラメータ：
	-	keyword (文字列, オプション) – 検索キーワード
-	出力例：
JSON形式の文字列（補助金一覧の全体情報）を返します。

**get_subsidy_detail**
- 概要：
  補助金の詳細情報を取得します。添付文書のbase64データは除去され、各添付文書に対して補助金のIDを利用したダウンロードURLが付与されます。
-	入力パラメータ：
  -	subsidy_id (文字列)
  -	補助金のID（タイトルではなく必ずIDを指定）
-	出力例：
MCP形式のJSONオブジェクト
```{
  "content": [
    {
      "type": "text",
      "text": "<詳細情報のJSON文字列>"
    }
  ]
}
```

**download_attachment**
- 概要：指定した補助金の添付文書について、base64データは返さず、ダウンロード用URLを返します。
- 入力パラメータ：
  - subsidy_id (文字列) – 補助金のID（必ずIDを指定）
  - category (文字列) – 添付文書のカテゴリ（例：application_guidelines, outline_of_grant, application_form）
  - index (整数) – 添付文書のインデックス（0から開始）
- 出力例：
MCP形式のJSONオブジェクト
```{
  "content": [
    {
      "type": "text",
      "text": "Attachment download URL: https://your-mcp-server.example.com/subsidies/<subsidy_id>/<category>/<index>"
    }
  ]
}
```

