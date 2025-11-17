"""
Analytics Module

Provides analytics and reporting functionality for tracking leads,
campaigns, and performance metrics.
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
from collections import Counter


class Analytics:
    """
    Analytics class for tracking and reporting application metrics.
    
    Tracks:
    - Total leads discovered
    - Leads per run
    - Industries found
    - Duplicate detection
    - Success/failure rates
    """
    
    def __init__(self, analytics_file: str = "logs/analytics.json"):
        """
        Initialize analytics tracker.
        
        Args:
            analytics_file: Path to analytics data file
        """
        self.analytics_file = Path(analytics_file)
        self.data = self._load_analytics()
    
    def _load_analytics(self) -> dict:
        """
        Load analytics data from file.
        
        Returns:
            Analytics data dictionary
        """
        if self.analytics_file.exists():
            try:
                with open(self.analytics_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Warning: Could not load analytics: {e}")
                return self._initialize_data()
        return self._initialize_data()
    
    def _initialize_data(self) -> dict:
        """
        Initialize empty analytics data structure.
        
        Returns:
            Empty analytics dictionary
        """
        return {
            "total_runs": 0,
            "total_leads_discovered": 0,
            "total_emails_generated": 0,
            "total_portfolios_created": 0,
            "total_duplicates_found": 0,
            "industries": {},
            "runs": [],
            "created_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat()
        }
    
    def _save_analytics(self):
        """Save analytics data to file."""
        try:
            self.analytics_file.parent.mkdir(parents=True, exist_ok=True)
            self.data["last_updated"] = datetime.now().isoformat()
            with open(self.analytics_file, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Warning: Could not save analytics: {e}")
    
    def record_run(self, business_name: str, leads_found: int, 
                   emails_generated: int, portfolios_created: int,
                   duplicates: int, industries: List[str],
                   success: bool = True, error: Optional[str] = None):
        """
        Record a new run in analytics.
        
        Args:
            business_name: Name of the business
            leads_found: Number of leads discovered
            emails_generated: Number of emails generated
            portfolios_created: Number of portfolios created
            duplicates: Number of duplicate leads found
            industries: List of industries found
            success: Whether the run was successful
            error: Error message if failed
        """
        run_data = {
            "timestamp": datetime.now().isoformat(),
            "business_name": business_name,
            "leads_found": leads_found,
            "emails_generated": emails_generated,
            "portfolios_created": portfolios_created,
            "duplicates": duplicates,
            "industries": industries,
            "success": success,
            "error": error
        }
        
        # Update totals
        self.data["total_runs"] += 1
        self.data["total_leads_discovered"] += leads_found
        self.data["total_emails_generated"] += emails_generated
        self.data["total_portfolios_created"] += portfolios_created
        self.data["total_duplicates_found"] += duplicates
        
        # Update industries
        for industry in industries:
            self.data["industries"][industry] = self.data["industries"].get(industry, 0) + 1
        
        # Add run to history
        self.data["runs"].append(run_data)
        
        # Save to file
        self._save_analytics()
    
    def get_summary(self) -> Dict:
        """
        Get analytics summary.
        
        Returns:
            Dictionary with analytics summary
        """
        return {
            "total_runs": self.data["total_runs"],
            "total_leads": self.data["total_leads_discovered"],
            "total_emails": self.data["total_emails_generated"],
            "total_portfolios": self.data["total_portfolios_created"],
            "total_duplicates": self.data["total_duplicates_found"],
            "unique_industries": len(self.data["industries"]),
            "top_industries": self._get_top_industries(5),
            "avg_leads_per_run": self._calculate_avg_leads_per_run(),
            "success_rate": self._calculate_success_rate(),
            "last_run": self._get_last_run_info()
        }
    
    def _get_top_industries(self, count: int = 5) -> List[tuple]:
        """
        Get top industries by frequency.
        
        Args:
            count: Number of top industries to return
        
        Returns:
            List of (industry, count) tuples
        """
        counter = Counter(self.data["industries"])
        return counter.most_common(count)
    
    def _calculate_avg_leads_per_run(self) -> float:
        """
        Calculate average leads per run.
        
        Returns:
            Average leads per run
        """
        if self.data["total_runs"] == 0:
            return 0.0
        return round(self.data["total_leads_discovered"] / self.data["total_runs"], 2)
    
    def _calculate_success_rate(self) -> float:
        """
        Calculate success rate of runs.
        
        Returns:
            Success rate as percentage
        """
        if not self.data["runs"]:
            return 0.0
        successful = sum(1 for run in self.data["runs"] if run.get("success", False))
        return round((successful / len(self.data["runs"])) * 100, 2)
    
    def _get_last_run_info(self) -> Optional[Dict]:
        """
        Get information about the last run.
        
        Returns:
            Last run data or None
        """
        if not self.data["runs"]:
            return None
        last_run = self.data["runs"][-1]
        return {
            "timestamp": last_run["timestamp"],
            "business_name": last_run["business_name"],
            "leads_found": last_run["leads_found"],
            "success": last_run["success"]
        }
    
    def get_runs_by_date_range(self, days: int = 7) -> List[Dict]:
        """
        Get runs within specified date range.
        
        Args:
            days: Number of days to look back
        
        Returns:
            List of runs within date range
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        recent_runs = []
        
        for run in self.data["runs"]:
            run_date = datetime.fromisoformat(run["timestamp"])
            if run_date >= cutoff_date:
                recent_runs.append(run)
        
        return recent_runs
    
    def print_summary(self):
        """Print formatted analytics summary to console."""
        summary = self.get_summary()
        
        print("\n" + "="*60)
        print(" 📊 ANALYTICS SUMMARY")
        print("="*60)
        print(f"Total Runs: {summary['total_runs']}")
        print(f"Total Leads Discovered: {summary['total_leads']}")
        print(f"Total Emails Generated: {summary['total_emails']}")
        print(f"Total Portfolios Created: {summary['total_portfolios']}")
        print(f"Duplicates Prevented: {summary['total_duplicates']}")
        print(f"Average Leads per Run: {summary['avg_leads_per_run']}")
        print(f"Success Rate: {summary['success_rate']}%")
        print(f"\nUnique Industries: {summary['unique_industries']}")
        
        if summary['top_industries']:
            print("\nTop Industries:")
            for industry, count in summary['top_industries']:
                print(f"  • {industry}: {count} leads")
        
        if summary['last_run']:
            print(f"\nLast Run:")
            print(f"  • Date: {summary['last_run']['timestamp']}")
            print(f"  • Business: {summary['last_run']['business_name']}")
            print(f"  • Leads: {summary['last_run']['leads_found']}")
            print(f"  • Status: {'✅ Success' if summary['last_run']['success'] else '❌ Failed'}")
        
        print("="*60 + "\n")
    
    def export_to_json(self, output_file: str = "output/analytics_export.json"):
        """
        Export analytics data to JSON file.
        
        Args:
            output_file: Path to output file
        """
        try:
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
            print(f"Analytics exported to {output_file}")
        except Exception as e:
            print(f"Error exporting analytics: {e}")
