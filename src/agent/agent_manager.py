import logging
from pathlib import Path
import asyncio
from azure.ai.projects.models import AsyncFunctionTool, AsyncToolSet, BingGroundingTool, MessageRole
from tool_functions import travel_functions


class AgentManager:
    def __init__(self, project_client, config):
        self.pc = project_client
        self.cfg = config

    async def __aenter__(self):
        # build toolset
        self.tools = AsyncToolSet()
        self.tools.add(AsyncFunctionTool(functions=travel_functions))
        try:
            conn = await self.pc.connections.get(connection_name=self.cfg.bing_connection)
            self.tools.add(BingGroundingTool(connection_id=conn.id))
        except Exception as e:
            logging.warning("Bing tool failed: %s", e)
        # create agent
        self.agent = await self.pc.agents.create_agent(
            model=self.cfg.model_deployment,
            name="travel-recommender",
            instructions="...existing instructions...",  # elided for brevity
            toolset=self.tools,
            headers={"x-ms-enable-preview": "true"},
        )
        return self

    async def create_and_run(self):
        thread = await self.pc.agents.create_thread()
        self.thread_id = thread.id
        await self.pc.agents.create_message(
            thread_id=self.thread_id,
            role=MessageRole.USER,
            content=(
                f"Suggest additional activities based on my existing itinerary at {self.cfg.itinerary_url}. "
                f"Please save the new itinerary to {self.cfg.save_pdf_path}."
            ),
        )
        run = await self.pc.agents.create_and_process_run(
            thread_id=self.thread_id, agent_id=self.agent.id
        )
        if run.status != "completed":
            logging.error("Run failed: %s", run.last_error)
        messages = await self.pc.agents.list_messages(thread_id=self.thread_id)
        last = messages.get_last_text_message_by_role(MessageRole.AGENT)
        self.agent_id = self.agent.id
        return self.thread_id, self.agent_id, last.text.value if last else None

    async def __aexit__(self, exc_type, exc, tb):
        await self.pc.agents.delete_thread(self.thread_id)
        await self.pc.agents.delete_agent(self.agent_id)
