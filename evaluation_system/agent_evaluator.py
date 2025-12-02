# agent_evaluator.py - Individual Agent Performance Evaluator
# Evaluates individual agent performance across multiple dimensions

from typing import Dict, List, Optional
from datetime import datetime, timedelta
from .metrics import PerformanceMetrics, QualityMetrics, ProductivityMetrics, CollaborationMetrics


class AgentEvaluator:
    """
    Evaluates individual agent performance using multiple metrics categories
    """
    
    # Role-specific performance thresholds
    ROLE_THRESHOLDS = {
        'Project_Manager': {
            'min_success_rate': 85.0,
            'min_on_time_delivery': 80.0,
            'min_collaboration_score': 8.0
        },
        'Software_Architect': {
            'min_success_rate': 90.0,
            'min_code_quality': 85.0,
            'min_review_score': 8.5
        },
        'Frontend_Developer': {
            'min_success_rate': 80.0,
            'min_code_quality': 75.0,
            'min_test_coverage': 70.0
        },
        'Backend_Developer': {
            'min_success_rate': 80.0,
            'min_code_quality': 80.0,
            'min_test_coverage': 75.0
        },
        'Data_Engineer': {
            'min_success_rate': 85.0,
            'min_code_quality': 80.0,
            'min_data_quality': 90.0
        },
        'Data_Scientist': {
            'min_success_rate': 75.0,
            'min_model_accuracy': 85.0,
            'min_documentation': 70.0
        },
        'ML_Engineer': {
            'min_success_rate': 80.0,
            'min_model_performance': 85.0,
            'min_deployment_success': 90.0
        },
        'DevOps_Engineer': {
            'min_success_rate': 90.0,
            'min_uptime': 99.0,
            'min_deployment_success': 95.0
        },
        'QA_Engineer': {
            'min_success_rate': 85.0,
            'min_bug_detection': 80.0,
            'min_test_coverage': 85.0
        },
        'Security_Engineer': {
            'min_success_rate': 90.0,
            'min_vulnerability_detection': 85.0,
            'min_security_score': 90.0
        }
    }
    
    def __init__(self, agent_id: str, agent_role: str):
        """
        Initialize agent evaluator
        
        Args:
            agent_id: Unique identifier for the agent
            agent_role: Role of the agent (e.g., 'Frontend_Developer')
        """
        self.agent_id = agent_id
        self.agent_role = agent_role
        self.performance_metrics = PerformanceMetrics(agent_id, agent_role)
        self.quality_metrics = QualityMetrics(agent_id, agent_role)
        self.productivity_metrics = ProductivityMetrics(agent_id, agent_role)
        self.collaboration_metrics = CollaborationMetrics(agent_id, agent_role)
        self.evaluation_history: List[Dict] = []
    
    def update_performance_metrics(self, **kwargs) -> None:
        """Update performance metrics with new data"""
        for key, value in kwargs.items():
            if hasattr(self.performance_metrics, key):
                setattr(self.performance_metrics, key, value)
        self.performance_metrics.calculate_success_rate()
    
    def update_quality_metrics(self, **kwargs) -> None:
        """Update quality metrics with new data"""
        for key, value in kwargs.items():
            if hasattr(self.quality_metrics, key):
                setattr(self.quality_metrics, key, value)
    
    def update_productivity_metrics(self, **kwargs) -> None:
        """Update productivity metrics with new data"""
        for key, value in kwargs.items():
            if hasattr(self.productivity_metrics, key):
                setattr(self.productivity_metrics, key, value)
    
    def update_collaboration_metrics(self, **kwargs) -> None:
        """Update collaboration metrics with new data"""
        for key, value in kwargs.items():
            if hasattr(self.collaboration_metrics, key):
                setattr(self.collaboration_metrics, key, value)
    
    def calculate_overall_score(self) -> float:
        """
        Calculate overall performance score (0-100)
        Weighted average of different metric categories
        """
        weights = {
            'performance': 0.30,
            'quality': 0.30,
            'productivity': 0.25,
            'collaboration': 0.15
        }
        
        # Performance score
        performance_score = self.performance_metrics.success_rate
        
        # Quality score (normalized to 0-100)
        quality_components = [
            self.quality_metrics.code_review_score,
            self.quality_metrics.calculate_test_pass_rate(),
            max(0, 100 - (self.quality_metrics.bug_count * 2))  # Penalty for bugs
        ]
        quality_score = sum(quality_components) / len(quality_components)
        
        # Productivity score (normalized to 0-100)
        productivity_score = min(100, (
            self.productivity_metrics.calculate_pr_merge_rate() * 0.4 +
            self.productivity_metrics.story_points_completed * 2 +
            self.productivity_metrics.documentation_coverage * 0.4
        ))
        
        # Collaboration score (normalized to 0-100)
        collaboration_score = self.collaboration_metrics.calculate_collaboration_score() * 10
        
        # Calculate weighted overall score
        overall_score = (
            performance_score * weights['performance'] +
            quality_score * weights['quality'] +
            productivity_score * weights['productivity'] +
            collaboration_score * weights['collaboration']
        )
        
        return round(overall_score, 2)
    
    def evaluate_against_thresholds(self) -> Dict[str, bool]:
        """
        Evaluate agent performance against role-specific thresholds
        
        Returns:
            Dictionary of threshold checks with pass/fail status
        """
        thresholds = self.ROLE_THRESHOLDS.get(self.agent_role, {})
        results = {}
        
        if 'min_success_rate' in thresholds:
            results['success_rate'] = (
                self.performance_metrics.success_rate >= thresholds['min_success_rate']
            )
        
        if 'min_on_time_delivery' in thresholds:
            results['on_time_delivery'] = (
                self.performance_metrics.on_time_delivery_rate >= thresholds['min_on_time_delivery']
            )
        
        if 'min_code_quality' in thresholds:
            results['code_quality'] = (
                self.quality_metrics.code_review_score >= thresholds['min_code_quality']
            )
        
        if 'min_test_coverage' in thresholds:
            results['test_coverage'] = (
                self.quality_metrics.test_coverage >= thresholds['min_test_coverage']
            )
        
        if 'min_collaboration_score' in thresholds:
            results['collaboration'] = (
                self.collaboration_metrics.calculate_collaboration_score() >= 
                thresholds['min_collaboration_score']
            )
        
        return results
    
    def get_performance_rating(self) -> str:
        """
        Get performance rating based on overall score
        
        Returns:
            Rating: 'Excellent', 'Good', 'Satisfactory', 'Needs Improvement', 'Poor'
        """
        score = self.calculate_overall_score()
        
        if score >= 90:
            return 'Excellent'
        elif score >= 75:
            return 'Good'
        elif score >= 60:
            return 'Satisfactory'
        elif score >= 40:
            return 'Needs Improvement'
        else:
            return 'Poor'
    
    def generate_evaluation_report(self) -> Dict:
        """
        Generate comprehensive evaluation report for the agent
        
        Returns:
            Dictionary containing all evaluation metrics and analysis
        """
        overall_score = self.calculate_overall_score()
        rating = self.get_performance_rating()
        threshold_results = self.evaluate_against_thresholds()
        
        report = {
            'agent_id': self.agent_id,
            'agent_role': self.agent_role,
            'evaluation_date': datetime.now().isoformat(),
            'overall_score': overall_score,
            'performance_rating': rating,
            'threshold_checks': threshold_results,
            'metrics': {
                'performance': self.performance_metrics.to_dict(),
                'quality': self.quality_metrics.to_dict(),
                'productivity': self.productivity_metrics.to_dict(),
                'collaboration': self.collaboration_metrics.to_dict()
            },
            'strengths': self.identify_strengths(),
            'areas_for_improvement': self.identify_improvement_areas()
        }
        
        # Store in history
        self.evaluation_history.append(report)
        
        return report
    
    def identify_strengths(self) -> List[str]:
        """Identify agent's strengths based on metrics"""
        strengths = []
        
        if self.performance_metrics.success_rate >= 85:
            strengths.append("High task success rate")
        
        if self.quality_metrics.code_review_score >= 85:
            strengths.append("Excellent code quality")
        
        if self.quality_metrics.test_coverage >= 80:
            strengths.append("Strong test coverage")
        
        if self.productivity_metrics.calculate_pr_merge_rate() >= 80:
            strengths.append("High PR merge rate")
        
        if self.collaboration_metrics.calculate_collaboration_score() >= 8.0:
            strengths.append("Excellent team collaboration")
        
        if self.quality_metrics.bug_count <= 5:
            strengths.append("Low bug count")
        
        return strengths
    
    def identify_improvement_areas(self) -> List[str]:
        """Identify areas where agent needs improvement"""
        areas = []
        
        if self.performance_metrics.success_rate < 70:
            areas.append("Task success rate needs improvement")
        
        if self.quality_metrics.code_review_score < 70:
            areas.append("Code quality needs enhancement")
        
        if self.quality_metrics.test_coverage < 60:
            areas.append("Test coverage should be increased")
        
        if self.quality_metrics.bug_count > 15:
            areas.append("Bug count is high, focus on quality")
        
        if self.productivity_metrics.documentation_coverage < 50:
            areas.append("Documentation needs improvement")
        
        if self.collaboration_metrics.calculate_collaboration_score() < 6.0:
            areas.append("Collaboration and communication need attention")
        
        return areas
    
    def compare_with_previous(self, lookback_periods: int = 1) -> Optional[Dict]:
        """
        Compare current performance with previous evaluation(s)
        
        Args:
            lookback_periods: Number of previous evaluations to compare with
        
        Returns:
            Dictionary showing trends and changes
        """
        if len(self.evaluation_history) < lookback_periods + 1:
            return None
        
        current = self.evaluation_history[-1]
        previous = self.evaluation_history[-(lookback_periods + 1)]
        
        return {
            'score_change': current['overall_score'] - previous['overall_score'],
            'rating_change': f"{previous['performance_rating']} → {current['performance_rating']}",
            'trend': 'improving' if current['overall_score'] > previous['overall_score'] else 'declining'
        }
