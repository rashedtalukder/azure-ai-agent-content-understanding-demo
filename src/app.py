import asyncio
import logging
import json
import sys
from config_manager import ConfigManager
from context_managers import AzureCredentialManager, ContentUnderstandingManager, ProjectClientManager
from agent.agent_manager import AgentManager
import config

logging.basicConfig(level=logging.INFO)


async def main():
    cfg = ConfigManager()

    async with AzureCredentialManager() as cred:
        # create analyzer
        async with ContentUnderstandingManager(cfg.azure_endpoint, cfg.azure_api_version, cred) as cu:
            config.ANALYZER_ID = cfg.analyzer_id
            config.CU_CLIENT = cu
            analyzer = cu.begin_create_analyzer(
                analyzer_id=cfg.analyzer_id, analyzer_template_path=cfg.analyzer_template
            )
            result = cu.poll_result(analyzer)
            if result.get("status", "").lower() != "succeeded":
                logging.error("Analyzer creation failed: %s",
                              json.dumps(result, indent=2))
                sys.exit(1)
            logging.info("Analyzer created.")

        # run agent
        async with ProjectClientManager(cred, cfg.foundry_conn_str) as pc:
            async with AgentManager(pc, cfg) as am:
                thread_id, agent_id, response = await am.create_and_run()
                print("Agent response:", response)

        # delete analyzer
        cu.delete_analyzer(analyzer_id=cfg.analyzer_id)
        logging.info("Analyzer deleted.")

if __name__ == "__main__":
    asyncio.run(main())
