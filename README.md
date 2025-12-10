로컬 pc인 윈도우11 + VSCode(or Cursor) 환경에서 진행합니다.


# 0. 로컬 개발 환경 준비 (Windows 11 + VSCode)

프로젝트는 미리 git clone 된 상태라고 가정합니다.

```powershell
git clone https://github.com/jinhoOps/ncloud-docs-mcp-server.git
cd ncloud-docs-mcp-server
```

VSCode / Cursor 에서 이 폴더를 열어 둡니다.



# 1. uv 기반 파이썬 환경 세팅

## 1-1. uv init 수행 (처음 이 레포를 만들 때만 필요)

이미 이 레포에는 `pyproject.toml` 이 들어 있으므로
다른 사람이 클론해서 쓸 때는 이 단계는 보통 생략해도 됩니다.

처음 이 프로젝트를 만들 때는 아래처럼 실행했습니다:

```powershell
uv init --python 3.13
```

이 작업으로

* pyproject.toml
* main.py
* .python-version

이 생성됩니다.

이미 레포에 포함되어 있다면 따로 실행할 필요는 없습니다.

## 1-2. 파이썬 버전 확인 및 설치/고정

`.python-version` 파일을 확인합니다.

```powershell
Get-Content .python-version  # 보통 3.13.x 로 기록됨
```

아직 해당 버전이 설치되어 있지 않다면:

```powershell
uv python install 3.13       # 실제로 설치되는 버전은 3.13.9 (예상)
uv python pin 3.13.9
Get-Content .python-version  # 3.13.9 로 바뀐 것 확인
```

파이썬 버전 및 패키지 인식을 확인합니다.

```powershell
uv run python -c "import sys; print(sys.version); import ncloud_docs_mcp; print('OK')"
```

마지막 줄에 `OK` 가 나오면 패키지 인식은 정상입니다.



# 2. 패키지 구조 준비 (이미 레포에 포함된 경우 확인만)

현재 레포는 다음과 같은 구조를 가지고 있습니다.

```text
ncloud_docs_mcp/
  __init__.py
  config.py
  cli.py
  server/
    __init__.py
    mcp_server.py
    tools.py
  indexer/
    __init__.py
    crawler.py
    extractor.py
    embedder.py
    runner.py
  vector/
    __init__.py
    qdrant_client.py
  models/
    __init__.py
    search.py
  storage/
    __init__.py
    ...
data/
  cache_html/
  (qdrant 데이터는 컨테이너 내부에 저장)
```

처음 만들 때는 PowerShell로 대략 이렇게 생성했습니다:

```powershell
New-Item -ItemType Directory -Path ncloud_docs_mcp
New-Item -ItemType Directory -Path ncloud_docs_mcp/server
New-Item -ItemType Directory -Path ncloud_docs_mcp/indexer
New-Item -ItemType Directory -Path ncloud_docs_mcp/vector
New-Item -ItemType Directory -Path ncloud_docs_mcp/models
New-Item -ItemType Directory -Path ncloud_docs_mcp/storage

"" | Out-File ncloud_docs_mcp/__init__.py
"" | Out-File ncloud_docs_mcp/server/__init__.py
"" | Out-File ncloud_docs_mcp/indexer/__init__.py
"" | Out-File ncloud_docs_mcp/vector/__init__.py
"" | Out-File ncloud_docs_mcp/models/__init__.py
"" | Out-File ncloud_docs_mcp/storage/__init__.py
```

하지만 이제는 레포에 이미 포함되어 있으므로, 클론한 사람은 **그냥 파일만 확인하면 됩니다.**



# 3. 데이터 디렉터리 생성

인덱싱 시 HTML 캐시 등을 저장할 로컬 디렉터리를 만들어 둡니다.

```powershell
New-Item -ItemType Directory -Path data
New-Item -ItemType Directory -Path data/cache_html
```

(Qdrant 저장소는 Windows 환경 문제 때문에 컨테이너 내부에 유지합니다.)



# 4. Python 의존성 설치

프로젝트 루트에서 uv 로 의존성을 설치합니다.

```powershell
uv add httpx
uv add beautifulsoup4
uv add qdrant-client
uv add pydantic
uv add python-dotenv
```

(MCP Python SDK 패키지는 나중에 추가 예정)
```
uv add mcp
```

설치가 끝나면 다시 한 번 간단히 확인:

```powershell
uv run python -c "import httpx, bs4, qdrant_client, pydantic; print('deps OK')"
```



# 5. Qdrant 컨테이너 실행 (Windows용 권장 방식)

Windows + Docker Desktop 환경에서 로컬 디렉터리를 볼륨으로 마운트하면
Qdrant가 파일시스템 체크 때문에 종료되는 이슈가 있어서,
MVP 개발 단계에서는 **볼륨 없이 컨테이너 내부 스토리지만 사용**하는 방식을 씁니다.

먼저 기존 qdrant 컨테이너가 있다면 정리:

```bash
docker rm -f qdrant
```

그다음 Qdrant를 실행합니다. (이 터미널은 켜둔 상태로 로그를 보면서 작업해도 좋습니다.)

```bash
docker run --name qdrant \
  -p 6333:6333 \
  -e QDRANT__STORAGE__PERF__DISABLE_FS_CHECK=true \
  qdrant/qdrant
```

정상적으로 떠 있으면 로그에 대략 이런 메시지가 보입니다.

* `Qdrant HTTP listening on 6333`
* `Qdrant gRPC listening on 6334`

다른 터미널에서 확인:

```bash
docker ps
```

qdrant 컨테이너가 `Up` 상태이면 OK입니다.

대시보드는 브라우저에서 확인 가능합니다.

```text
http://localhost:6333/dashboard
```



# 6. 인덱서 실행 (금융 사용 가이드 인덱싱)

이제 금융 사용 가이드 전체를 인덱싱하는 CLI를 실행합니다.

```powershell
uv run python -m ncloud_docs_mcp.cli index-fin
```

정상적으로 동작하면 아래와 비슷한 로그가 나옵니다.

```text
=== run_fin_index: 금융 문서 전체 인덱싱 시작 ===
총 XX개의 URL 수집됨
  URL[0]: https://guide-fin.ncloud-docs.com/docs/...
  ...
앞 10개의 URL만 인덱싱 진행
[PROCESS] https://guide-fin.ncloud-docs.com/docs/server-overview
  fetch OK
  섹션 수: 4
  벡터 수: 4
  payload 수: 4
  Qdrant upsert 완료
...
=== run_fin_index: 완료 ===
```

* 개발 단계에서는 `runner.py` 내부의 `max_urls` 를 이용해서
  너무 많은 페이지를 한 번에 인덱싱하지 않도록 제한하고 있습니다.
* Qdrant 대시보드의 `Collections → ncp_docs_fin_usage → Points` 에서
  포인트(벡터) 개수가 증가하는 것을 확인할 수 있습니다.



# 7. Qdrant 연동 스모크 테스트 (선택)

Qdrant와 Python 클라이언트가 잘 붙는지 간단히 확인하고 싶다면:

(이때도 Qdrant 컨테이너는 실행 중이어야 합니다.)

```powershell
uv run python -c "from ncloud_docs_mcp.vector.qdrant_client import NcpQdrantClient; c = NcpQdrantClient(); c.ensure_collection(); print('done')"
```

`done` 이 출력되면 컬렉션 생성/접근은 정상입니다.
(인덱서에서 `upsert_sections` 호출 시에도 자동으로 `ensure_collection()` 이 호출됩니다.)



# 8. 검색 기능 테스트 (내부 Python 함수)

인덱싱이 끝난 후, 검색 파이프라인이 정상동작하는지 Python에서 직접 호출해 봅니다.

```powershell
uv run python -c "from ncloud_docs_mcp.server.tools import ncp_search_docs; import json; print(json.dumps(ncp_search_docs('fin', 'server', 3), ensure_ascii=False, indent=2))"
```

예상되는 출력 형태:

```json
{
  "platform": "fin",
  "query": "server",
  "top_k": 3,
  "results": [
    {
      "title": "(추후추출)",
      "url": "https://guide-fin.ncloud-docs.com/docs/server-overview",
      "section": "서버 개요",
      "snippet": "본문 텍스트 일부...",
      "score": 0.12345,
      "platform": "fin"
    },
    ...
  ]
}
```

* `results` 배열에 하나 이상 결과가 보이면 검색 기능은 정상입니다.
* 현재는 Dummy 임베딩을 사용하므로 “정확한 의미 검색”이라기보다는
  “파이프라인이 잘 동작하는지” 확인용입니다.



# 9. 문서 읽기 기능 테스트 (내부 Python 함수)

특정 문서 URL을 넣어 markdown 형태로 읽어오는 기능도 테스트합니다.

```powershell
uv run python -c "from ncloud_docs_mcp.server.tools import ncp_read_doc; import json; print(json.dumps(ncp_read_doc('https://guide-fin.ncloud-docs.com/docs/server-overview'), ensure_ascii=False)[:1000])"
```

대략 이런 형태의 JSON이 출력됩니다.

```json
{
  "url": "https://guide-fin.ncloud-docs.com/docs/server-overview",
  "platform": "fin",
  "title": "(추후추출)",
  "markdown_body": "## 서버 소개\n\n본문 내용...\n\n## 또 다른 섹션\n\n..."
}
```

* `markdown_body` 에 섹션별로 `## 제목` + 텍스트가 붙어서 내려오면 정상입니다.
* 현재 제목(title)은 HTML `<title>` 추출이 아니라 임시값 `"(추후추출)"` 을 사용하고 있습니다.

---

# 10. 정리 – 여기까지가 MVP 1차

위 단계까지 끝나면 다음이 모두 충족됩니다.

* 금융 사용 가이드 전체(또는 max_urls 범위)가 Qdrant에 인덱싱됨
* 내부 함수 `ncp_search_docs()` 로 검색 결과를 조회할 수 있음
* 내부 함수 `ncp_read_doc()` 로 NCP 문서를 markdown 형태로 읽어올 수 있음
* Qdrant 대시보드에서 컬렉션과 포인트를 눈으로 확인할 수 있음

즉,

1. “금융 사용 가이드 전체를 자동 인덱싱하는 시스템”
2. “문서를 검색하고 읽을 수 있는 서버 내부 로직”

까지 구현된 **MVP 1차 단계가 완료된 상태**입니다.


좋아요, 지금 README가 **MVP 1차까지** 잘 정리돼 있으니까
그 아래에 **“MVP 2차 – MCP 서버 + Claude 연동”** 섹션만 이어서 붙이면 딱 깔끔하겠습니다.

아래 내용 그대로 10번 섹션 뒤에 붙여 넣으시면 돼요.



````markdown


# 11. MCP 서버 실행 (FastMCP 기반 stdio 서버)

이 단계부터는 **MCP Python SDK(mcp 패키지)**가 설치되어 있다고 가정합니다.

```powershell
uv add mcp
````

MCP 서버 엔트리 포인트는 다음 모듈입니다.

```text
ncloud_docs_mcp.server.mcp_server
```

로컬에서 MCP 서버가 에러 없이 뜨는지 먼저 확인합니다.

```powershell
uv run python -m ncloud_docs_mcp.server.mcp_server
```

* 정상 동작 시 **아무 출력 없이 그대로 대기 상태**가 됩니다.
* `Ctrl + C` 로 종료하면 됩니다.
* MCP 서버는 STDIO(JSON-RPC) 기반이므로,
  `mcp_server.py` 내부에서는 `print()`로 stdout에 로그를 찍으면 안 됩니다.
  (로그가 필요하면 `logging` + stderr 핸들러를 사용해야 합니다.)



# 12. Claude Desktop MCP 서버 연동

이 프로젝트는 Claude Desktop의 MCP 기능을 통해 툴로 호출할 수 있습니다.

## 12-1. Claude Desktop 설정 파일 열기

Claude Desktop 메뉴에서:

* `Developer` → `Edit Config` 선택

Windows 기준 설정 파일 경로는 대략 다음과 같습니다.

```text
%APPDATA%\Claude\claude_desktop_config.json
```

## 12-2. mcpServers 항목에 서버 등록

`claude_desktop_config.json` 의 `mcpServers` 항목에 아래 내용을 추가합니다.
(이미 `mcpServers`가 있다면 그 안에 `"ncloud-docs-mcp"` 블록만 추가)

`"D:\\sandbox\\CODE\\ncloud-docs-mcp-server"` 부분은 **본인 로컬 경로**에 맞게 수정해야 합니다.

```jsonc
{
  "mcpServers": {
    "ncloud-docs-mcp": {
      "command": "uv",
      "args": [
        "--directory",
        "D:\\sandbox\\CODE\\ncloud-docs-mcp-server",
        "run",
        "python",
        "-m",
        "ncloud_docs_mcp.server.mcp_server"
      ]
    }
  }
}
```

수정 후에는 **Claude Desktop을 완전히 종료했다가 다시 실행**해야 변경사항이 반영됩니다.


# 13. Claude에서 MCP 툴 동작 확인

Claude Desktop 재실행 후, 아무 채팅이나 열고 아래를 확인합니다.

1. 입력창에서 `/` 를 입력해보면 MCP 툴 목록에
   `search_docs`, `read_doc` 비슷한 이름의 툴이 보이는지 확인합니다.
2. 또는 Claude에게 자연어로 다음과 같이 요청해볼 수 있습니다.

### 13-1. search_docs 툴 테스트

예시 프롬프트:

> "ncloud 문서 MCP 서버 연결된 거 맞으면,
> search_docs 툴로 금융(fin) 플랫폼에서 server 관련 문서 5개만 찾아줘"

내부적으로는 대략 다음 호출이 수행됩니다.

```python
search_docs(platform="fin", query="server", top_k=5)
```

정상이라면 Claude 응답에 다음과 유사한 JSON/요약이 포함됩니다.

```json
{
  "platform": "fin",
  "query": "server",
  "top_k": 5,
  "results": [
    {
      "title": "(추후추출)",
      "url": "https://guide-fin.ncloud-docs.com/docs/cloudinsight-faq",
      "section": "Q. 특정 시간대에 이벤트 룰 액션을 정지할 수 있는 방법이 있나요?",
      "snippet": "A.Planned Maintenance 기능을 활용하면 ...",
      "score": 0.8768,
      "platform": "fin"
    },
    ...
  ]
}
```

Claude는 이 결과를 바탕으로 **관련 문서 목록 + 간단 요약**을 보여주게 됩니다.

### 13-2. read_doc 툴 테스트

예시 프롬프트:

> "read_doc 툴로 [https://guide-fin.ncloud-docs.com/docs/server-overview](https://guide-fin.ncloud-docs.com/docs/server-overview) 문서를 읽고 요약해줘"

내부적으로는 다음 호출이 수행됩니다.

```python
read_doc(url="https://guide-fin.ncloud-docs.com/docs/server-overview")
```

정상이라면 `ncp_read_doc()`에서 반환한 `markdown_body`를 기반으로, Claude가 문서 내용을 요약해 줍니다.


# 14. 정리 – 여기까지가 MVP 2차

여기까지 완료되면 다음이 모두 충족됩니다.

1. 금융 사용 가이드 전체(또는 max_urls 범위)가 Qdrant에 인덱싱됨
2. 내부 함수 `ncp_search_docs()` / `ncp_read_doc()` 로 검색 및 문서 읽기가 정상 동작
3. MCP 서버(`ncloud_docs_mcp.server.mcp_server`)가 STDIO 기반으로 실행 가능
4. Claude Desktop에서

   * `search_docs` MCP 툴로 금융 문서 검색
   * `read_doc` MCP 툴로 단일 문서 읽기 + 요약
     을 실제로 호출/활용할 수 있음

즉,

1. **“금융 사용 가이드 전체를 자동 인덱싱하는 시스템”**
2. **“문서를 검색하고 읽을 수 있는 MCP 서버(Claude 연동)”**

까지 구현된 **MVP 2차 단계가 완료된 상태**입니다.
