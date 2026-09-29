from langchain_core.messages import HumanMessage, SystemMessage

from astock_agent.schemas.financial import FinancialSummary
from astock_agent.schemas.stock import MarketSummary
from astock_agent.services.llm import get_llm

SYSTEM_PROMPT = """
你是一名谨慎、客观的A股研究报告编辑。

你的任务是整合行情分析和财务分析，生成一份结构清晰的中文研究报告。

要求：
1. 只能使用输入中提供的数据和分析，不得编造新闻、估值、公司事件或行业信息。
2. 如果文字分析与结构化数据冲突，优先采用结构化数据。
3. 不得把股价变化直接归因于财务变化，除非输入中提供了明确证据。
4. 必须区分行情数据区间、财务报告期和财报披露日期。
5. 明确区分客观数据与分析判断。
6. 数据不足时必须说明局限。
7. 不给出目标价，不承诺收益，不输出绝对化投资建议。
8. 使用简洁、专业的中文。
""".strip()


def synthesize_research(
    market_summary: MarketSummary,
    financial_summary: FinancialSummary,
    market_report: str,
    financial_report: str,
) -> str:
    """Combine market and financial analyses into one research report."""

    llm = get_llm()

    user_prompt = f"""
请根据以下材料生成一份A股综合研究报告。

【结构化行情摘要】
{market_summary.model_dump_json(indent=2)}

【行情分析报告】
{market_report}

【结构化财务摘要】
{financial_summary.model_dump_json(indent=2)}

【财务分析报告】
{financial_report}

请按照以下结构输出：
1. 研究摘要
2. 行情表现
3. 财务表现
4. 综合观察
5. 主要风险与数据局限

综合观察只能总结数据共同呈现的特征，不得自行编造因果关系。
""".strip()

    response = llm.invoke(
        [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=user_prompt),
        ]
    )

    content = response.content

    if not content:
        raise RuntimeError("The research synthesizer returned an empty response")

    return str(content).strip()
