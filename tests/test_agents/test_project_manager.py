"""
Tests for the Project Manager Agent.

This module contains unit tests for the ProjectManager class
and related functionality.
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from Agents.A1_Project_Manager.Agent_Project_Manager import (
    ProjectManager,
    AgentTask,
    # Legacy functions
    initiate_project,
    create_project_plan,
    assign_tasks_to_agents,
    monitor_agents_progress,
    evaluate_project_success,
    project_manager,
)
from core.llm_provider import MockLLMProvider, LLMConfig


class TestAgentTask:
    """Test suite for AgentTask dataclass."""

    def test_task_creation(self):
        """Test basic task creation."""
        task = AgentTask(
            agent_id="Agent_1",
            task="Code review"
        )
        assert task.agent_id == "Agent_1"
        assert task.task == "Code review"
        assert task.status == "Pending"
        assert task.priority == 3

    def test_task_with_all_fields(self):
        """Test task with all fields."""
        task = AgentTask(
            agent_id="Agent_2",
            task="Testing",
            status="In Progress",
            priority=1,
            assigned_at="2024-01-15T10:00:00",
            metadata={"type": "unit"}
        )
        assert task.status == "In Progress"
        assert task.priority == 1
        assert task.metadata["type"] == "unit"


class TestProjectManager:
    """Test suite for ProjectManager class."""

    @pytest.fixture
    def mock_provider(self):
        """Create a mock LLM provider."""
        provider = MockLLMProvider()
        provider.set_responses([
            "Project initiation document",
            "Project plan content",
            "Evaluation report"
        ])
        return provider

    @pytest.fixture
    def manager(self, mock_provider):
        """Create a ProjectManager with mock provider."""
        return ProjectManager(
            llm_provider=mock_provider,
            project_name="Test Project"
        )

    def test_initialization(self, manager):
        """Test manager initialization."""
        assert manager.project_name == "Test Project"
        assert manager.llm_provider is not None
        assert len(manager.tasks) == 0

    def test_initialization_without_provider(self):
        """Test manager initializes with mock when no provider given."""
        manager = ProjectManager(project_name="No Provider Project")
        # Should use mock provider by default
        assert manager.llm_provider is not None

    def test_initiate_project(self, manager):
        """Test project initiation."""
        result = manager.initiate_project()
        assert result is not None
        assert isinstance(result, str)
        assert manager._initialized is True

    def test_initiate_project_with_custom_prompt(self, manager):
        """Test project initiation with custom prompt."""
        custom = "Create a mobile app project"
        result = manager.initiate_project(custom_prompt=custom)
        assert result is not None

    def test_create_project_plan(self, manager):
        """Test project plan creation."""
        plan = manager.create_project_plan()
        assert plan is not None
        assert "project_name" in plan
        assert plan["project_name"] == "Test Project"
        assert plan["status"] == "Created"

    def test_create_project_plan_with_requirements(self, manager):
        """Test project plan with requirements."""
        plan = manager.create_project_plan(requirements="Build REST API")
        assert plan is not None
        assert "content" in plan

    def test_assign_tasks_to_agents(self, manager):
        """Test task assignment."""
        tasks = {
            "Agent_1": {"task": "Review code", "priority": 1},
            "Agent_2": {"task": "Write tests", "priority": 2},
        }
        result = manager.assign_tasks_to_agents(tasks)
        assert result is True
        assert len(manager.tasks) == 2
        assert "Agent_1" in manager.tasks
        assert manager.tasks["Agent_1"].task == "Review code"
        assert manager.tasks["Agent_1"].priority == 1

    def test_task_assignment_sets_timestamp(self, manager):
        """Test that task assignment sets timestamp."""
        tasks = {"Agent_1": {"task": "Test task"}}
        manager.assign_tasks_to_agents(tasks)
        assert manager.tasks["Agent_1"].assigned_at is not None

    def test_monitor_agents_progress(self, manager):
        """Test progress monitoring."""
        tasks = {
            "Agent_1": {"task": "Task 1", "status": "Completed"},
            "Agent_2": {"task": "Task 2", "status": "In Progress"},
            "Agent_3": {"task": "Task 3", "status": "Pending"},
        }
        manager.assign_tasks_to_agents(tasks)

        progress = manager.monitor_agents_progress()
        assert progress["total_tasks"] == 3
        assert progress["completed"] == 1
        assert progress["in_progress"] == 1
        assert progress["pending"] == 1
        assert progress["completion_rate"] == pytest.approx(33.33, rel=0.1)

    def test_monitor_progress_empty_tasks(self, manager):
        """Test progress monitoring with no tasks."""
        progress = manager.monitor_agents_progress()
        assert progress["total_tasks"] == 0
        assert progress["completion_rate"] == 0

    def test_monitor_progress_updates_status(self, manager):
        """Test that monitoring updates task status."""
        manager.assign_tasks_to_agents({"Agent_1": {"task": "Test"}})

        # Update status
        manager.monitor_agents_progress({"Agent_1": {"status": "Completed"}})

        assert manager.tasks["Agent_1"].status == "Completed"

    def test_evaluate_project_success(self, manager):
        """Test project evaluation."""
        tasks = {
            "Agent_1": {"task": "Task 1", "status": "Completed"},
            "Agent_2": {"task": "Task 2", "status": "Completed"},
        }
        manager.assign_tasks_to_agents(tasks)

        evaluation = manager.evaluate_project_success()
        assert evaluation is not None
        assert "project_name" in evaluation
        assert "metrics" in evaluation
        assert "overall_success" in evaluation

    def test_evaluate_success_with_all_completed(self, manager):
        """Test evaluation with all tasks completed."""
        tasks = {
            "Agent_1": {"task": "Task 1", "status": "Completed"},
        }
        manager.assign_tasks_to_agents(tasks)

        evaluation = manager.evaluate_project_success()
        assert evaluation["overall_success"] is True

    def test_evaluate_success_with_failures(self, manager):
        """Test evaluation with failed tasks."""
        tasks = {
            "Agent_1": {"task": "Task 1", "status": "Failed"},
        }
        manager.assign_tasks_to_agents(tasks)

        evaluation = manager.evaluate_project_success()
        assert evaluation["overall_success"] is False

    def test_run_workflow(self, manager):
        """Test complete workflow execution."""
        tasks = {
            "Agent_1": {"task": "Task 1", "status": "Completed"},
        }

        # Set up multiple responses
        manager.llm_provider.set_responses([
            "Initiation doc",
            "Project plan",
            "Evaluation"
        ])

        result = manager.run(tasks)
        assert isinstance(result, bool)

    def test_run_workflow_empty_tasks(self, manager):
        """Test workflow with empty tasks."""
        manager.llm_provider.set_responses([
            "Initiation doc",
            "Project plan",
            "Evaluation"
        ])

        result = manager.run({})
        assert isinstance(result, bool)


class TestProjectManagerWithConfig:
    """Test ProjectManager with LLMConfig."""

    def test_initialization_with_config(self):
        """Test initialization with LLMConfig."""
        config = LLMConfig(
            api_key="test_key",
            model="gpt-4",
            temperature=0.5
        )
        # This should not raise, even without valid API key
        manager = ProjectManager(llm_config=config)
        assert manager is not None


class TestLegacyFunctions:
    """Test legacy backward-compatible functions."""

    def test_initiate_project_legacy(self):
        """Test legacy initiate_project function."""
        # Should not raise, uses mock internally
        result = initiate_project()
        assert result is not None

    def test_create_project_plan_legacy(self):
        """Test legacy create_project_plan function."""
        result = create_project_plan()
        assert result is True

    def test_assign_tasks_legacy(self):
        """Test legacy assign_tasks_to_agents function."""
        tasks = {"Agent_1": {"task": "Test"}}
        result = assign_tasks_to_agents(tasks)
        assert result is True

    def test_monitor_progress_legacy(self):
        """Test legacy monitor_agents_progress function."""
        tasks = {"Agent_1": {"status": "Pending"}}
        result = monitor_agents_progress(tasks)
        assert result is True

    def test_evaluate_success_legacy(self):
        """Test legacy evaluate_project_success function."""
        result = evaluate_project_success()
        assert result is True

    def test_project_manager_legacy(self):
        """Test legacy project_manager function."""
        tasks = {"Agent_1": {"task": "Test", "status": "Pending"}}
        result = project_manager(tasks)
        assert isinstance(result, bool)


class TestProjectManagerEdgeCases:
    """Test edge cases for ProjectManager."""

    def test_generate_content_without_provider(self):
        """Test content generation when provider fails."""
        manager = ProjectManager()
        manager.llm_provider = None  # Force no provider

        result = manager._generate_content("Test prompt")
        assert "[Placeholder:" in result

    def test_task_with_missing_fields(self):
        """Test task assignment with minimal fields."""
        manager = ProjectManager()
        tasks = {"Agent_1": {"task": "Minimal task"}}
        result = manager.assign_tasks_to_agents(tasks)
        assert result is True
        assert manager.tasks["Agent_1"].status == "Pending"
        assert manager.tasks["Agent_1"].priority == 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
