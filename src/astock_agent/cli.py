import typer
from rich.console import Console
from rich.markdown import Markdown

from astock_agent.graph.workflow import research_graph

console = Console()


def main(
    symbol: str,
    start_date: str,
    end_date: str,
) -> None:
    """生成包含行情和财务分析的 A 股综合研究报告。"""

    initial_state = {
        "symbol": symbol,
        "start_date": start_date,
        "end_date": end_date,
    }

    try:
        with console.status("正在运行多智能体研究工作流……"):
            result = research_graph.invoke(initial_state)

        final_report = result.get("final_report")

        if not isinstance(final_report, str) or not final_report.strip():
            raise RuntimeError("工作流没有生成最终报告")

    except Exception as exc:
        typer.echo(f"研究失败：{exc}", err=True)
        raise typer.Exit(code=1) from exc

    console.print(Markdown(final_report))


def run() -> None:
    """Start the command-line application."""

    typer.run(main)


if __name__ == "__main__":
    run()
