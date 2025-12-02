#!/usr/bin/env python3
# example_evaluation.py - Example Usage of the Evaluation System
# Demonstrates how to use the evaluation system to assess agent and team performance

from evaluation_system import (
    AgentEvaluator,
    TeamEvaluator,
    EvaluationReport
)


def example_single_agent_evaluation():
    """Example: Evaluate a single agent"""
    print("="*60)
    print("EXAMPLE: Single Agent Evaluation")
    print("="*60)
    
    # Create an agent evaluator for a Backend Developer
    agent = AgentEvaluator(agent_id="A001", agent_role="Backend_Developer")
    
    # Update performance metrics
    agent.update_performance_metrics(
        tasks_assigned=20,
        tasks_completed=18,
        tasks_in_progress=1,
        tasks_failed=1,
        average_task_completion_time=3600,  # 1 hour in seconds
        on_time_delivery_rate=85.0
    )
    
    # Update quality metrics
    agent.update_quality_metrics(
        code_review_score=85.0,
        bug_count=5,
        critical_bugs=0,
        major_bugs=2,
        minor_bugs=3,
        test_coverage=78.0,
        tests_passed=95,
        tests_failed=5,
        code_reviews_given=12,
        code_reviews_received=8,
        review_feedback_score=8.5
    )
    
    # Update productivity metrics
    agent.update_productivity_metrics(
        lines_of_code_written=5000,
        commits_made=45,
        pull_requests_created=15,
        pull_requests_merged=14,
        story_points_completed=25,
        features_delivered=8,
        documentation_coverage=65.0
    )
    
    # Update collaboration metrics
    agent.update_collaboration_metrics(
        messages_sent=150,
        code_reviews_participated=12,
        meetings_attended=8,
        documentation_contributions=10,
        mentoring_sessions=3,
        pair_programming_sessions=5,
        blockers_resolved_for_others=4,
        questions_answered=20,
        responsiveness_score=8.5,
        teamwork_score=9.0,
        communication_clarity_score=8.0
    )
    
    # Generate evaluation report
    report = agent.generate_evaluation_report()
    
    print(f"\nAgent: {report['agent_id']} ({report['agent_role']})")
    print(f"Overall Score: {report['overall_score']}/100")
    print(f"Performance Rating: {report['performance_rating']}")
    print(f"\nStrengths:")
    for strength in report['strengths']:
        print(f"  - {strength}")
    print(f"\nAreas for Improvement:")
    for area in report['areas_for_improvement']:
        print(f"  - {area}")
    
    return agent


def example_team_evaluation():
    """Example: Evaluate the entire team"""
    print("\n" + "="*60)
    print("EXAMPLE: Team Evaluation")
    print("="*60)
    
    # Create team evaluator
    team = TeamEvaluator(team_name="KHM Smart Build Coding Team")
    
    # Create and add multiple agents
    
    # Project Manager
    pm = AgentEvaluator(agent_id="A001", agent_role="Project_Manager")
    pm.update_performance_metrics(
        tasks_assigned=15, tasks_completed=14, tasks_failed=0,
        on_time_delivery_rate=90.0
    )
    pm.update_quality_metrics(code_review_score=88.0, test_coverage=0)
    pm.update_productivity_metrics(
        story_points_completed=20, features_delivered=5,
        documentation_coverage=85.0
    )
    pm.update_collaboration_metrics(
        code_reviews_participated=20, meetings_attended=15,
        responsiveness_score=9.0, teamwork_score=9.5,
        communication_clarity_score=9.0
    )
    team.add_agent(pm)
    
    # Frontend Developer
    frontend = AgentEvaluator(agent_id="A002", agent_role="Frontend_Developer")
    frontend.update_performance_metrics(
        tasks_assigned=25, tasks_completed=22, tasks_failed=2,
        on_time_delivery_rate=82.0
    )
    frontend.update_quality_metrics(
        code_review_score=80.0, bug_count=8, test_coverage=72.0,
        tests_passed=110, tests_failed=8
    )
    frontend.update_productivity_metrics(
        lines_of_code_written=6500, commits_made=55,
        pull_requests_created=20, pull_requests_merged=18,
        story_points_completed=30, features_delivered=10
    )
    frontend.update_collaboration_metrics(
        code_reviews_participated=15, pair_programming_sessions=8,
        responsiveness_score=8.0, teamwork_score=8.5,
        communication_clarity_score=8.0
    )
    team.add_agent(frontend)
    
    # Backend Developer
    backend = AgentEvaluator(agent_id="A003", agent_role="Backend_Developer")
    backend.update_performance_metrics(
        tasks_assigned=28, tasks_completed=25, tasks_failed=1,
        on_time_delivery_rate=85.0
    )
    backend.update_quality_metrics(
        code_review_score=85.0, bug_count=5, test_coverage=80.0,
        tests_passed=140, tests_failed=6
    )
    backend.update_productivity_metrics(
        lines_of_code_written=7200, commits_made=60,
        pull_requests_created=22, pull_requests_merged=20,
        story_points_completed=35, features_delivered=12
    )
    backend.update_collaboration_metrics(
        code_reviews_participated=18, mentoring_sessions=5,
        responsiveness_score=8.5, teamwork_score=9.0,
        communication_clarity_score=8.5
    )
    team.add_agent(backend)
    
    # QA Engineer
    qa = AgentEvaluator(agent_id="A004", agent_role="QA_Engineer")
    qa.update_performance_metrics(
        tasks_assigned=30, tasks_completed=28, tasks_failed=1,
        on_time_delivery_rate=88.0
    )
    qa.update_quality_metrics(
        code_review_score=82.0, bug_count=3, test_coverage=90.0,
        tests_passed=200, tests_failed=10
    )
    qa.update_productivity_metrics(
        lines_of_code_written=3500, commits_made=40,
        pull_requests_created=18, pull_requests_merged=17,
        story_points_completed=28, features_delivered=8
    )
    qa.update_collaboration_metrics(
        code_reviews_participated=25, questions_answered=30,
        responsiveness_score=9.0, teamwork_score=8.5,
        communication_clarity_score=8.5
    )
    team.add_agent(qa)
    
    # DevOps Engineer
    devops = AgentEvaluator(agent_id="A005", agent_role="DevOps_Engineer")
    devops.update_performance_metrics(
        tasks_assigned=20, tasks_completed=19, tasks_failed=0,
        on_time_delivery_rate=92.0
    )
    devops.update_quality_metrics(
        code_review_score=88.0, bug_count=2, test_coverage=85.0,
        tests_passed=90, tests_failed=3
    )
    devops.update_productivity_metrics(
        lines_of_code_written=4000, commits_made=45,
        pull_requests_created=16, pull_requests_merged=15,
        story_points_completed=24, features_delivered=7
    )
    devops.update_collaboration_metrics(
        code_reviews_participated=12, blockers_resolved_for_others=8,
        responsiveness_score=9.5, teamwork_score=9.0,
        communication_clarity_score=8.5
    )
    team.add_agent(devops)
    
    # Generate team report
    team_report = team.generate_team_report()
    
    # Print summary
    print(team.export_team_metrics_summary())
    
    return team, team_report


def example_report_generation(agent, team, team_report):
    """Example: Generate various report formats"""
    print("\n" + "="*60)
    print("EXAMPLE: Report Generation")
    print("="*60)
    
    # Create report generator
    report_gen = EvaluationReport(output_dir="evaluation_reports")
    
    # Generate agent report
    agent_report = agent.generate_evaluation_report()
    
    # Generate JSON reports
    agent_json = report_gen.generate_agent_report_json(agent_report)
    print(f"\n✓ Agent JSON report saved to: {agent_json}")
    
    team_json = report_gen.generate_team_report_json(team_report)
    print(f"✓ Team JSON report saved to: {team_json}")
    
    # Generate Markdown reports
    agent_md = report_gen.generate_agent_report_markdown(agent_report)
    print(f"✓ Agent Markdown report saved to: {agent_md}")
    
    team_md = report_gen.generate_team_report_markdown(team_report)
    print(f"✓ Team Markdown report saved to: {team_md}")
    
    # Generate CSV metrics
    agents_data = [team.agents[agent_id].generate_evaluation_report() 
                   for agent_id in team.agents.keys()]
    csv_file = report_gen.generate_metrics_csv(agents_data)
    print(f"✓ Metrics CSV saved to: {csv_file}")
    
    print("\nAll reports generated successfully!")


def example_performance_tracking():
    """Example: Track performance over time"""
    print("\n" + "="*60)
    print("EXAMPLE: Performance Tracking Over Time")
    print("="*60)
    
    # Create an agent
    agent = AgentEvaluator(agent_id="A006", agent_role="Data_Scientist")
    
    # First evaluation period
    agent.update_performance_metrics(
        tasks_assigned=15, tasks_completed=12, tasks_failed=2
    )
    agent.update_quality_metrics(code_review_score=75.0, bug_count=10)
    agent.update_productivity_metrics(story_points_completed=18)
    agent.update_collaboration_metrics(
        responsiveness_score=7.0, teamwork_score=7.5,
        communication_clarity_score=7.0
    )
    
    first_report = agent.generate_evaluation_report()
    print(f"\nFirst Evaluation:")
    print(f"  Overall Score: {first_report['overall_score']}/100")
    print(f"  Rating: {first_report['performance_rating']}")
    
    # Second evaluation period (improved performance)
    agent.update_performance_metrics(
        tasks_assigned=20, tasks_completed=18, tasks_failed=1
    )
    agent.update_quality_metrics(code_review_score=85.0, bug_count=5)
    agent.update_productivity_metrics(story_points_completed=25)
    agent.update_collaboration_metrics(
        responsiveness_score=8.5, teamwork_score=8.5,
        communication_clarity_score=8.0
    )
    
    second_report = agent.generate_evaluation_report()
    print(f"\nSecond Evaluation:")
    print(f"  Overall Score: {second_report['overall_score']}/100")
    print(f"  Rating: {second_report['performance_rating']}")
    
    # Compare performance
    comparison = agent.compare_with_previous(lookback_periods=1)
    if comparison:
        print(f"\nPerformance Comparison:")
        print(f"  Score Change: {comparison['score_change']:+.2f}")
        print(f"  Rating Change: {comparison['rating_change']}")
        print(f"  Trend: {comparison['trend'].upper()}")


def main():
    """Run all examples"""
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + " "*15 + "EVALUATION SYSTEM EXAMPLES" + " "*17 + "║")
    print("╚" + "="*58 + "╝")
    
    # Example 1: Single agent evaluation
    agent = example_single_agent_evaluation()
    
    # Example 2: Team evaluation
    team, team_report = example_team_evaluation()
    
    # Example 3: Report generation
    example_report_generation(agent, team, team_report)
    
    # Example 4: Performance tracking
    example_performance_tracking()
    
    print("\n" + "="*60)
    print("All examples completed successfully!")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
