from langchain_core.messages import HumanMessage, SystemMessage

from astock_agent.schemas.stock import MarketSummary
from astock_agent.services.llm import get_llm

SYSTEM_PROMPT = """
你是一名谨慎、客观的A股市场分析师。

你的任务是根据程序提供的行情摘要，生成中文市场分析。

要求：
1. 只使用输入数据，不得编造新闻、财务数据或公司事件。
2. 明确区分客观数据和分析判断。
3. 分析价格趋势、区间波动和成交活跃度。
4. 数据不足时必须明确说明局限。
5. 不承诺收益，不输出绝对化投资建议。
6. 使用简洁的中文分段输出。
""".strip()


def analyze_market(summary: MarketSummary) -> str:
    """Generate a Chinese market analysis from a market summary."""

    llm = get_llm()

    user_prompt = f"""
请分析下面这份A股行情摘要：

数据来源：AKShare stock_zh_a_hist。
价格单位：元/股；成交量单位：手；成交额单位：元。
数据截止到摘要中的 end_date。不要猜测当前日期，也不要把条件性的未来日期提示写进报告。

{summary.model_dump_json(indent=2)}

请按照以下结构输出：
1. 走势概览
2. 价格区间
3. 成交活跃度
4. 风险与局限
""".strip()

    response = llm.invoke(
        [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=user_prompt),
        ]
    )

    content = response.content

    if not content:
        raise RuntimeError("The market analyst returned an empty response")

    return str(content).strip()
