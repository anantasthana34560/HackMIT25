import asyncio
from textwrap import dedent
import os
import csv

from agno.agent import Agent
from agno.tools.mcp import MCPTools
from agno.tools.reasoning import ReasoningTools
from agno.models.anthropic import Claude


async def run_agent(message: str) -> None:
    async with MCPTools(
        "npx -y @openbnb/mcp-server-airbnb --ignore-robots-txt"
    ) as mcp_tools:
        agent = Agent(
            model=Claude(id="claude-opus-4-1-20250805"),
            tools=[ReasoningTools(add_instructions=True), mcp_tools],
            instructions=dedent("""\
            ## General Instructions
            - Always start by using the think tool to map out the steps needed to complete the task.
            - After receiving tool results, use the think tool as a scratchpad to validate the results for correctness
            - Before responding to the user, use the think tool to jot down final thoughts and ideas.
            - Present final outputs in well-organized tables whenever possible.
            - Always provide links to the listings in your response.
            - Show your top 10 recommendations in a table and make a case for why each is the best choice.

            ## Using the think tool
            At every step, use the think tool as a scratchpad to:
            - Restate the object in your own words to ensure full comprehension.
            - List the  specific rules that apply to the current request
            - Check if all required information is collected and is valid
            - Verify that the planned action completes the task\
            """),
            add_datetime_to_context=True,
            markdown=True,
        )
        await agent.aprint_response(message, stream=True)


if __name__ == "__main__":
    # If run normally, run the agent demo
    task = dedent("""\
    I'm traveling to San Francisco from April 20th - May 8th. Can you find me the best deals for a 1 bedroom apartment?
    I'd like a dedicated workspace and close proximity to public transport.\
    """)
    asyncio.run(run_agent(task))

    # Additionally, add keywords to the experiences CSV
    def categorize_keyword(text: str) -> str:
        t = (text or "").lower()
        if any(k in t for k in ["comedy", "improv", "stand-up", "stand up", "laugh"]):
            return "Comedy"
        if any(k in t for k in ["class", "workshop", "lesson", "course", "lecture", "science", "robotics", "stem"]):
            return "Education"
        if any(k in t for k in ["museum", "exhibit", "gallery", "observatory", "planetarium"]):
            return "Museum"
        if any(k in t for k in ["tour", "cruise", "view", "sightseeing", "panoramic", "observatory", "walk", "trail"]):
            return "Sightseeing"
        if any(k in t for k in ["kayak", "kayaking", "bike", "biking", "hike", "hiking", "adventure", "boat", "canoe", "zipline"]):
            return "Adventure"
        if any(k in t for k in ["historic", "history", "historical", "freedom trail", "old state", "colonial", "presidential", "tour of"]):
            return "Historic"
        if any(k in t for k in ["picnic", "tea", "relax", "quiet", "garden", "courtyard"]):
            return "Relaxing"
        return "Sightseeing"

    def add_keyword_column(input_csv: str, output_csv: str) -> None:
        with open(input_csv, newline='', encoding='utf-8') as fin, open(output_csv, 'w', newline='', encoding='utf-8') as fout:
            reader = csv.DictReader(fin)
            fieldnames = reader.fieldnames + ["Keyword"] if reader.fieldnames and "Keyword" not in reader.fieldnames else reader.fieldnames
            writer = csv.DictWriter(fout, fieldnames=fieldnames)
            writer.writeheader()
            for row in reader:
                text = row.get('Experience Description') or row.get('Company Name') or ' '.join(str(v) for v in row.values())
                row["Keyword"] = categorize_keyword(text)
                writer.writerow(row)

    base = os.path.dirname(__file__)
    inp = os.path.join(base, "100 experiences in boston - ok. now can you do 100  experiences and 100 resta....csv")
    outp = os.path.join(base, "experiences_with_keywords.csv")
    try:
        add_keyword_column(inp, outp)
        print(f"Wrote {outp}")
    except FileNotFoundError:
        print("Experiences CSV not found; skipping keyword generation.")