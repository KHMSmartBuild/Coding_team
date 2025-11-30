"""
Agent 1 - Project Manager Agent.

This module implements the Project Manager agent responsible for overseeing
software development projects, setting goals, and ensuring timely completion.
The agent manages AI sub-agents, assigns tasks, and monitors progress.

The script has the following steps:
    1. Initiate the project
    2. Create a project plan
    3. Assign tasks to AI agents
    4. Monitor AI agents' progress
    5. Evaluate project success

Example:
    >>> from Agents.A1_Project_Manager.Agent_Project_Manager import ProjectManager
    >>> manager = ProjectManager()
    >>> result = manager.run(agent_tasks)

Attributes:
    ProjectManager: Main class for project management operations.

TODO(feature): Add support for multi-project management
TODO(feature): Add Gantt chart generation
TODO(enhancement): Add real-time progress notifications
"""

import logging
import sys
import os
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

# Add project root to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Use standard logging with fallback
try:
    from helpers.logging_config import get_logger
    logger = get_logger(__name__)
except ImportError:
    logger = logging.getLogger(__name__)

# NOTE: LLM imports are optional - graceful fallback if not available
try:
    from core.llm_provider import (
        LLMConfig,
        LLMProvider,
        LLMResponse,
        OpenAIProvider,
        MockLLMProvider,
        Message,
        create_provider,
    )
    from core.container import Container, get_global_container
    HAS_CORE = True
except ImportError:
    HAS_CORE = False
    LLMConfig = None
    LLMProvider = None

logger = get_logger(__name__)


@dataclass
class AgentTask:
    """Represents a task assigned to an AI agent.

    Attributes:
        agent_id: Unique identifier for the agent.
        task: Description of the task.
        status: Current status (Pending, In Progress, Completed, Failed).
        priority: Task priority (1-5, 1 being highest).
        assigned_at: Timestamp when task was assigned.
        completed_at: Timestamp when task was completed.

    Example:
        >>> task = AgentTask(
        ...     agent_id="Agent_1",
        ...     task="Code documentation",
        ...     status="Pending",
        ...     priority=2
        ... )
    """
    agent_id: str
    task: str
    status: str = "Pending"
    priority: int = 3
    assigned_at: Optional[str] = None
    completed_at: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class ProjectManager:
    """Project Manager Agent for overseeing software development projects.

    This class implements the Project Manager agent that coordinates
    AI sub-agents, manages project timelines, and ensures successful
    project delivery.

    Attributes:
        llm_provider: The LLM provider for generating content.
        container: Dependency injection container.
        project_name: Name of the current project.
        tasks: Dictionary of agent tasks.

    Example:
        >>> manager = ProjectManager(
        ...     llm_config=LLMConfig(api_key='xxx', model='gpt-4')
        ... )
        >>> result = manager.initiate_project()

    Note:
        The LLM provider is optional. Without it, the agent operates
        in a limited capacity with placeholder responses.
    """

    DEFAULT_PROMPTS = {
        "initiation": """Create a comprehensive project initiation document for a 
new software development project. Include:
1. Project overview and objectives
2. Scope and deliverables
3. Key stakeholders
4. Success criteria
5. Initial timeline estimates
6. Risk assessment""",
        "planning": """Create a detailed project plan including:
1. Work breakdown structure
2. Resource allocation
3. Timeline with milestones
4. Dependencies
5. Communication plan""",
        "evaluation": """Evaluate the project success based on:
1. Deliverable completion
2. Timeline adherence
3. Quality metrics
4. Stakeholder satisfaction
5. Lessons learned"""
    }

    def __init__(
        self,
        llm_config: Optional['LLMConfig'] = None,
        llm_provider: Optional['LLMProvider'] = None,
        container: Optional['Container'] = None,
        project_name: str = "Default Project"
    ) -> None:
        """Initialize the Project Manager agent.

        Args:
            llm_config: Configuration for the LLM provider.
            llm_provider: Pre-configured LLM provider (overrides config).
            container: Dependency injection container.
            project_name: Name of the project to manage.
        """
        self.project_name = project_name
        self.tasks: Dict[str, AgentTask] = {}
        self._initialized = False

        # Set up dependency injection
        if HAS_CORE:
            self.container = container or get_global_container()
            self._setup_llm_provider(llm_config, llm_provider)
        else:
            self.container = None
            self.llm_provider = None
            logger.warning(
                "Core module not available. Running in limited mode."
            )

        logger.info(f"ProjectManager initialized for '{project_name}'")

    def _setup_llm_provider(
        self,
        config: Optional['LLMConfig'],
        provider: Optional['LLMProvider']
    ) -> None:
        """Set up the LLM provider.

        Args:
            config: LLM configuration.
            provider: Pre-configured provider.
        """
        if provider:
            self.llm_provider = provider
        elif config:
            self.llm_provider = create_provider("openai", config)
        elif self.container and self.container.has("llm_provider"):
            self.llm_provider = self.container.resolve("llm_provider")
        else:
            # Default to mock provider for testing
            self.llm_provider = MockLLMProvider() if HAS_CORE else None
            logger.info("Using mock LLM provider (no API key configured)")

    def _generate_content(
        self,
        prompt: str,
        system_message: str = "You are a professional project manager."
    ) -> str:
        """Generate content using the LLM provider.

        Args:
            prompt: The user prompt.
            system_message: System message for context.

        Returns:
            Generated content string.
        """
        if not self.llm_provider:
            logger.warning("No LLM provider available, returning placeholder")
            return f"[Placeholder: Response to '{prompt[:50]}...']"

        try:
            messages = [
                Message(role="system", content=system_message),
                Message(role="user", content=prompt)
            ]
            response = self.llm_provider.generate_chat(messages)
            return response.content
        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            return f"[Error generating content: {str(e)}]"

    def initiate_project(self, custom_prompt: Optional[str] = None) -> str:
        """Initiate a new project and generate initiation document.

        This method creates a comprehensive project initiation document
        using the LLM provider. The document includes project overview,
        objectives, scope, stakeholders, and initial estimates.

        Args:
            custom_prompt: Optional custom prompt for initiation.

        Returns:
            The generated project initiation document.

        Raises:
            RuntimeError: If project initiation fails.

        Example:
            >>> manager = ProjectManager()
            >>> doc = manager.initiate_project()
            >>> print(doc)
        """
        logger.info(f"Initiating project: {self.project_name}")

        prompt = custom_prompt or self.DEFAULT_PROMPTS["initiation"]
        prompt = f"Project: {self.project_name}\n\n{prompt}"

        initiation_document = self._generate_content(prompt)

        if not initiation_document:
            logger.error("Failed to generate initiation document")
            raise RuntimeError("Project initiation failed")

        self._initialized = True
        logger.info("Project initiation completed successfully")
        return initiation_document

    def create_project_plan(self, requirements: Optional[str] = None) -> Dict[str, Any]:
        """Create a detailed project plan.

        This method generates a comprehensive project plan including
        work breakdown structure, timeline, and resource allocation.

        Args:
            requirements: Optional project requirements to include.

        Returns:
            Dictionary containing the project plan.

        Example:
            >>> plan = manager.create_project_plan("Build a web app")
            >>> print(plan['timeline'])
        """
        logger.info("Creating project plan")

        prompt = self.DEFAULT_PROMPTS["planning"]
        if requirements:
            prompt = f"Requirements: {requirements}\n\n{prompt}"

        plan_content = self._generate_content(prompt)

        plan = {
            "project_name": self.project_name,
            "content": plan_content,
            "status": "Created",
            "version": "1.0"
        }

        logger.info("Project plan created successfully")
        return plan

    def assign_tasks_to_agents(self, agent_tasks: Dict[str, Dict[str, Any]]) -> bool:
        """Assign tasks to AI agents.

        This method assigns tasks to the appropriate AI agents based
        on the provided task definitions.

        Args:
            agent_tasks: Dictionary mapping agent IDs to task definitions.
                Each task should have 'task' and optionally 'status', 'priority'.

        Returns:
            True if all tasks were assigned successfully.

        Example:
            >>> tasks = {
            ...     'Agent_1': {'task': 'Code review', 'priority': 1},
            ...     'Agent_2': {'task': 'Testing', 'priority': 2}
            ... }
            >>> success = manager.assign_tasks_to_agents(tasks)
        """
        logger.info(f"Assigning {len(agent_tasks)} tasks to agents")

        from datetime import datetime

        for agent_id, task_def in agent_tasks.items():
            task = AgentTask(
                agent_id=agent_id,
                task=task_def.get('task', 'Unspecified task'),
                status=task_def.get('status', 'Pending'),
                priority=task_def.get('priority', 3),
                assigned_at=datetime.now().isoformat(),
                metadata=task_def.get('metadata', {})
            )
            self.tasks[agent_id] = task
            logger.debug(f"Assigned task to {agent_id}: {task.task}")

        logger.info("All tasks assigned successfully")
        return True

    def monitor_agents_progress(
        self,
        agent_tasks: Optional[Dict[str, Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """Monitor the progress of AI agents.

        This method checks the status of all assigned tasks and
        compiles a progress report.

        Args:
            agent_tasks: Optional updated task status dictionary.

        Returns:
            Dictionary containing progress metrics and status.

        Example:
            >>> progress = manager.monitor_agents_progress()
            >>> print(f"Completion: {progress['completion_rate']}%")
        """
        logger.info("Monitoring agent progress")

        # Update task statuses if provided
        if agent_tasks:
            for agent_id, status in agent_tasks.items():
                if agent_id in self.tasks:
                    self.tasks[agent_id].status = status.get('status', 'Unknown')

        # Compile progress report
        total = len(self.tasks)
        completed = sum(1 for t in self.tasks.values() if t.status == "Completed")
        in_progress = sum(1 for t in self.tasks.values() if t.status == "In Progress")
        pending = sum(1 for t in self.tasks.values() if t.status == "Pending")
        failed = sum(1 for t in self.tasks.values() if t.status == "Failed")

        progress = {
            "total_tasks": total,
            "completed": completed,
            "in_progress": in_progress,
            "pending": pending,
            "failed": failed,
            "completion_rate": (completed / total * 100) if total > 0 else 0,
            "tasks": {
                agent_id: {
                    "task": task.task,
                    "status": task.status,
                    "priority": task.priority
                }
                for agent_id, task in self.tasks.items()
            }
        }

        logger.info(f"Progress: {progress['completion_rate']:.1f}% complete")
        return progress

    def evaluate_project_success(self) -> Dict[str, Any]:
        """Evaluate the overall project success.

        This method analyzes project metrics and generates
        a success evaluation report.

        Returns:
            Dictionary containing evaluation results.

        Example:
            >>> evaluation = manager.evaluate_project_success()
            >>> print(f"Success: {evaluation['overall_success']}")
        """
        logger.info("Evaluating project success")

        progress = self.monitor_agents_progress()

        # Generate LLM evaluation
        prompt = f"""
        {self.DEFAULT_PROMPTS['evaluation']}

        Current metrics:
        - Completion rate: {progress['completion_rate']:.1f}%
        - Completed tasks: {progress['completed']}/{progress['total_tasks']}
        - Failed tasks: {progress['failed']}
        """

        evaluation_content = self._generate_content(prompt)

        evaluation = {
            "project_name": self.project_name,
            "metrics": progress,
            "evaluation": evaluation_content,
            "overall_success": progress['completion_rate'] >= 80 and progress['failed'] == 0
        }

        logger.info(f"Evaluation complete. Success: {evaluation['overall_success']}")
        return evaluation

    def run(self, agent_tasks: Dict[str, Dict[str, Any]]) -> bool:
        """Run the complete project management workflow.

        This method executes all project management steps in sequence:
        initiation, planning, task assignment, monitoring, and evaluation.

        Args:
            agent_tasks: Dictionary of agent tasks to manage.

        Returns:
            True if all steps completed successfully.

        Raises:
            Exception: If any step fails critically.

        Example:
            >>> tasks = {'Agent_1': {'task': 'Review code', 'status': 'Pending'}}
            >>> success = manager.run(tasks)
        """
        logger.info(f"Starting project management workflow for '{self.project_name}'")

        try:
            # Step 1: Initiate project
            initiation_doc = self.initiate_project()
            logger.debug(f"Initiation document created ({len(initiation_doc)} chars)")
        except Exception as e:
            logger.error(f"Project initiation failed: {e}")
            raise

        try:
            # Step 2: Create project plan
            project_plan = self.create_project_plan()
            logger.debug(f"Project plan created: {project_plan['status']}")
        except Exception as e:
            logger.error(f"Project planning failed: {e}")
            raise

        try:
            # Step 3: Assign tasks
            tasks_assigned = self.assign_tasks_to_agents(agent_tasks)
            if not tasks_assigned:
                raise RuntimeError("Task assignment failed")
        except Exception as e:
            logger.error(f"Task assignment failed: {e}")
            raise

        try:
            # Step 4: Monitor progress
            progress = self.monitor_agents_progress()
            logger.debug(f"Current progress: {progress['completion_rate']:.1f}%")
        except Exception as e:
            logger.error(f"Progress monitoring failed: {e}")
            raise

        try:
            # Step 5: Evaluate success
            evaluation = self.evaluate_project_success()
            success = evaluation['overall_success']
        except Exception as e:
            logger.error(f"Project evaluation failed: {e}")
            raise

        logger.info(
            f"Project management workflow completed. Success: {success}"
        )
        return success


# Legacy function for backward compatibility
# DEPRECATED: Use ProjectManager class instead
def initiate_project() -> str:
    """Initiate a project (deprecated).

    This function is deprecated. Use ProjectManager.initiate_project() instead.

    Returns:
        Project initiation document string.

    .. deprecated::
        Use :class:`ProjectManager` instead.
    """
    logger.warning(
        "initiate_project() is deprecated. Use ProjectManager class instead."
    )
    manager = ProjectManager()
    return manager.initiate_project()


def create_project_plan() -> bool:
    """Create project plan (deprecated).

    Returns:
        True for backward compatibility.

    .. deprecated::
        Use :class:`ProjectManager` instead.
    """
    logger.warning(
        "create_project_plan() is deprecated. Use ProjectManager class instead."
    )
    return True


def assign_tasks_to_agents(agent_tasks: Dict[str, Dict[str, Any]]) -> bool:
    """Assign tasks to agents (deprecated).

    Args:
        agent_tasks: Task definitions.

    Returns:
        True for backward compatibility.

    .. deprecated::
        Use :class:`ProjectManager` instead.
    """
    logger.warning(
        "assign_tasks_to_agents() is deprecated. Use ProjectManager class instead."
    )
    return True


def monitor_agents_progress(agent_tasks: Dict[str, Dict[str, Any]]) -> bool:
    """Monitor agent progress (deprecated).

    Args:
        agent_tasks: Task status updates.

    Returns:
        True for backward compatibility.

    .. deprecated::
        Use :class:`ProjectManager` instead.
    """
    logger.warning(
        "monitor_agents_progress() is deprecated. Use ProjectManager class instead."
    )
    return True


def evaluate_project_success() -> bool:
    """Evaluate project success (deprecated).

    Returns:
        True for backward compatibility.

    .. deprecated::
        Use :class:`ProjectManager` instead.
    """
    logger.warning(
        "evaluate_project_success() is deprecated. Use ProjectManager class instead."
    )
    return True


def project_manager(agent_tasks: Dict[str, Dict[str, Any]]) -> bool:
    """Run project management workflow (deprecated).

    This function is deprecated. Use ProjectManager.run() instead.

    Args:
        agent_tasks: Dictionary of agent tasks.

    Returns:
        True if successful, False otherwise.

    .. deprecated::
        Use :class:`ProjectManager` instead.
    """
    logger.warning(
        "project_manager() is deprecated. Use ProjectManager class instead."
    )
    manager = ProjectManager()
    try:
        return manager.run(agent_tasks)
    except Exception as e:
        logger.error(f"Project management failed: {e}")
        return False


# Example usage
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO)

    # Define tasks for AI agents
    agent_tasks = {
        'Agent_1': {'task': 'Code documentation', 'status': 'Pending', 'priority': 2},
        'Agent_2': {'task': 'Code review', 'status': 'Pending', 'priority': 1},
        'Agent_3': {'task': 'Code translation', 'status': 'Pending', 'priority': 3},
    }

    # Create and run project manager
    manager = ProjectManager(project_name="Sample Development Project")

    try:
        success = manager.run(agent_tasks)
        if success:
            print("Project management tasks completed successfully.")
        else:
            print("Project management tasks completed with issues.")
    except Exception as e:
        print(f"Project management failed: {e}")
