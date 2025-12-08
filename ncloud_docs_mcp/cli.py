
import argparse

from ncloud_docs_mcp.indexer.runner import run_fin_index


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="ncloud-docs-mcp",
        description="Naver Cloud Docs MCP helper CLI",
    )

    subparsers = parser.add_subparsers(dest="command")
    subparsers.required = True

    # 금융 사용 가이드 인덱싱
    index_fin_parser = subparsers.add_parser(
        "index-fin",
        help="Index Naver Cloud Financial guide docs",
    )
    # 필요하면 옵션 추가 예정
    # index_fin_parser.add_argument(...)

    args = parser.parse_args()

    if args.command == "index-fin":
        run_fin_index()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
