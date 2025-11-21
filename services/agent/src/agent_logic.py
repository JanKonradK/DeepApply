import os
from browser_use import Agent
from langchain_openai import ChatOpenAI
from .rag_engine import KnowledgeBase

class DeepApplyAgent:
    def __init__(self, kb: KnowledgeBase = None):
        self.kb = kb
        # Initialize LLM
        # Using Grok as configured in the environment
        self.llm = ChatOpenAI(
            base_url='https://api.grok.x.ai/v1',
            api_key=os.getenv('GROK_API_KEY'),
            model='grok-beta'
        )

    async def run(self, url: str):
        print(f"Starting application process for: {url}")

        # Construct the task with context if available
        task = f"Navigate to {url}. Detect the job application form. Fill out the fields using the user's profile information. Submit the application if possible, or stop before the final submit if unsure."

        # Create the agent
        agent = Agent(
            task=task,
            llm=self.llm,
            # You might want to pass the browser context or other options here
        )

        # Run the agent
        try:
            history = await agent.run()
            result = history.final_result()
            return result
        except Exception as e:
            print(f"Error running agent: {e}")
            return str(e)
