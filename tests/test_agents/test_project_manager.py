"""Tests for the Project Manager Agent.

This module contains comprehensive tests for the modernized Project Manager
agent with dependency injection and LLM abstractions.
"""

import pytest
from Agents.A1_Project_Manager.Agent_Project_Manager import (
    ProjectManager,
    assign_tasks_to_agents,
    create_project_plan,
    evaluate_project_success,
    initiate_project,
    monitor_agents_progress,
    project_manager,
)


class TestProjectManager:
    """Tests for ProjectManager class."""

    def test_create_project_manager(self):
        """Test creating a ProjectManager instance."""
        pm = ProjectManager()
        assert pm.container is None
        assert pm._llm_provider is None

    def test_create_with_mock(self):
        """Test creating ProjectManager with mock provider."""
        pm = ProjectManager.create_with_mock()
        assert pm.llm_provider is not None
        assert pm.container is not None

    def test_initiate_project_with_mock(self):
        """Test initiating a project with mock provider."""
        pm = ProjectManager.create_with_mock()
        result = pm.initiate_project()

        assert isinstance(result, str)
        assert len(result) > 0

    def test_initiate_project_with_description(self):
        """Test initiating project with custom description."""
        pm = ProjectManager.create_with_mock()
        result = pm.initiate_project("A web application for e-commerce")

        assert isinstance(result, str)

    def test_create_project_plan(self):
        """Test creating a project plan."""
        pm = ProjectManager.create_with_mock()
        result = pm.create_project_plan()

        assert isinstance(result, dict)
        assert result.get("status") == "success"
        assert "plan" in result

    def test_assign_tasks_to_agents(self):
        """Test assigning tasks to agents."""
        pm = ProjectManager.create_with_mock()
        tasks = {
            "Agent_1": {"task": "Documentation", "status": "Pending"},
            "Agent_2": {"task": "Code Review", "status": "Pending"},
        }

        result = pm.assign_tasks_to_agents(tasks)

        assert result.get("status") == "success"
        assert result.get("total_assigned") == 2
        assert len(result.get("assignments", [])) == 2

    def test_assign_tasks_empty(self):
        """Test assigning empty tasks."""
        pm = ProjectManager.create_with_mock()
        result = pm.assign_tasks_to_agents({})

        assert result.get("status") == "success"
        assert result.get("total_assigned") == 0

    def test_monitor_agents_progress(self):
        """Test monitoring agent progress."""
        pm = ProjectManager.create_with_mock()
        tasks = {
            "Agent_1": {"task": "Documentation", "status": "In Progress"},
            "Agent_2": {"task": "Code Review", "status": "Complete"},
        }

        result = pm.monitor_agents_progress(tasks)

        assert result.get("status") == "success"
        assert "progress" in result
        assert len(result["progress"]) == 2

    def test_evaluate_project_success(self):
        """Test evaluating project success."""
        pm = ProjectManager.create_with_mock()
        result = pm.evaluate_project_success()

        assert result.get("status") == "success"
        assert "evaluation" in result
        assert "score" in result

    def test_run_project_workflow(self):
        """Test running complete project workflow."""
        pm = ProjectManager.create_with_mock()
        tasks = {
            "Agent_1": {"task": "Documentation", "status": "Pending"},
        }

        result = pm.run_project_workflow(tasks)

        assert result.get("workflow_status") == "complete"
        assert "initiation" in result
        assert "plan" in result
        assert "assignments" in result
        assert "progress" in result
        assert "evaluation" in result


class TestProjectManagerWithContainer:
    """Tests for ProjectManager with dependency injection."""

    def test_llm_provider_from_container(self):
        """Test LLM provider resolved from container."""
        try:
            from core import Container, MockProvider

            container = Container()
            provider = MockProvider(responses=["Custom response"])
            container.register_singleton("llm_provider", provider)

            pm = ProjectManager(container=container)
            resolved_provider = pm.llm_provider

            assert resolved_provider is provider
        except ImportError:
            pytest.skip("Core module not available")

    def test_explicit_provider_preferred(self):
        """Test explicit provider is preferred over container."""
        try:
            from core import Container, MockProvider

            container = Container()
            container_provider = MockProvider(responses=["Container response"])
            container.register_singleton("llm_provider", container_provider)

            explicit_provider = MockProvider(responses=["Explicit response"])

            pm = ProjectManager(
                container=container, llm_provider=explicit_provider
            )

            assert pm.llm_provider is explicit_provider
        except ImportError:
            pytest.skip("Core module not available")


class TestLegacyCompatibility:
    """Tests for legacy function compatibility."""

    def test_legacy_initiate_project(self):
        """Test legacy initiate_project function."""
        result = initiate_project()
        assert isinstance(result, str)

    def test_legacy_create_project_plan(self):
        """Test legacy create_project_plan function."""
        result = create_project_plan()
        assert result is True

    def test_legacy_assign_tasks_to_agents(self):
        """Test legacy assign_tasks_to_agents function."""
        tasks = {"Agent_1": {"task": "Test", "status": "Pending"}}
        result = assign_tasks_to_agents(tasks)
        assert result is True

    def test_legacy_monitor_agents_progress(self):
        """Test legacy monitor_agents_progress function."""
        tasks = {"Agent_1": {"task": "Test", "status": "In Progress"}}
        result = monitor_agents_progress(tasks)
        assert result is True

    def test_legacy_evaluate_project_success(self):
        """Test legacy evaluate_project_success function."""
        result = evaluate_project_success()
        assert result is True

    def test_legacy_project_manager(self):
        """Test legacy project_manager function."""
        tasks = {
            "Agent_1": {"task": "Documentation", "status": "Pending"},
            "Agent_2": {"task": "Review", "status": "Pending"},
        }
        result = project_manager(tasks)
        assert result is True


class TestTaskAssignment:
    """Tests for task assignment functionality."""

    def test_task_assignment_structure(self):
        """Test structure of task assignments."""
        pm = ProjectManager.create_with_mock()
        tasks = {
            "Agent_1": {"task": "Documentation", "status": "Pending"},
        }

        result = pm.assign_tasks_to_agents(tasks)
        assignment = result["assignments"][0]

        assert "agent" in assignment
        assert "task" in assignment
        assert "status" in assignment
        assert assignment["status"] == "Assigned"

    def test_task_assignment_preserves_task_name(self):
        """Test task assignment preserves task names."""
        pm = ProjectManager.create_with_mock()
        tasks = {
            "TestAgent": {"task": "Specific Task", "status": "Pending"},
        }

        result = pm.assign_tasks_to_agents(tasks)
        assignment = result["assignments"][0]

        assert assignment["agent"] == "TestAgent"
        assert assignment["task"] == "Specific Task"


class TestProgressMonitoring:
    """Tests for progress monitoring functionality."""

    def test_progress_report_structure(self):
        """Test structure of progress reports."""
        pm = ProjectManager.create_with_mock()
        tasks = {
            "Agent_1": {"task": "Documentation", "status": "Complete"},
        }

        result = pm.monitor_agents_progress(tasks)
        progress = result["progress"][0]

        assert "agent" in progress
        assert "task" in progress
        assert "status" in progress

    def test_progress_preserves_status(self):
        """Test progress monitoring preserves status."""
        pm = ProjectManager.create_with_mock()
        tasks = {
            "Agent_1": {"task": "Documentation", "status": "In Progress"},
        }

        result = pm.monitor_agents_progress(tasks)
        progress = result["progress"][0]

        assert progress["status"] == "In Progress"

    def test_progress_summary(self):
        """Test progress summary generation."""
        pm = ProjectManager.create_with_mock()
        tasks = {
            "Agent_1": {"task": "Task 1", "status": "Complete"},
            "Agent_2": {"task": "Task 2", "status": "In Progress"},
            "Agent_3": {"task": "Task 3", "status": "Pending"},
        }

        result = pm.monitor_agents_progress(tasks)

        assert "summary" in result
        assert "3" in result["summary"]  # Should mention 3 agents


class TestEvaluation:
    """Tests for project evaluation functionality."""

    def test_evaluation_includes_score(self):
        """Test evaluation includes a score."""
        pm = ProjectManager.create_with_mock()
        result = pm.evaluate_project_success()

        assert "score" in result
        assert isinstance(result["score"], (int, float))
        assert 0 <= result["score"] <= 1

    def test_evaluation_includes_description(self):
        """Test evaluation includes description."""
        pm = ProjectManager.create_with_mock()
        result = pm.evaluate_project_success()

        assert "evaluation" in result
        assert isinstance(result["evaluation"], str)


class TestWorkflowIntegration:
    """Integration tests for the complete workflow."""

    def test_workflow_returns_all_results(self):
        """Test workflow returns results from all steps."""
        pm = ProjectManager.create_with_mock()
        tasks = {"Agent_1": {"task": "Test", "status": "Pending"}}

        result = pm.run_project_workflow(tasks)

        expected_keys = [
            "initiation",
            "plan",
            "assignments",
            "progress",
            "evaluation",
            "workflow_status",
        ]
        for key in expected_keys:
            assert key in result

    def test_workflow_with_multiple_agents(self):
        """Test workflow with multiple agents."""
        pm = ProjectManager.create_with_mock()
        tasks = {
            "Agent_1": {"task": "Documentation", "status": "Pending"},
            "Agent_2": {"task": "Code Review", "status": "Pending"},
            "Agent_3": {"task": "Testing", "status": "Pending"},
        }

        result = pm.run_project_workflow(tasks)

        assert result["workflow_status"] == "complete"
        assert result["assignments"]["total_assigned"] == 3


class TestCreateWithProvider:
    """Tests for create_with_provider factory method."""

    def test_create_with_provider_requires_core(self):
        """Test create_with_provider requires core module."""
        try:
            from core import MockProvider

            # If core is available, this should work with mock
            pm = ProjectManager.create_with_mock()
            assert pm.llm_provider is not None
        except ImportError:
            # If core is not available, should handle gracefully
            pm = ProjectManager()
            assert pm._llm_provider is None


class TestErrorHandling:
    """Tests for error handling in ProjectManager."""

    def test_project_manager_handles_missing_task_key(self):
        """Test handling of missing task key."""
        pm = ProjectManager.create_with_mock()
        tasks = {
            "Agent_1": {},  # Missing 'task' key
        }

        result = pm.assign_tasks_to_agents(tasks)
        assert result["assignments"][0]["task"] == "Unknown"

    def test_progress_handles_missing_status(self):
        """Test handling of missing status in progress monitoring."""
        pm = ProjectManager.create_with_mock()
        tasks = {
            "Agent_1": {"task": "Documentation"},  # Missing 'status'
        }

        result = pm.monitor_agents_progress(tasks)
        assert result["progress"][0]["status"] == "Unknown"
