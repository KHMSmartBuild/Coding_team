# metrics.py - Core Metrics for Agent and Team Evaluation
# Defines various metrics used to evaluate agent performance and team effectiveness

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from datetime import datetime
from enum import Enum


class MetricCategory(Enum):
    """Categories of evaluation metrics"""
    PERFORMANCE = "performance"
    QUALITY = "quality"
    PRODUCTIVITY = "productivity"
    COLLABORATION = "collaboration"


@dataclass
class PerformanceMetrics:
    """
    Performance metrics for individual agents
    Tracks task completion, response time, and efficiency
    """
    agent_id: str
    agent_role: str
    
    # Task metrics
    tasks_assigned: int = 0
    tasks_completed: int = 0
    tasks_in_progress: int = 0
    tasks_failed: int = 0
    
    # Time metrics (in seconds)
    average_task_completion_time: float = 0.0
    total_working_time: float = 0.0
    
    # Success metrics
    success_rate: float = 0.0
    on_time_delivery_rate: float = 0.0
    
    # Timestamp
    evaluation_timestamp: datetime = field(default_factory=datetime.now)
    
    def calculate_success_rate(self) -> float:
        """Calculate task success rate"""
        if self.tasks_assigned == 0:
            return 0.0
        self.success_rate = (self.tasks_completed / self.tasks_assigned) * 100
        return self.success_rate
    
    def calculate_completion_rate(self) -> float:
        """Calculate task completion rate"""
        if self.tasks_assigned == 0:
            return 0.0
        return ((self.tasks_completed + self.tasks_failed) / self.tasks_assigned) * 100
    
    def to_dict(self) -> Dict:
        """Convert metrics to dictionary"""
        return {
            'agent_id': self.agent_id,
            'agent_role': self.agent_role,
            'tasks_assigned': self.tasks_assigned,
            'tasks_completed': self.tasks_completed,
            'tasks_in_progress': self.tasks_in_progress,
            'tasks_failed': self.tasks_failed,
            'average_task_completion_time': self.average_task_completion_time,
            'total_working_time': self.total_working_time,
            'success_rate': self.success_rate,
            'on_time_delivery_rate': self.on_time_delivery_rate,
            'evaluation_timestamp': self.evaluation_timestamp.isoformat()
        }


@dataclass
class QualityMetrics:
    """
    Quality metrics for code and deliverables
    Tracks code quality, bug rates, and review feedback
    """
    agent_id: str
    agent_role: str
    
    # Code quality metrics
    code_review_score: float = 0.0  # 0-100 scale
    bug_count: int = 0
    critical_bugs: int = 0
    major_bugs: int = 0
    minor_bugs: int = 0
    
    # Testing metrics
    test_coverage: float = 0.0  # Percentage
    tests_passed: int = 0
    tests_failed: int = 0
    
    # Review metrics
    code_reviews_given: int = 0
    code_reviews_received: int = 0
    review_feedback_score: float = 0.0  # 0-10 scale
    
    # Security metrics
    security_vulnerabilities: int = 0
    security_issues_resolved: int = 0
    
    # Timestamp
    evaluation_timestamp: datetime = field(default_factory=datetime.now)
    
    def calculate_bug_density(self, lines_of_code: int) -> float:
        """Calculate bugs per 1000 lines of code"""
        if lines_of_code == 0:
            return 0.0
        return (self.bug_count / lines_of_code) * 1000
    
    def calculate_test_pass_rate(self) -> float:
        """Calculate test pass rate"""
        total_tests = self.tests_passed + self.tests_failed
        if total_tests == 0:
            return 0.0
        return (self.tests_passed / total_tests) * 100
    
    def to_dict(self) -> Dict:
        """Convert metrics to dictionary"""
        return {
            'agent_id': self.agent_id,
            'agent_role': self.agent_role,
            'code_review_score': self.code_review_score,
            'bug_count': self.bug_count,
            'critical_bugs': self.critical_bugs,
            'major_bugs': self.major_bugs,
            'minor_bugs': self.minor_bugs,
            'test_coverage': self.test_coverage,
            'tests_passed': self.tests_passed,
            'tests_failed': self.tests_failed,
            'code_reviews_given': self.code_reviews_given,
            'code_reviews_received': self.code_reviews_received,
            'review_feedback_score': self.review_feedback_score,
            'security_vulnerabilities': self.security_vulnerabilities,
            'security_issues_resolved': self.security_issues_resolved,
            'evaluation_timestamp': self.evaluation_timestamp.isoformat()
        }


@dataclass
class ProductivityMetrics:
    """
    Productivity metrics for individual agents
    Tracks output, velocity, and efficiency
    """
    agent_id: str
    agent_role: str
    
    # Output metrics
    lines_of_code_written: int = 0
    commits_made: int = 0
    pull_requests_created: int = 0
    pull_requests_merged: int = 0
    
    # Velocity metrics
    story_points_completed: int = 0
    features_delivered: int = 0
    
    # Efficiency metrics
    code_reuse_rate: float = 0.0  # Percentage
    refactoring_rate: float = 0.0  # Percentage
    documentation_coverage: float = 0.0  # Percentage
    
    # Time management
    estimated_vs_actual_ratio: float = 1.0  # <1 faster, >1 slower
    
    # Timestamp
    evaluation_timestamp: datetime = field(default_factory=datetime.now)
    
    def calculate_pr_merge_rate(self) -> float:
        """Calculate pull request merge rate"""
        if self.pull_requests_created == 0:
            return 0.0
        return (self.pull_requests_merged / self.pull_requests_created) * 100
    
    def calculate_velocity_score(self) -> float:
        """Calculate overall velocity score"""
        # Weighted combination of various productivity factors
        factors = [
            self.story_points_completed,
            self.features_delivered,
            self.pull_requests_merged
        ]
        return sum(factors) / len(factors) if factors else 0.0
    
    def to_dict(self) -> Dict:
        """Convert metrics to dictionary"""
        return {
            'agent_id': self.agent_id,
            'agent_role': self.agent_role,
            'lines_of_code_written': self.lines_of_code_written,
            'commits_made': self.commits_made,
            'pull_requests_created': self.pull_requests_created,
            'pull_requests_merged': self.pull_requests_merged,
            'story_points_completed': self.story_points_completed,
            'features_delivered': self.features_delivered,
            'code_reuse_rate': self.code_reuse_rate,
            'refactoring_rate': self.refactoring_rate,
            'documentation_coverage': self.documentation_coverage,
            'estimated_vs_actual_ratio': self.estimated_vs_actual_ratio,
            'evaluation_timestamp': self.evaluation_timestamp.isoformat()
        }


@dataclass
class CollaborationMetrics:
    """
    Collaboration metrics for team interaction
    Tracks communication, knowledge sharing, and teamwork
    """
    agent_id: str
    agent_role: str
    
    # Communication metrics
    messages_sent: int = 0
    code_reviews_participated: int = 0
    meetings_attended: int = 0
    
    # Knowledge sharing
    documentation_contributions: int = 0
    knowledge_base_articles: int = 0
    mentoring_sessions: int = 0
    pair_programming_sessions: int = 0
    
    # Team support
    blockers_resolved_for_others: int = 0
    questions_answered: int = 0
    
    # Collaboration quality
    responsiveness_score: float = 0.0  # 0-10 scale
    teamwork_score: float = 0.0  # 0-10 scale
    communication_clarity_score: float = 0.0  # 0-10 scale
    
    # Timestamp
    evaluation_timestamp: datetime = field(default_factory=datetime.now)
    
    def calculate_collaboration_score(self) -> float:
        """Calculate overall collaboration score"""
        scores = [
            self.responsiveness_score,
            self.teamwork_score,
            self.communication_clarity_score
        ]
        return sum(scores) / len(scores) if scores else 0.0
    
    def to_dict(self) -> Dict:
        """Convert metrics to dictionary"""
        return {
            'agent_id': self.agent_id,
            'agent_role': self.agent_role,
            'messages_sent': self.messages_sent,
            'code_reviews_participated': self.code_reviews_participated,
            'meetings_attended': self.meetings_attended,
            'documentation_contributions': self.documentation_contributions,
            'knowledge_base_articles': self.knowledge_base_articles,
            'mentoring_sessions': self.mentoring_sessions,
            'pair_programming_sessions': self.pair_programming_sessions,
            'blockers_resolved_for_others': self.blockers_resolved_for_others,
            'questions_answered': self.questions_answered,
            'responsiveness_score': self.responsiveness_score,
            'teamwork_score': self.teamwork_score,
            'communication_clarity_score': self.communication_clarity_score,
            'evaluation_timestamp': self.evaluation_timestamp.isoformat()
        }
