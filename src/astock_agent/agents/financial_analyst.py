from langchain_core.messages import HumanMessage, SystemMessage

from astock_agent.schemas.financial import FinancialSummary
from astock_agent.services.llm import get_llm

SYSTEM_PROMPT = """
你是一名谨慎、客观的A股财务分析师。

你的任务是根据程序提供的财务摘要，生成中文财务分析。

要求：
1. 只使用输入数据，不得编造新闻、公司事件、估值或其他财务指标。
2. 明确区分客观数据和分析判断。
3. 同比数据必须基于相同报告期比较。
4. 区分百分比与百分点，例如毛利率从80%变为85%，应称为上升5个百分点。
5. 如果某个字段为空，必须说明数据不足，不能自行补充。
6. 必须说明报告期和财报披露日期。
7. 不承诺收益，不给出绝对化投资建议。
8. 使用简洁的中文分段输出。
""".strip()


def analyze_financials(summary: FinancialSummary) -> str:
    """Generate a Chinese financial analysis from a financial summary."""

    llm = get_llm()

    user_prompt = f"""
请分析下面这份A股财务摘要：

数据来源：{summary.source}
金额单位：元
同比变化单位：百分比
ROE和毛利率变化单位：百分点

{summary.model_dump_json(indent=2)}

请按照以下结构输出：
1. 报告概览
2. 收入与利润
3. 盈利能力
4. 风险与数据局限

金额可以换算为亿元展示，1亿元等于100000000元。
不得推测数据中没有提供的业绩变化原因。
""".strip()

    response = llm.invoke(
        [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=user_prompt),
        ]
    )

    content = response.content

    if not content:
        raise RuntimeError("The financial analyst returned an empty response")

    return str(content).strip()