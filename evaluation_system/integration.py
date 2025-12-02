# integration.py - Integration with Existing Agents
# Provides utilities to integrate the evaluation system with existing agent modules

import sys
from pathlib import Path
from typing import Dict, List, Optional

# Add parent directory to path to import agents
sys.path.insert(0, str(Path(__file__).parent.parent))

from evaluation_system import AgentEvaluator, TeamEvaluator


class AgentIntegration:
    """
    Integration layer between existing agents and evaluation system
    Maps agent tasks and outputs to evaluation metrics
    """
    
    # Mapping of agent module names to evaluation roles
    AGENT_ROLE_MAPPING = {
        'A1_Project_Manager': 'Project_Manager',
        'A2_Software_Architect': 'Software_Architect',
        'A3_Frontend_Developer': 'Frontend_Developer',
        'A4_Backend_Developer': 'Backend_Developer',
        'A5_Data_Engineer': 'Data_Engineer',
        'A6_Data_Scientist': 'Data_Scientist',
        'A7_Machine_Learning_Engineer': 'ML_Engineer',
        'A8_DevOps_Engineer': 'DevOps_Engineer',
        'A9_Quality_Assurance_Engineer': 'QA_Engineer',
        'A10_Security_Engineer': 'Security_Engineer'
    }
    
    def __init__(self):
        """Initialize agent integration"""
        self.evaluators: Dict[str, AgentEvaluator] = {}
        self.team_evaluator = TeamEvaluator(team_name="KHM Smart Build Coding Team")
    
    def create_agent_evaluator(self, agent_module_name: str, agent_id: str) -> AgentEvaluator:
        """
        Create an evaluator for an existing agent
        
        Args:
            agent_module_name: Name of the agent module (e.g., 'A1_Project_Manager')
            agent_id: Unique identifier for the agent instance
        
        Returns:
            AgentEvaluator instance
        """
        role = self.AGENT_ROLE_MAPPING.get(agent_module_name, agent_module_name)
        evaluator = AgentEvaluator(agent_id=agent_id, agent_role=role)
        self.evaluators[agent_id] = evaluator
        self.team_evaluator.add_agent(evaluator)
        return evaluator
    
    def record_task_assignment(self, agent_id: str, task_count: int = 1) -> None:
        """
        Record task assignment to an agent
        
        Args:
            agent_id: Agent identifier
            task_count: Number of tasks assigned
        """
        if agent_id in self.evaluators:
            evaluator = self.evaluators[agent_id]
            current = evaluator.performance_metrics.tasks_assigned
            evaluator.update_performance_metrics(tasks_assigned=current + task_count)
    
    def record_task_completion(
        self, 
        agent_id: str, 
        success: bool = True, 
        completion_time: Optional[float] = None
    ) -> None:
        """
        Record task completion for an agent
        
        Args:
            agent_id: Agent identifier
            success: Whether task completed successfully
            completion_time: Time taken to complete task (seconds)
        """
        if agent_id in self.evaluators:
            evaluator = self.evaluators[agent_id]
            
            if success:
                current = evaluator.performance_metrics.tasks_completed
                evaluator.update_performance_metrics(tasks_completed=current + 1)
            else:
                current = evaluator.performance_metrics.tasks_failed
                evaluator.update_performance_metrics(tasks_failed=current + 1)
            
            if completion_time is not None:
                # Update average completion time
                current_avg = evaluator.performance_metrics.average_task_completion_time
                completed = evaluator.performance_metrics.tasks_completed
                
                if completed > 0:
                    new_avg = ((current_avg * (completed - 1)) + completion_time) / completed
                    evaluator.update_performance_metrics(average_task_completion_time=new_avg)
            
            # Recalculate success rate
            evaluator.performance_metrics.calculate_success_rate()
    
    def record_code_activity(
        self,
        agent_id: str,
        lines_of_code: int = 0,
        commits: int = 0,
        pull_requests: int = 0,
        prs_merged: int = 0
    ) -> None:
        """
        Record code-related activity for an agent
        
        Args:
            agent_id: Agent identifier
            lines_of_code: Lines of code written
            commits: Number of commits
            pull_requests: Number of PRs created
            prs_merged: Number of PRs merged
        """
        if agent_id in self.evaluators:
            evaluator = self.evaluators[agent_id]
            current_metrics = evaluator.productivity_metrics
            
            evaluator.update_productivity_metrics(
                lines_of_code_written=current_metrics.lines_of_code_written + lines_of_code,
                commits_made=current_metrics.commits_made + commits,
                pull_requests_created=current_metrics.pull_requests_created + pull_requests,
                pull_requests_merged=current_metrics.pull_requests_merged + prs_merged
            )
    
    def record_quality_metrics(
        self,
        agent_id: str,
        bugs_found: int = 0,
        critical_bugs: int = 0,
        tests_passed: int = 0,
        tests_failed: int = 0,
        code_review_score: Optional[float] = None,
        test_coverage: Optional[float] = None
    ) -> None:
        """
        Record quality metrics for an agent
        
        Args:
            agent_id: Agent identifier
            bugs_found: Number of bugs found
            critical_bugs: Number of critical bugs
            tests_passed: Number of tests passed
            tests_failed: Number of tests failed
            code_review_score: Code review score (0-100)
            test_coverage: Test coverage percentage
        """
        if agent_id in self.evaluators:
            evaluator = self.evaluators[agent_id]
            current_metrics = evaluator.quality_metrics
            
            updates = {
                'bug_count': current_metrics.bug_count + bugs_found,
                'critical_bugs': current_metrics.critical_bugs + critical_bugs,
                'tests_passed': current_metrics.tests_passed + tests_passed,
                'tests_failed': current_metrics.tests_failed + tests_failed
            }
            
            if code_review_score is not None:
                updates['code_review_score'] = code_review_score
            
            if test_coverage is not None:
                updates['test_coverage'] = test_coverage
            
            evaluator.update_quality_metrics(**updates)
    
    def record_collaboration(
        self,
        agent_id: str,
        code_reviews: int = 0,
        meetings: int = 0,
        documentation: int = 0,
        mentoring: int = 0,
        pair_programming: int = 0
    ) -> None:
        """
        Record collaboration activities for an agent
        
        Args:
            agent_id: Agent identifier
            code_reviews: Number of code reviews participated in
            meetings: Number of meetings attended
            documentation: Documentation contributions
            mentoring: Mentoring sessions
            pair_programming: Pair programming sessions
        """
        if agent_id in self.evaluators:
            evaluator = self.evaluators[agent_id]
            current_metrics = evaluator.collaboration_metrics
            
            evaluator.update_collaboration_metrics(
                code_reviews_participated=current_metrics.code_reviews_participated + code_reviews,
                meetings_attended=current_metrics.meetings_attended + meetings,
                documentation_contributions=current_metrics.documentation_contributions + documentation,
                mentoring_sessions=current_metrics.mentoring_sessions + mentoring,
                pair_programming_sessions=current_metrics.pair_programming_sessions + pair_programming
            )
    
    def get_agent_evaluation(self, agent_id: str) -> Optional[Dict]:
        """
        Get evaluation report for an agent
        
        Args:
            agent_id: Agent identifier
        
        Returns:
            Evaluation report dictionary or None if agent not found
        """
        if agent_id in self.evaluators:
            return self.evaluators[agent_id].generate_evaluation_report()
        return None
    
    def get_team_evaluation(self) -> Dict:
        """
        Get team evaluation report
        
        Returns:
            Team evaluation report dictionary
        """
        return self.team_evaluator.generate_team_report()
    
    def get_all_agents_summary(self) -> List[Dict]:
        """
        Get summary of all agents
        
        Returns:
            List of agent summaries
        """
        summaries = []
        for agent_id, evaluator in self.evaluators.items():
            summaries.append({
                'agent_id': agent_id,
                'agent_role': evaluator.agent_role,
                'overall_score': evaluator.calculate_overall_score(),
                'rating': evaluator.get_performance_rating()
            })
        return summaries


def example_integration_usage():
    """Example demonstrating integration with existing agents"""
    print("="*60)
    print("EXAMPLE: Integration with Existing Agents")
    print("="*60)
    
    # Initialize integration
    integration = AgentIntegration()
    
    # Create evaluators for existing agents
    pm_eval = integration.create_agent_evaluator('A1_Project_Manager', 'PM001')
    frontend_eval = integration.create_agent_evaluator('A3_Frontend_Developer', 'FE001')
    backend_eval = integration.create_agent_evaluator('A4_Backend_Developer', 'BE001')
    qa_eval = integration.create_agent_evaluator('A9_Quality_Assurance_Engineer', 'QA001')
    
    # Simulate project activity
    
    # Project Manager activities
    integration.record_task_assignment('PM001', task_count=10)
    integration.record_task_completion('PM001', success=True, completion_time=7200)
    integration.record_task_completion('PM001', success=True, completion_time=5400)
    integration.record_collaboration('PM001', meetings=15, documentation=20)
    
    # Frontend Developer activities
    integration.record_task_assignment('FE001', task_count=25)
    for _ in range(22):
        integration.record_task_completion('FE001', success=True, completion_time=3600)
    integration.record_task_completion('FE001', success=False)
    integration.record_code_activity('FE001', lines_of_code=5000, commits=40, 
                                    pull_requests=15, prs_merged=13)
    integration.record_quality_metrics('FE001', bugs_found=8, tests_passed=100, 
                                      tests_failed=5, code_review_score=80.0)
    integration.record_collaboration('FE001', code_reviews=12, pair_programming=6)
    
    # Backend Developer activities
    integration.record_task_assignment('BE001', task_count=30)
    for _ in range(27):
        integration.record_task_completion('BE001', success=True, completion_time=4200)
    integration.record_code_activity('BE001', lines_of_code=7000, commits=50,
                                    pull_requests=20, prs_merged=19)
    integration.record_quality_metrics('BE001', bugs_found=4, critical_bugs=1,
                                      tests_passed=150, tests_failed=8,
                                      code_review_score=88.0, test_coverage=82.0)
    integration.record_collaboration('BE001', code_reviews=18, mentoring=4)
    
    # QA Engineer activities
    integration.record_task_assignment('QA001', task_count=35)
    for _ in range(33):
        integration.record_task_completion('QA001', success=True, completion_time=3000)
    integration.record_quality_metrics('QA001', bugs_found=50, critical_bugs=5,
                                      tests_passed=300, tests_failed=15,
                                      code_review_score=85.0, test_coverage=90.0)
    integration.record_collaboration('QA001', code_reviews=25, documentation=15)
    
    # Get individual agent evaluations
    print("\nIndividual Agent Evaluations:")
    print("-" * 60)
    for agent_id in ['PM001', 'FE001', 'BE001', 'QA001']:
        report = integration.get_agent_evaluation(agent_id)
        if report:
            print(f"\n{report['agent_role']} ({agent_id}):")
            print(f"  Overall Score: {report['overall_score']}/100")
            print(f"  Rating: {report['performance_rating']}")
            print(f"  Success Rate: {report['metrics']['performance']['success_rate']}%")
    
    # Get team evaluation
    print("\n" + "="*60)
    print("Team Evaluation:")
    print("-" * 60)
    team_report = integration.get_team_evaluation()
    print(f"Team Performance Score: {team_report['overall_metrics']['team_performance_score']}/100")
    print(f"Team Success Rate: {team_report['overall_metrics']['team_success_rate']}%")
    print(f"Team Velocity: {team_report['overall_metrics']['team_velocity']} story points")
    
    print("\nTop Performers:")
    for i, performer in enumerate(team_report['top_performers'], 1):
        print(f"{i}. {performer['agent_role']} - {performer['overall_score']}/100")
    
    print("\n" + "="*60)


if __name__ == "__main__":
    example_integration_usage()
