# evaluation_report.py - Evaluation Report Generator and Exporter
# Generates detailed evaluation reports in various formats

from typing import Dict, List, Optional
from datetime import datetime
import json
from pathlib import Path


class EvaluationReport:
    """
    Generates and exports evaluation reports in multiple formats
    Supports JSON, Markdown, and CSV exports
    """
    
    def __init__(self, output_dir: str = "evaluation_reports"):
        """
        Initialize report generator
        
        Args:
            output_dir: Directory to save generated reports
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_agent_report_json(
        self, 
        agent_report: Dict, 
        filename: Optional[str] = None
    ) -> str:
        """
        Generate agent evaluation report in JSON format
        
        Args:
            agent_report: Agent evaluation report dictionary
            filename: Optional custom filename
        
        Returns:
            Path to the generated report file
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            agent_id = agent_report.get('agent_id', 'unknown')
            filename = f"agent_{agent_id}_{timestamp}.json"
        
        filepath = self.output_dir / filename
        
        with open(filepath, 'w') as f:
            json.dump(agent_report, f, indent=2)
        
        return str(filepath)
    
    def generate_team_report_json(
        self, 
        team_report: Dict, 
        filename: Optional[str] = None
    ) -> str:
        """
        Generate team evaluation report in JSON format
        
        Args:
            team_report: Team evaluation report dictionary
            filename: Optional custom filename
        
        Returns:
            Path to the generated report file
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"team_report_{timestamp}.json"
        
        filepath = self.output_dir / filename
        
        with open(filepath, 'w') as f:
            json.dump(team_report, f, indent=2)
        
        return str(filepath)
    
    def generate_agent_report_markdown(
        self, 
        agent_report: Dict, 
        filename: Optional[str] = None
    ) -> str:
        """
        Generate agent evaluation report in Markdown format
        
        Args:
            agent_report: Agent evaluation report dictionary
            filename: Optional custom filename
        
        Returns:
            Path to the generated report file
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            agent_id = agent_report.get('agent_id', 'unknown')
            filename = f"agent_{agent_id}_{timestamp}.md"
        
        filepath = self.output_dir / filename
        
        markdown_content = self._format_agent_markdown(agent_report)
        
        with open(filepath, 'w') as f:
            f.write(markdown_content)
        
        return str(filepath)
    
    def _format_agent_markdown(self, report: Dict) -> str:
        """Format agent report as Markdown"""
        md = f"""# Agent Evaluation Report

## Agent Information
- **Agent ID:** {report['agent_id']}
- **Agent Role:** {report['agent_role']}
- **Evaluation Date:** {report['evaluation_date']}
- **Overall Score:** {report['overall_score']}/100
- **Performance Rating:** {report['performance_rating']}

## Performance Metrics
"""
        
        perf = report['metrics']['performance']
        md += f"""
- **Tasks Assigned:** {perf['tasks_assigned']}
- **Tasks Completed:** {perf['tasks_completed']}
- **Tasks In Progress:** {perf['tasks_in_progress']}
- **Tasks Failed:** {perf['tasks_failed']}
- **Success Rate:** {perf['success_rate']}%
- **On-Time Delivery Rate:** {perf['on_time_delivery_rate']}%
- **Average Task Completion Time:** {perf['average_task_completion_time']} seconds

## Quality Metrics
"""
        
        qual = report['metrics']['quality']
        md += f"""
- **Code Review Score:** {qual['code_review_score']}/100
- **Bug Count:** {qual['bug_count']} (Critical: {qual['critical_bugs']}, Major: {qual['major_bugs']}, Minor: {qual['minor_bugs']})
- **Test Coverage:** {qual['test_coverage']}%
- **Tests Passed:** {qual['tests_passed']}
- **Tests Failed:** {qual['tests_failed']}
- **Code Reviews Given:** {qual['code_reviews_given']}
- **Code Reviews Received:** {qual['code_reviews_received']}
- **Security Vulnerabilities:** {qual['security_vulnerabilities']}

## Productivity Metrics
"""
        
        prod = report['metrics']['productivity']
        md += f"""
- **Lines of Code Written:** {prod['lines_of_code_written']}
- **Commits Made:** {prod['commits_made']}
- **Pull Requests Created:** {prod['pull_requests_created']}
- **Pull Requests Merged:** {prod['pull_requests_merged']}
- **Story Points Completed:** {prod['story_points_completed']}
- **Features Delivered:** {prod['features_delivered']}
- **Documentation Coverage:** {prod['documentation_coverage']}%

## Collaboration Metrics
"""
        
        collab = report['metrics']['collaboration']
        md += f"""
- **Messages Sent:** {collab['messages_sent']}
- **Code Reviews Participated:** {collab['code_reviews_participated']}
- **Meetings Attended:** {collab['meetings_attended']}
- **Documentation Contributions:** {collab['documentation_contributions']}
- **Mentoring Sessions:** {collab['mentoring_sessions']}
- **Pair Programming Sessions:** {collab['pair_programming_sessions']}
- **Responsiveness Score:** {collab['responsiveness_score']}/10
- **Teamwork Score:** {collab['teamwork_score']}/10

## Threshold Checks
"""
        
        for check, passed in report['threshold_checks'].items():
            status = "✓ Passed" if passed else "✗ Failed"
            md += f"- **{check.replace('_', ' ').title()}:** {status}\n"
        
        if report['strengths']:
            md += "\n## Strengths\n"
            for strength in report['strengths']:
                md += f"- {strength}\n"
        
        if report['areas_for_improvement']:
            md += "\n## Areas for Improvement\n"
            for area in report['areas_for_improvement']:
                md += f"- {area}\n"
        
        return md
    
    def generate_team_report_markdown(
        self, 
        team_report: Dict, 
        filename: Optional[str] = None
    ) -> str:
        """
        Generate team evaluation report in Markdown format
        
        Args:
            team_report: Team evaluation report dictionary
            filename: Optional custom filename
        
        Returns:
            Path to the generated report file
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"team_report_{timestamp}.md"
        
        filepath = self.output_dir / filename
        
        markdown_content = self._format_team_markdown(team_report)
        
        with open(filepath, 'w') as f:
            f.write(markdown_content)
        
        return str(filepath)
    
    def _format_team_markdown(self, report: Dict) -> str:
        """Format team report as Markdown"""
        md = f"""# Team Evaluation Report

## Team Information
- **Team Name:** {report['team_name']}
- **Evaluation Date:** {report['evaluation_date']}
- **Team Size:** {report['team_size']} members

## Overall Performance
- **Team Performance Score:** {report['overall_metrics']['team_performance_score']}/100
- **Team Success Rate:** {report['overall_metrics']['team_success_rate']}%
- **Team Quality Score:** {report['overall_metrics']['team_quality_score']}/100
- **Team Velocity:** {report['overall_metrics']['team_velocity']} story points

**Team Health Status:** {report['team_health_status']}

## Productivity Metrics
- **Total Lines of Code:** {report['productivity_metrics']['total_lines_of_code']}
- **Total Commits:** {report['productivity_metrics']['total_commits']}
- **Total Pull Requests:** {report['productivity_metrics']['total_pull_requests']}
- **PRs Merged:** {report['productivity_metrics']['total_prs_merged']}
- **PR Merge Rate:** {report['productivity_metrics']['pr_merge_rate']}%
- **Features Delivered:** {report['productivity_metrics']['total_features_delivered']}

## Collaboration Metrics
- **Total Code Reviews:** {report['collaboration_metrics']['total_code_reviews']}
- **Total Documentation:** {report['collaboration_metrics']['total_documentation']}
- **Mentoring Sessions:** {report['collaboration_metrics']['total_mentoring_sessions']}
- **Pair Programming:** {report['collaboration_metrics']['total_pair_programming']}
- **Blockers Resolved:** {report['collaboration_metrics']['total_blockers_resolved']}
- **Collaboration Health:** {report['collaboration_metrics']['collaboration_health']}

## Team Balance
"""
        
        balance = report['team_balance']
        md += f"""
- **Average Team Score:** {balance['average_team_score']}/100
- **Score Variance:** {balance['score_variance']}
- **Team Balance Status:** {"Balanced" if balance['is_balanced'] else "Unbalanced"}

### Role Distribution
"""
        for role, count in balance['role_distribution'].items():
            md += f"- **{role}:** {count}\n"
        
        if report['top_performers']:
            md += "\n## Top Performers\n"
            for i, performer in enumerate(report['top_performers'], 1):
                md += f"{i}. **{performer['agent_role']}** - Score: {performer['overall_score']}/100 ({performer['rating']})\n"
        
        if report['underperformers']:
            md += "\n## Underperformers\n"
            for performer in report['underperformers']:
                md += f"- **{performer['agent_role']}** - Score: {performer['overall_score']}/100\n"
                if performer.get('improvement_areas'):
                    for area in performer['improvement_areas']:
                        md += f"  - {area}\n"
        
        if report['recommendations']:
            md += "\n## Recommendations\n"
            for i, rec in enumerate(report['recommendations'], 1):
                md += f"{i}. {rec}\n"
        
        return md
    
    def generate_metrics_csv(
        self, 
        agents_data: List[Dict], 
        filename: Optional[str] = None
    ) -> str:
        """
        Generate CSV file with agent metrics for analysis
        
        Args:
            agents_data: List of agent evaluation reports
            filename: Optional custom filename
        
        Returns:
            Path to the generated CSV file
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"agent_metrics_{timestamp}.csv"
        
        filepath = self.output_dir / filename
        
        # CSV header
        csv_content = "Agent ID,Agent Role,Overall Score,Performance Rating,Tasks Assigned,Tasks Completed,Success Rate,Code Quality,Test Coverage,Bug Count,LOC Written,PRs Merged,Collaboration Score\n"
        
        # CSV rows
        for agent in agents_data:
            perf = agent['metrics']['performance']
            qual = agent['metrics']['quality']
            prod = agent['metrics']['productivity']
            collab = agent['metrics']['collaboration']
            
            csv_content += f"{agent['agent_id']},{agent['agent_role']},{agent['overall_score']},{agent['performance_rating']},"
            csv_content += f"{perf['tasks_assigned']},{perf['tasks_completed']},{perf['success_rate']},"
            csv_content += f"{qual['code_review_score']},{qual['test_coverage']},{qual['bug_count']},"
            csv_content += f"{prod['lines_of_code_written']},{prod['pull_requests_merged']},"
            
            # Calculate collaboration score
            collab_score = (collab['responsiveness_score'] + collab['teamwork_score'] + 
                          collab['communication_clarity_score']) / 3
            csv_content += f"{collab_score:.2f}\n"
        
        with open(filepath, 'w') as f:
            f.write(csv_content)
        
        return str(filepath)
    
    def generate_comparison_report(
        self, 
        current_report: Dict, 
        previous_report: Dict, 
        filename: Optional[str] = None
    ) -> str:
        """
        Generate comparison report between two evaluation periods
        
        Args:
            current_report: Current evaluation report
            previous_report: Previous evaluation report
            filename: Optional custom filename
        
        Returns:
            Path to the generated report file
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"comparison_report_{timestamp}.md"
        
        filepath = self.output_dir / filename
        
        md = f"""# Evaluation Comparison Report

## Comparison Period
- **Previous Evaluation:** {previous_report['evaluation_date']}
- **Current Evaluation:** {current_report['evaluation_date']}

## Performance Changes
"""
        
        curr_perf = current_report['overall_metrics']['team_performance_score']
        prev_perf = previous_report['overall_metrics']['team_performance_score']
        change = curr_perf - prev_perf
        
        md += f"- **Team Performance Score:** {prev_perf} → {curr_perf} ({change:+.2f})\n"
        
        curr_success = current_report['overall_metrics']['team_success_rate']
        prev_success = previous_report['overall_metrics']['team_success_rate']
        change = curr_success - prev_success
        
        md += f"- **Team Success Rate:** {prev_success}% → {curr_success}% ({change:+.2f}%)\n"
        
        curr_quality = current_report['overall_metrics']['team_quality_score']
        prev_quality = previous_report['overall_metrics']['team_quality_score']
        change = curr_quality - prev_quality
        
        md += f"- **Team Quality Score:** {prev_quality} → {curr_quality} ({change:+.2f})\n"
        
        curr_velocity = current_report['overall_metrics']['team_velocity']
        prev_velocity = previous_report['overall_metrics']['team_velocity']
        change = curr_velocity - prev_velocity
        
        md += f"- **Team Velocity:** {prev_velocity} → {curr_velocity} ({change:+.0f} story points)\n"
        
        md += "\n## Overall Trend\n"
        if curr_perf > prev_perf:
            md += "✓ **Team performance is improving**\n"
        elif curr_perf < prev_perf:
            md += "✗ **Team performance is declining**\n"
        else:
            md += "→ **Team performance is stable**\n"
        
        with open(filepath, 'w') as f:
            f.write(md)
        
        return str(filepath)
