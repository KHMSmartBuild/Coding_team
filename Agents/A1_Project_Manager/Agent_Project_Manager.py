"""Project Manager Agent Module.

This module provides the Project Manager agent that oversees the entire project,
sets goals, and ensures timely completion. It uses dependency injection and
LLM abstractions for flexible configuration.

Example:
    >>> from core import Container, create_provider
    >>> container = Container()
    >>> provider = create_provider("mock")
    >>> container.register_singleton("llm_provider", provider)
    >>> pm = ProjectManager(container)
    >>> result = pm.initiate_project()
"""

from typing import Any, Dict, List, Optional, Union

# Try to import new core module; fall back to legacy imports if not available
try:
    from core import Container, LLMProvider, MockProvider, create_provider
    _CORE_AVAILABLE = True
except ImportError:
    _CORE_AVAILABLE = False
    Container = None
    LLMProvider = None
    MockProvider = None
    create_provider = None

# Try to import legacy langchain for backward compatibility
try:
    from langchain import LLMChain
    from langchain.llms import OpenAI
    _LANGCHAIN_AVAILABLE = True
except ImportError:
    _LANGCHAIN_AVAILABLE = False
    LLMChain = None
    OpenAI = None


class ProjectManager:
    """Project Manager Agent.

    Oversees the entire project lifecycle including initiation, planning,
    task assignment, monitoring, and evaluation.

    Attributes:
        container: The DI container for service resolution.
        llm_provider: The LLM provider for AI-powered tasks.

    Example:
        >>> pm = ProjectManager.create_with_mock()
        >>> result = pm.initiate_project()
    """

    def __init__(
        self,
        container: Optional["Container"] = None,
        llm_provider: Optional["LLMProvider"] = None,
    ):
        """Initialize the Project Manager.

        Args:
            container: Optional DI container for service resolution.
            llm_provider: Optional LLM provider. If not provided, will be
                resolved from container or created as mock.
        """
        self.container = container
        self._llm_provider = llm_provider

    @property
    def llm_provider(self) -> Optional["LLMProvider"]:
        """Get the LLM provider.

        Lazily resolves the provider from the container if not set.

        Returns:
            The LLM provider instance.
        """
        if self._llm_provider is None:
            if self.container is not None and _CORE_AVAILABLE:
                if self.container.is_registered("llm_provider"):
                    self._llm_provider = self.container.resolve("llm_provider")
        return self._llm_provider

    @classmethod
    def create_with_mock(cls) -> "ProjectManager":
        """Create a ProjectManager with a mock LLM provider.

        Useful for testing and development without API keys.

        Returns:
            A ProjectManager instance with mock provider.

        Example:
            >>> pm = ProjectManager.create_with_mock()
        """
        if not _CORE_AVAILABLE:
            return cls()

        container = Container()
        provider = create_provider("mock", responses=[
            "Project initiation document created.",
            "Project plan created successfully.",
            "Tasks assigned to agents.",
            "Progress report generated.",
            "Project evaluation complete.",
        ])
        container.register_singleton("llm_provider", provider)
        return cls(container=container, llm_provider=provider)

    @classmethod
    def create_with_provider(
        cls,
        provider_type: str,
        api_key: str,
        **kwargs: Any,
    ) -> "ProjectManager":
        """Create a ProjectManager with a specific LLM provider.

        Args:
            provider_type: The type of provider ("openai", "anthropic").
            api_key: The API key for the provider.
            **kwargs: Additional provider configuration.

        Returns:
            A ProjectManager instance with the specified provider.

        Example:
            >>> pm = ProjectManager.create_with_provider(
            ...     "openai", api_key="sk-..."
            ... )
        """
        if not _CORE_AVAILABLE:
            raise ImportError("Core module is required for create_with_provider")

        container = Container()
        provider = create_provider(provider_type, api_key=api_key, **kwargs)
        container.register_singleton("llm_provider", provider)
        return cls(container=container, llm_provider=provider)

    def initiate_project(self, project_description: str = "") -> str:
        """Initiate a new project.

        Creates a project initiation document using the LLM provider.

        Args:
            project_description: Optional description of the project.

        Returns:
            The project initiation document content.

        Example:
            >>> pm = ProjectManager.create_with_mock()
            >>> doc = pm.initiate_project("A new web application")
        """
        prompt = (
            f"Create a project initiation document for a new software "
            f"development project. {project_description}"
        ).strip()

        if self.llm_provider is not None and _CORE_AVAILABLE:
            response = self.llm_provider.generate(prompt)
            return response.content

        # Legacy fallback using langchain
        if _LANGCHAIN_AVAILABLE:
            davinci = OpenAI(model_name='text-davinci-003')
            llm_chain = LLMChain(prompt=prompt, llm=davinci)
            return llm_chain.run(prompt)

        return "Project initiation document (mock)"

    def create_project_plan(self) -> Dict[str, Any]:
        """Create a project plan.

        Returns:
            A dictionary containing the project plan.

        Example:
            >>> pm = ProjectManager.create_with_mock()
            >>> plan = pm.create_project_plan()
        """
        prompt = "Create a detailed project plan with milestones and tasks."

        if self.llm_provider is not None and _CORE_AVAILABLE:
            response = self.llm_provider.generate(prompt)
            return {
                "status": "success",
                "plan": response.content,
            }

        return {
            "status": "success",
            "plan": "Default project plan",
        }

    def assign_tasks_to_agents(
        self,
        agent_tasks: Dict[str, Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Assign tasks to AI agents.

        Args:
            agent_tasks: Dictionary mapping agent names to their tasks.

        Returns:
            A dictionary with assignment results.

        Example:
            >>> pm = ProjectManager.create_with_mock()
            >>> tasks = {"Agent_1": {"task": "Documentation", "status": "Pending"}}
            >>> result = pm.assign_tasks_to_agents(tasks)
        """
        assigned = []
        for agent_name, task_info in agent_tasks.items():
            assigned.append({
                "agent": agent_name,
                "task": task_info.get("task", "Unknown"),
                "status": "Assigned",
            })

        return {
            "status": "success",
            "assignments": assigned,
            "total_assigned": len(assigned),
        }

    def monitor_agents_progress(
        self,
        agent_tasks: Dict[str, Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Monitor the progress of AI agents.

        Args:
            agent_tasks: Dictionary of agent tasks to monitor.

        Returns:
            A dictionary with progress information.

        Example:
            >>> pm = ProjectManager.create_with_mock()
            >>> tasks = {"Agent_1": {"task": "Documentation", "status": "In Progress"}}
            >>> progress = pm.monitor_agents_progress(tasks)
        """
        progress_report = []
        for agent_name, task_info in agent_tasks.items():
            progress_report.append({
                "agent": agent_name,
                "task": task_info.get("task", "Unknown"),
                "status": task_info.get("status", "Unknown"),
            })

        return {
            "status": "success",
            "progress": progress_report,
            "summary": f"Monitoring {len(progress_report)} agents",
        }

    def evaluate_project_success(self) -> Dict[str, Any]:
        """Evaluate the overall project success.

        Returns:
            A dictionary with evaluation results.

        Example:
            >>> pm = ProjectManager.create_with_mock()
            >>> evaluation = pm.evaluate_project_success()
        """
        prompt = "Evaluate the project success based on completed milestones."

        if self.llm_provider is not None and _CORE_AVAILABLE:
            response = self.llm_provider.generate(prompt)
            return {
                "status": "success",
                "evaluation": response.content,
                "score": 0.85,  # Example score
            }

        return {
            "status": "success",
            "evaluation": "Project evaluation complete",
            "score": 0.85,
        }

    def run_project_workflow(
        self,
        agent_tasks: Dict[str, Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Run the complete project management workflow.

        Executes all project management tasks in sequence.

        Args:
            agent_tasks: Dictionary of tasks to assign to agents.

        Returns:
            A dictionary with the complete workflow results.

        Raises:
            Exception: If any workflow step fails.

        Example:
            >>> pm = ProjectManager.create_with_mock()
            >>> tasks = {"Agent_1": {"task": "Documentation", "status": "Pending"}}
            >>> result = pm.run_project_workflow(tasks)
        """
        results = {}

        try:
            results["initiation"] = self.initiate_project()
        except Exception as e:
            raise Exception(f"Error: Project not initiated. {e}")

        try:
            results["plan"] = self.create_project_plan()
        except Exception as e:
            raise Exception(f"Error: Project plan not created. {e}")

        try:
            results["assignments"] = self.assign_tasks_to_agents(agent_tasks)
        except Exception as e:
            raise Exception(f"Error: Tasks not assigned to agents. {e}")

        try:
            results["progress"] = self.monitor_agents_progress(agent_tasks)
        except Exception as e:
            raise Exception(f"Error: AI agents' progress not monitored. {e}")

        try:
            results["evaluation"] = self.evaluate_project_success()
        except Exception as e:
            raise Exception(f"Error: Project success not evaluated. {e}")

        results["workflow_status"] = "complete"
        return results


# Legacy compatibility functions


def initiate_project() -> str:
    """Legacy function: Initiate a project.

    Creates a project initiation document using the default provider.
    Maintained for backward compatibility.

    Returns:
        The project initiation document.
    """
    pm = ProjectManager.create_with_mock()
    return pm.initiate_project()


def create_project_plan() -> bool:
    """Legacy function: Create a project plan.

    Maintained for backward compatibility.

    Returns:
        True if the plan was created successfully.
    """
    pm = ProjectManager.create_with_mock()
    result = pm.create_project_plan()
    return result.get("status") == "success"


def assign_tasks_to_agents(agent_tasks: Dict[str, Dict[str, Any]]) -> bool:
    """Legacy function: Assign tasks to agents.

    Maintained for backward compatibility.

    Args:
        agent_tasks: Dictionary of tasks.

    Returns:
        True if tasks were assigned successfully.
    """
    pm = ProjectManager.create_with_mock()
    result = pm.assign_tasks_to_agents(agent_tasks)
    return result.get("status") == "success"


def monitor_agents_progress(agent_tasks: Dict[str, Dict[str, Any]]) -> bool:
    """Legacy function: Monitor agent progress.

    Maintained for backward compatibility.

    Args:
        agent_tasks: Dictionary of tasks.

    Returns:
        True if monitoring was successful.
    """
    pm = ProjectManager.create_with_mock()
    result = pm.monitor_agents_progress(agent_tasks)
    return result.get("status") == "success"


def evaluate_project_success() -> bool:
    """Legacy function: Evaluate project success.

    Maintained for backward compatibility.

    Returns:
        True if evaluation was successful.
    """
    pm = ProjectManager.create_with_mock()
    result = pm.evaluate_project_success()
    return result.get("status") == "success"


def project_manager(agent_tasks: Dict[str, Dict[str, Any]]) -> bool:
    """Legacy function: Run the project manager workflow.

    Maintained for backward compatibility.

    Args:
        agent_tasks: Dictionary of tasks for the project.

    Returns:
        True if all tasks completed successfully.
    """
    pm = ProjectManager.create_with_mock()
    try:
        result = pm.run_project_workflow(agent_tasks)
        return result.get("workflow_status") == "complete"
    except Exception as e:
        print(str(e))
        raise


# Example usage
if __name__ == "__main__":
    # Define the tasks for the AI agents
    agent_tasks = {
        'Agent_1': {'task': 'Code documentation', 'status': 'Pending'},
        'Agent_2': {'task': 'Code review', 'status': 'Pending'},
        'Agent_3': {'task': 'Code translation', 'status': 'Pending'},
    }

    # Using the new class-based approach
    pm = ProjectManager.create_with_mock()
    result = pm.run_project_workflow(agent_tasks)

    if result.get("workflow_status") == "complete":
        print("Project management tasks completed successfully.")
    else:
        print("Project management tasks failed.")
