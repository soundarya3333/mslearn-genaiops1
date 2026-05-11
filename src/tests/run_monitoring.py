"""Run all test prompts against trail guide prompt versions (v1, v2, v3, v4)
with Application Insights and Foundry tracing enabled.

This script uses Foundry's AI Project client so that requests are visible
in the Foundry portal (Tracing, Resource Usage, etc.), not just in Log Analytics.

It:
1. Gets an OpenAI-compatible client routed through Foundry's API gateway
2. Loads prompt versions from the prompts directory
3. Runs all test prompts against each version
4. Wraps each version in a named trace span for side-by-side comparison
5. Captures token usage, latency, and response data per prompt
"""

import os
import time
import uuid
from pathlib import Path
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.monitor.opentelemetry import configure_azure_monitor
from opentelemetry import trace
from opentelemetry.instrumentation.openai_v2 import OpenAIInstrumentor

# Load environment variables from .env file
load_dotenv()

project_endpoint = os.environ["AZURE_AI_PROJECT_ENDPOINT"]
model_name = os.getenv("MODEL_NAME", "gpt-4.1")

# Connect to Azure AI Project
project_client = AIProjectClient(
    endpoint=project_endpoint,
    credential=DefaultAzureCredential(),
)

# Get the Azure OpenAI client routed through Foundry's API gateway.
# This ensures token usage and traces are visible in Foundry's portal.
chat_client = project_client.get_openai_client()

# Retrieve the Application Insights connection string provisioned alongside the project
connection_string = project_client.telemetry.get_application_insights_connection_string()
print(f"[DEBUG] Connection string: {connection_string}")

os.environ["APPLICATIONINSIGHTS_CONNECTION_STRING"] = connection_string
configure_azure_monitor(connection_string=connection_string)
OpenAIInstrumentor().instrument()

tracer = trace.get_tracer(__name__)

# Paths to prompt versions and test prompts
PROMPTS_DIR = Path(__file__).parent.parent / "agents" / "trail_guide_agent" / "prompts"
TEST_PROMPTS_DIR = Path(__file__).parent / "test-prompts"

# Prompt versions to compare
VERSIONS = ["v1", "v2", "v3", "v4_optimized_concise"]


def load_prompt(version: str) -> str:
    """Load a prompt version from the prompts directory."""
    if version == "v4_optimized_concise":
        return (PROMPTS_DIR / f"{version}.txt").read_text().strip()
    return (PROMPTS_DIR / f"{version}_instructions.txt").read_text().strip()


def load_test_prompts() -> dict:
    """Load all test prompts from the test-prompts directory."""
    return {
        f.stem: f.read_text().strip()
        for f in sorted(TEST_PROMPTS_DIR.glob("*.txt"))
    }


def run_version(version: str, system_prompt: str, test_prompts: dict):
    """Run all test prompts for a single prompt version, wrapped in a trace span."""
    session_id = str(uuid.uuid4())
    print(f"\n{'='*60}")
    print(f"Running {version.upper()} — {len(test_prompts)} test prompts")
    print(f"{'='*60}")

    with tracer.start_as_current_span(f"trail_guide_{version}") as version_span:
        version_span.set_attribute("prompt.version", version)
        version_span.set_attribute("session.id", session_id)
        version_span.set_attribute("model", model_name)

        for test_name, prompt_text in test_prompts.items():
            print(f"\n  Test: {test_name}")

            with tracer.start_as_current_span(f"{version}_{test_name}") as span:
                span.set_attribute("test.name", test_name)
                span.set_attribute("prompt.version", version)
                span.set_attribute("session.id", session_id)

                start = time.time()
                response = chat_client.chat.completions.create(
                    model=model_name,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt_text},
                    ],
                )
                duration = time.time() - start

                output = response.choices[0].message.content
                usage = response.usage

                span.set_attribute("response.duration_s", round(duration, 3))
                span.set_attribute("response.prompt_tokens", usage.prompt_tokens)
                span.set_attribute("response.completion_tokens", usage.completion_tokens)
                span.set_attribute("response.total_tokens", usage.total_tokens)

                print(f"    Duration : {duration:.2f}s")
                print(f"    Tokens   : {usage.total_tokens} "
                      f"(prompt: {usage.prompt_tokens}, completion: {usage.completion_tokens})")
                print(f"    Response : {output[:80]}...")


if __name__ == "__main__":
    test_prompts = load_test_prompts()
    if not test_prompts:
        print(f"No test prompts found in {TEST_PROMPTS_DIR}")
        raise SystemExit(1)

    print(f"Loaded {len(test_prompts)} test prompts")
    print(f"Running versions: {', '.join(VERSIONS)}")

    for version in VERSIONS:
        system_prompt = load_prompt(version)
        run_version(version, system_prompt, test_prompts)

    print(f"\n{'='*60}")
    print("All versions complete.")
    print("Open Azure AI Foundry > Tracing to compare spans across versions.")
    print(f"{'='*60}")

    # Force flush all telemetry before exit
    provider = trace.get_tracer_provider()
    if hasattr(provider, "force_flush"):
        provider.force_flush()
        print("Telemetry flushed.")
