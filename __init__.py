"""Coding Team Package.

A comprehensive framework for AI-powered coding assistance with:
- Multiple specialized AI agents (Project Manager, Architect, Developers, etc.)
- Core infrastructure (DI Container, LLM Providers, Tools Framework)
- Helper utilities for common operations

Example:
    >>> from Agents.A1_Project_Manager import ProjectManager
    >>> pm = ProjectManager.create_with_mock()
    >>> result = pm.initiate_project()

Core Module Example:
    >>> from core import Container, create_provider, ToolRegistry
    >>> container = Container()
    >>> provider = create_provider("mock")
"""


def __getattr__(name):
    """Lazy import of submodules and classes.

    This allows importing from the package without loading all submodules
    until they are actually needed.

    Args:
        name: The name of the attribute to import.

    Returns:
        The imported module or class.

    Raises:
        AttributeError: If the attribute is not found.
    """
    # Core module components
    core_components = {
        "Container",
        "ContainerError",
        "ServiceLifetime",
        "LLMProvider",
        "LLMConfig",
        "LLMResponse",
        "MockProvider",
        "OpenAIProvider",
        "AnthropicProvider",
        "create_provider",
        "Tool",
        "ToolRegistry",
        "FunctionTool",
        "create_default_registry",
    }

    if name in core_components:
        try:
            from core import (
                Container,
                ContainerError,
                ServiceLifetime,
                LLMProvider,
                LLMConfig,
                LLMResponse,
                MockProvider,
                OpenAIProvider,
                AnthropicProvider,
                create_provider,
                Tool,
                ToolRegistry,
                FunctionTool,
                create_default_registry,
            )

            return locals()[name]
        except ImportError:
            pass

    # Agent imports
    agent_mapping = {
        "Agent_Project_Manager": "Agents.A1_Project_Manager",
        "Agent_Software_Architect": "Agents.A2_Software_Architect",
        "Agent_Frontend_Developer": "Agents.A3_Frontend_Developer",
        "Agent_Backend_Developer": "Agents.A4_Backend_Developer",
        "Agent_Data_Engineer": "Agents.A5_Data_Engineer",
        "Agent_Data_Scientist": "Agents.A6_Data_Scientist",
        "Agent_Machine_Learning_Engineer": "Agents.A7_Machine_Learning_Engineer",
        "Agent_DevOps_Engineer": "Agents.A8_DevOps_Engineer",
        "Agent_Quality_Assurance_Engineer": "Agents.A9_Quality_Assurance_Engineer",
        "Agent_Security_Engineer": "Agents.A10_Security_Engineer",
    }

    if name in agent_mapping:
        import importlib

        try:
            module = importlib.import_module(agent_mapping[name])
            return getattr(module, name)
        except (ImportError, AttributeError):
            pass

    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")


# Minimal explicit imports for backward compatibility
# These are loaded immediately to maintain compatibility with existing code
try:
    from Agents.A1_Project_Manager import Agent_Project_Manager
    from Agents.A2_Software_Architect import Agent_Software_Architect
    from Agents.A3_Frontend_Developer import Agent_Frontend_Developer
    from Agents.A4_Backend_Developer import Agent_Backend_Developer
    from Agents.A5_Data_Engineer import Agent_Data_Engineer
    from Agents.A6_Data_Scientist import Agent_Data_Scientist
    from Agents.A7_Machine_Learning_Engineer import Agent_Machine_Learning_Engineer
    from Agents.A8_DevOps_Engineer import Agent_DevOps_Engineer
    from Agents.A9_Quality_Assurance_Engineer import Agent_Quality_Assurance_Engineer
    from Agents.A10_Security_Engineer import Agent_Security_Engineer
except ImportError:
    # Graceful fallback if agent imports fail
    pass

# Task script imports with graceful fallback
try:
    from Agents.A1_Project_Manager import (
        Change_Management,
        make_a_decision,
        Resource_Allocation,
        Risk_Analysis,
        Team_Collaboration,
    )
except (ImportError, FileNotFoundError, Exception):
    pass

try:
    from Agents.A2_Software_Architect import (
        Bottleneck_Identification,
        Code_Quality_Analysis,
        System_Requirements_Analysis,
    )
except (ImportError, Exception):
    pass

try:
    from Agents.A3_Frontend_Developer import (
        Frontend_Test_Automation,
        Usability_Analysis,
    )
except (ImportError, Exception):
    pass

try:
    from Agents.A4_Backend_Developer import (
        Backend_Test_Automation,
        Database_Analysis,
    )
except (ImportError, Exception):
    pass

try:
    from Agents.A5_Data_Engineer import (
        Data_Pipeline_Implementation,
        Data_Validation,
    )
except (ImportError, Exception):
    pass

try:
    from Agents.A6_Data_Scientist import (
        Model_Implementation,
        Visualization_Creation,
    )
except (ImportError, Exception):
    pass

try:
    from Agents.A7_Machine_Learning_Engineer import (
        Model_Deployment_API,
        Model_Deployment_Integration,
        Model_Optimization,
    )
except (ImportError, Exception):
    pass

try:
    from Agents.A8_DevOps_Engineer import (
        Deployment_Automation,
        Monitoring_and_Alerting,
    )
except (ImportError, Exception):
    pass

try:
    from Agents.A9_Quality_Assurance_Engineer import (
        Test_Execution_and_Reporting,
        Test_Plan_Creation,
    )
except (ImportError, Exception):
    pass

try:
    from Agents.A10_Security_Engineer import (
        Security_Assessment,
        Security_Improvement_Recommendations,
    )
except (ImportError, Exception):
    pass

# Docs imports with graceful fallback
try:
    from docs import agent_dataset_requirements, data_augmentation_script, Tasks_status
except (ImportError, Exception):
    pass
