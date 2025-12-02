# team_evaluator.py - Team-level Performance Evaluator
# Evaluates overall team performance, collaboration, and project success

from typing import Dict, List, Optional
from datetime import datetime
from .agent_evaluator import AgentEvaluator
from .metrics import PerformanceMetrics


class TeamEvaluator:
    """
    Evaluates overall team performance and dynamics
    Aggregates individual agent metrics to assess team effectiveness
    """
    
    def __init__(self, team_name: str = "Coding Team"):
        """
        Initialize team evaluator
        
        Args:
            team_name: Name of the team being evaluated
        """
        self.team_name = team_name
        self.agents: Dict[str, AgentEvaluator] = {}
        self.team_metrics: Dict = {}
        self.evaluation_history: List[Dict] = []
    
    def add_agent(self, agent_evaluator: AgentEvaluator) -> None:
        """
        Add an agent to the team evaluation
        
        Args:
            agent_evaluator: AgentEvaluator instance for the agent
        """
        self.agents[agent_evaluator.agent_id] = agent_evaluator
    
    def remove_agent(self, agent_id: str) -> None:
        """Remove an agent from the team evaluation"""
        if agent_id in self.agents:
            del self.agents[agent_id]
    
    def calculate_team_performance_score(self) -> float:
        """
        Calculate overall team performance score
        Average of all agent performance scores
        
        Returns:
            Team performance score (0-100)
        """
        if not self.agents:
            return 0.0
        
        agent_scores = [agent.calculate_overall_score() for agent in self.agents.values()]
        return round(sum(agent_scores) / len(agent_scores), 2)
    
    def calculate_team_success_rate(self) -> float:
        """
        Calculate team-wide task success rate
        
        Returns:
            Team success rate percentage
        """
        if not self.agents:
            return 0.0
        
        total_assigned = sum(
            agent.performance_metrics.tasks_assigned 
            for agent in self.agents.values()
        )
        total_completed = sum(
            agent.performance_metrics.tasks_completed 
            for agent in self.agents.values()
        )
        
        if total_assigned == 0:
            return 0.0
        
        return round((total_completed / total_assigned) * 100, 2)
    
    def calculate_team_quality_score(self) -> float:
        """
        Calculate team-wide quality score
        Based on code quality, test coverage, and bug rates
        
        Returns:
            Team quality score (0-100)
        """
        if not self.agents:
            return 0.0
        
        quality_scores = []
        for agent in self.agents.values():
            metrics = agent.quality_metrics
            agent_quality = (
                metrics.code_review_score * 0.4 +
                metrics.test_coverage * 0.3 +
                metrics.calculate_test_pass_rate() * 0.3
            )
            quality_scores.append(agent_quality)
        
        return round(sum(quality_scores) / len(quality_scores), 2)
    
    def calculate_team_productivity(self) -> Dict:
        """
        Calculate team productivity metrics
        
        Returns:
            Dictionary with team productivity statistics
        """
        if not self.agents:
            return {}
        
        total_loc = sum(
            agent.productivity_metrics.lines_of_code_written 
            for agent in self.agents.values()
        )
        total_commits = sum(
            agent.productivity_metrics.commits_made 
            for agent in self.agents.values()
        )
        total_prs = sum(
            agent.productivity_metrics.pull_requests_created 
            for agent in self.agents.values()
        )
        total_prs_merged = sum(
            agent.productivity_metrics.pull_requests_merged 
            for agent in self.agents.values()
        )
        total_story_points = sum(
            agent.productivity_metrics.story_points_completed 
            for agent in self.agents.values()
        )
        total_features = sum(
            agent.productivity_metrics.features_delivered 
            for agent in self.agents.values()
        )
        
        return {
            'total_lines_of_code': total_loc,
            'total_commits': total_commits,
            'total_pull_requests': total_prs,
            'total_prs_merged': total_prs_merged,
            'pr_merge_rate': round((total_prs_merged / total_prs * 100) if total_prs > 0 else 0, 2),
            'total_story_points': total_story_points,
            'total_features_delivered': total_features,
            'average_story_points_per_agent': round(total_story_points / len(self.agents), 2)
        }
    
    def calculate_collaboration_health(self) -> Dict:
        """
        Calculate team collaboration health metrics
        
        Returns:
            Dictionary with collaboration statistics
        """
        if not self.agents:
            return {}
        
        total_reviews = sum(
            agent.collaboration_metrics.code_reviews_participated 
            for agent in self.agents.values()
        )
        total_docs = sum(
            agent.collaboration_metrics.documentation_contributions 
            for agent in self.agents.values()
        )
        total_mentoring = sum(
            agent.collaboration_metrics.mentoring_sessions 
            for agent in self.agents.values()
        )
        total_pair_programming = sum(
            agent.collaboration_metrics.pair_programming_sessions 
            for agent in self.agents.values()
        )
        total_blockers_resolved = sum(
            agent.collaboration_metrics.blockers_resolved_for_others 
            for agent in self.agents.values()
        )
        
        avg_collaboration_score = sum(
            agent.collaboration_metrics.calculate_collaboration_score() 
            for agent in self.agents.values()
        ) / len(self.agents)
        
        return {
            'total_code_reviews': total_reviews,
            'total_documentation': total_docs,
            'total_mentoring_sessions': total_mentoring,
            'total_pair_programming': total_pair_programming,
            'total_blockers_resolved': total_blockers_resolved,
            'average_collaboration_score': round(avg_collaboration_score, 2),
            'collaboration_health': self._get_collaboration_health_status(avg_collaboration_score)
        }
    
    def _get_collaboration_health_status(self, score: float) -> str:
        """Determine collaboration health status based on score"""
        if score >= 8.0:
            return 'Excellent'
        elif score >= 6.5:
            return 'Good'
        elif score >= 5.0:
            return 'Fair'
        else:
            return 'Needs Improvement'
    
    def identify_top_performers(self, limit: int = 3) -> List[Dict]:
        """
        Identify top performing agents
        
        Args:
            limit: Number of top performers to return
        
        Returns:
            List of top performers with their scores
        """
        if not self.agents:
            return []
        
        agent_scores = [
            {
                'agent_id': agent.agent_id,
                'agent_role': agent.agent_role,
                'overall_score': agent.calculate_overall_score(),
                'rating': agent.get_performance_rating()
            }
            for agent in self.agents.values()
        ]
        
        # Sort by overall score descending
        agent_scores.sort(key=lambda x: x['overall_score'], reverse=True)
        
        return agent_scores[:limit]
    
    def identify_underperformers(self, threshold: float = 60.0) -> List[Dict]:
        """
        Identify agents performing below threshold
        
        Args:
            threshold: Minimum acceptable performance score
        
        Returns:
            List of underperforming agents with their scores
        """
        if not self.agents:
            return []
        
        underperformers = [
            {
                'agent_id': agent.agent_id,
                'agent_role': agent.agent_role,
                'overall_score': agent.calculate_overall_score(),
                'rating': agent.get_performance_rating(),
                'improvement_areas': agent._identify_improvement_areas()
            }
            for agent in self.agents.values()
            if agent.calculate_overall_score() < threshold
        ]
        
        return underperformers
    
    def calculate_team_velocity(self) -> float:
        """
        Calculate team velocity (story points per time period)
        
        Returns:
            Average story points completed by team
        """
        if not self.agents:
            return 0.0
        
        total_story_points = sum(
            agent.productivity_metrics.story_points_completed 
            for agent in self.agents.values()
        )
        
        return total_story_points
    
    def assess_team_balance(self) -> Dict:
        """
        Assess team balance across different roles and skills
        
        Returns:
            Dictionary with team balance metrics
        """
        role_distribution = {}
        for agent in self.agents.values():
            role = agent.agent_role
            role_distribution[role] = role_distribution.get(role, 0) + 1
        
        # Calculate score variance to assess team balance
        scores = [agent.calculate_overall_score() for agent in self.agents.values()]
        avg_score = sum(scores) / len(scores) if scores else 0
        variance = sum((score - avg_score) ** 2 for score in scores) / len(scores) if scores else 0
        
        return {
            'role_distribution': role_distribution,
            'team_size': len(self.agents),
            'average_team_score': round(avg_score, 2),
            'score_variance': round(variance, 2),
            'is_balanced': variance < 100  # Low variance indicates balanced team
        }
    
    def generate_team_report(self) -> Dict:
        """
        Generate comprehensive team evaluation report
        
        Returns:
            Dictionary containing all team evaluation metrics
        """
        team_performance = self.calculate_team_performance_score()
        team_success_rate = self.calculate_team_success_rate()
        team_quality = self.calculate_team_quality_score()
        productivity = self.calculate_team_productivity()
        collaboration = self.calculate_collaboration_health()
        team_balance = self.assess_team_balance()
        top_performers = self.identify_top_performers()
        underperformers = self.identify_underperformers()
        
        report = {
            'team_name': self.team_name,
            'evaluation_date': datetime.now().isoformat(),
            'team_size': len(self.agents),
            'overall_metrics': {
                'team_performance_score': team_performance,
                'team_success_rate': team_success_rate,
                'team_quality_score': team_quality,
                'team_velocity': self.calculate_team_velocity()
            },
            'productivity_metrics': productivity,
            'collaboration_metrics': collaboration,
            'team_balance': team_balance,
            'top_performers': top_performers,
            'underperformers': underperformers,
            'team_health_status': self._get_team_health_status(team_performance),
            'recommendations': self._generate_team_recommendations(
                team_performance, 
                collaboration, 
                underperformers
            )
        }
        
        # Store in history
        self.evaluation_history.append(report)
        
        return report
    
    def _get_team_health_status(self, score: float) -> str:
        """Determine overall team health status"""
        if score >= 85:
            return 'Excellent - Team is performing at a high level'
        elif score >= 70:
            return 'Good - Team is performing well with minor areas for improvement'
        elif score >= 55:
            return 'Fair - Team performance is acceptable but needs attention'
        else:
            return 'Poor - Team performance requires immediate intervention'
    
    def _generate_team_recommendations(
        self, 
        performance_score: float, 
        collaboration: Dict, 
        underperformers: List[Dict]
    ) -> List[str]:
        """Generate recommendations for team improvement"""
        recommendations = []
        
        if performance_score < 70:
            recommendations.append(
                "Overall team performance is below target. Consider team training and process improvements."
            )
        
        if collaboration.get('average_collaboration_score', 0) < 6.5:
            recommendations.append(
                "Team collaboration needs improvement. Increase code reviews, pair programming, and knowledge sharing."
            )
        
        if len(underperformers) > len(self.agents) * 0.3:
            recommendations.append(
                "High number of underperformers detected. Consider individual mentoring and skill development programs."
            )
        
        if collaboration.get('total_documentation', 0) < len(self.agents) * 5:
            recommendations.append(
                "Documentation contributions are low. Encourage more knowledge documentation and sharing."
            )
        
        productivity = self.calculate_team_productivity()
        if productivity.get('pr_merge_rate', 0) < 70:
            recommendations.append(
                "PR merge rate is low. Review code review processes and ensure timely feedback."
            )
        
        return recommendations
    
    def export_team_metrics_summary(self) -> str:
        """
        Export team metrics as a formatted summary string
        
        Returns:
            Formatted string summary of team metrics
        """
        report = self.generate_team_report()
        
        summary = f"""
{'='*60}
TEAM EVALUATION REPORT
{'='*60}
Team: {report['team_name']}
Evaluation Date: {report['evaluation_date']}
Team Size: {report['team_size']} members

OVERALL PERFORMANCE
{'-'*60}
Team Performance Score: {report['overall_metrics']['team_performance_score']}/100
Team Success Rate: {report['overall_metrics']['team_success_rate']}%
Team Quality Score: {report['overall_metrics']['team_quality_score']}/100
Team Velocity: {report['overall_metrics']['team_velocity']} story points

Team Health Status: {report['team_health_status']}

PRODUCTIVITY METRICS
{'-'*60}
Total Lines of Code: {report['productivity_metrics']['total_lines_of_code']}
Total Commits: {report['productivity_metrics']['total_commits']}
Pull Requests: {report['productivity_metrics']['total_pull_requests']} (Merged: {report['productivity_metrics']['total_prs_merged']})
PR Merge Rate: {report['productivity_metrics']['pr_merge_rate']}%
Features Delivered: {report['productivity_metrics']['total_features_delivered']}

COLLABORATION METRICS
{'-'*60}
Code Reviews: {report['collaboration_metrics']['total_code_reviews']}
Documentation Contributions: {report['collaboration_metrics']['total_documentation']}
Mentoring Sessions: {report['collaboration_metrics']['total_mentoring_sessions']}
Pair Programming: {report['collaboration_metrics']['total_pair_programming']}
Collaboration Health: {report['collaboration_metrics']['collaboration_health']}

TOP PERFORMERS
{'-'*60}
"""
        for i, performer in enumerate(report['top_performers'], 1):
            summary += f"{i}. {performer['agent_role']} - Score: {performer['overall_score']}/100 ({performer['rating']})\n"
        
        if report['underperformers']:
            summary += f"\nUNDERPERFORMERS\n{'-'*60}\n"
            for performer in report['underperformers']:
                summary += f"- {performer['agent_role']} - Score: {performer['overall_score']}/100\n"
        
        if report['recommendations']:
            summary += f"\nRECOMMENDATIONS\n{'-'*60}\n"
            for i, rec in enumerate(report['recommendations'], 1):
                summary += f"{i}. {rec}\n"
        
        summary += f"{'='*60}\n"
        
        return summary
