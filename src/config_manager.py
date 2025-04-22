import os
import uuid
from dotenv import load_dotenv
from pathlib import Path


class ConfigManager:
    def __init__(self, overrides: dict = None, override_env: bool = False):
        # load or reload .env
        load_dotenv(override=override_env)
        # read environment variables
        self.azure_endpoint = os.getenv("AZURE_AI_ENDPOINT")
        self.azure_api_version = os.getenv("AZURE_AI_API_VERSION")
        self.foundry_conn_str = os.getenv(
            "AZ_FOUNDRY_PROJECT_CONNECTION_STRINGS")
        self.model_deployment = os.getenv("AZ_MODEL_DEPLOYMENT_NAME")
        self.bing_connection = os.getenv("BING_CONNECTION_NAME")
        self.itinerary_url = os.getenv("ITINERARY_FILE_URL")
        self.save_pdf_path = Path(__file__).parent / \
            "output" / "new_itinerary.pdf"
        # runtime analyzer ID and template path
        self.analyzer_id = f"itinerary_analyzer-{uuid.uuid4().hex[:8]}"
        self.analyzer_template = Path(
            __file__).parent / "analyzer_templates" / "itinerary_template.json"

        # apply any overrides
        if overrides:
            for key, val in overrides.items():
                if hasattr(self, key):
                    setattr(self, key, val)

        # validate required configuration
        required = {
            "azure_endpoint": self.azure_endpoint,
            "azure_api_version": self.azure_api_version,
            "foundry_conn_str": self.foundry_conn_str,
            "model_deployment": self.model_deployment,
            "bing_connection": self.bing_connection,
            "itinerary_url": self.itinerary_url,
        }
        missing = [name for name, val in required.items() if not val]
        if missing:
            raise EnvironmentError(
                f"Missing required configuration: {', '.join(missing)}")
