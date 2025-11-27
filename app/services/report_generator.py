"""Report generation service"""

from typing import Dict, Optional, List
from datetime import datetime
import json


class ReportGenerator:
    """Service for generating various types of reports"""
    
    @staticmethod
    def generate_signal_coverage_report(
        measurements: List[Dict],
        statistics: Dict,
        area_bounds: Dict
    ) -> Dict:
        """
        Generate a signal coverage report.
        
        Args:
            measurements: List of signal measurements
            statistics: Coverage statistics
            area_bounds: Area boundaries
            
        Returns:
            Report data dictionary
        """
        report_data = {
            "report_type": "signal_coverage",
            "generated_at": datetime.utcnow().isoformat(),
            "area_bounds": area_bounds,
            "statistics": statistics,
            "measurements_count": len(measurements),
            "summary": {
                "average_signal": statistics.get("average_signal_dbm"),
                "coverage_percentage": statistics.get("coverage_percentage"),
                "total_measurements": statistics.get("total_measurements")
            }
        }
        
        return report_data
    
    @staticmethod
    def generate_operator_comparison_report(
        operator_stats: Dict[str, Dict],
        area_bounds: Dict
    ) -> Dict:
        """
        Generate an operator comparison report.
        
        Args:
            operator_stats: Statistics for each operator
            area_bounds: Area boundaries
            
        Returns:
            Report data dictionary
        """
        # Rank operators
        ranked_operators = sorted(
            operator_stats.items(),
            key=lambda x: x[1].get("average_signal_dbm", -999),
            reverse=True
        )
        
        report_data = {
            "report_type": "operator_comparison",
            "generated_at": datetime.utcnow().isoformat(),
            "area_bounds": area_bounds,
            "operators": operator_stats,
            "ranking": [
                {
                    "rank": idx + 1,
                    "operator": op,
                    "avg_signal": stats.get("average_signal_dbm"),
                    "coverage_percentage": stats.get("coverage_percentage")
                }
                for idx, (op, stats) in enumerate(ranked_operators)
            ]
        }
        
        return report_data
    
    @staticmethod
    def generate_link_budget_report(
        link_budget_results: Dict,
        parameters: Dict
    ) -> Dict:
        """
        Generate a link budget analysis report.
        
        Args:
            link_budget_results: Results from link budget calculation
            parameters: Input parameters
            
        Returns:
            Report data dictionary
        """
        report_data = {
            "report_type": "link_budget",
            "generated_at": datetime.utcnow().isoformat(),
            "parameters": parameters,
            "results": link_budget_results,
            "conclusions": {
                "is_viable": link_budget_results.get("is_viable"),
                "link_margin": link_budget_results.get("link_margin_db"),
                "recommendation": (
                    "Link is viable with sufficient margin" 
                    if link_budget_results.get("link_margin_db", 0) > 10
                    else "Link may be marginal, consider improvements"
                    if link_budget_results.get("is_viable")
                    else "Link is not viable, redesign required"
                )
            }
        }
        
        return report_data
    
    @staticmethod
    def generate_tower_coverage_report(
        towers: List,
        area_bounds: Dict,
        operator: Optional[str] = None
    ) -> Dict:
        """
        Generate a tower coverage report.
        
        Args:
            towers: List of towers
            area_bounds: Area boundaries
            operator: Optional operator filter
            
        Returns:
            Report data dictionary
        """
        # Group towers by technology
        tech_distribution = {}
        for tower in towers:
            tech = tower.technology or "Unknown"
            tech_distribution[tech] = tech_distribution.get(tech, 0) + 1
        
        report_data = {
            "report_type": "tower_coverage",
            "generated_at": datetime.utcnow().isoformat(),
            "area_bounds": area_bounds,
            "operator": operator,
            "total_towers": len(towers),
            "technology_distribution": tech_distribution,
            "towers": [
                {
                    "id": tower.id,
                    "operator": tower.operator,
                    "cell_id": tower.cell_id,
                    "latitude": tower.latitude,
                    "longitude": tower.longitude,
                    "technology": tower.technology,
                    "frequency_mhz": tower.frequency_mhz
                }
                for tower in towers
            ]
        }
        
        return report_data
    
    @staticmethod
    def generate_speed_test_report(
        speed_tests: List,
        statistics: Dict
    ) -> Dict:
        """
        Generate a speed test analysis report.
        
        Args:
            speed_tests: List of speed test results
            statistics: Speed test statistics
            
        Returns:
            Report data dictionary
        """
        report_data = {
            "report_type": "speed_test_analysis",
            "generated_at": datetime.utcnow().isoformat(),
            "total_tests": len(speed_tests),
            "statistics": statistics,
            "summary": {
                "avg_download_mbps": statistics.get("avg_download_mbps"),
                "avg_upload_mbps": statistics.get("avg_upload_mbps"),
                "avg_ping_ms": statistics.get("avg_ping_ms")
            }
        }
        
        return report_data
    
    @staticmethod
    def export_to_json(report_data: Dict) -> str:
        """
        Export report data to JSON string.
        
        Args:
            report_data: Report data dictionary
            
        Returns:
            JSON string
        """
        return json.dumps(report_data, indent=2, default=str)
    
    @staticmethod
    def generate_summary(report_data: Dict) -> str:
        """
        Generate a text summary of a report.
        
        Args:
            report_data: Report data dictionary
            
        Returns:
            Summary text
        """
        report_type = report_data.get("report_type", "Unknown")
        generated_at = report_data.get("generated_at", "Unknown")
        
        summary = f"Report Type: {report_type}\n"
        summary += f"Generated: {generated_at}\n"
        summary += "-" * 50 + "\n"
        
        if report_type == "signal_coverage":
            stats = report_data.get("summary", {})
            summary += f"Average Signal: {stats.get('average_signal')} dBm\n"
            summary += f"Coverage: {stats.get('coverage_percentage')}%\n"
            summary += f"Total Measurements: {stats.get('total_measurements')}\n"
        
        elif report_type == "link_budget":
            results = report_data.get("results", {})
            summary += f"Received Power: {results.get('received_power_dbm')} dBm\n"
            summary += f"Path Loss: {results.get('path_loss_db')} dB\n"
            summary += f"Link Margin: {results.get('link_margin_db')} dB\n"
            summary += f"Viable: {'Yes' if results.get('is_viable') else 'No'}\n"
        
        return summary


# Global instance
report_generator = ReportGenerator()

