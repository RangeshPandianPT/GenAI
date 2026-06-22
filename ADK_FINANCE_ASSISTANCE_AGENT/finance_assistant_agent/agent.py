from google.adk.agents import LlmAgent

finance_assistance_agent = LlmAgent(
    name="finance_assistance_agent",
    model="gemini-2.5-flash",
    description="A simple finance assistant that helps with user's finance goals.",
    instruction="""You are a friendly finance assistant.
        You can help answer user's generic questions on finance and help plan
        their finance goals. Be more friendly and positive.
    """,
)

root_agent = finance_assistance_agent
