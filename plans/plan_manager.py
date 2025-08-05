"""
Plan manager for the service station operations bot.

Detects completion of plans and moves them from unimplemented to implemented.
"""

import os
import re
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class PlanManager:
    """Manages plan lifecycle and automation."""
    
    def __init__(self, plans_dir: str = "plans"):
        self.plans_dir = Path(plans_dir)
        self.unimplemented_dir = self.plans_dir / "unimplemented"
        self.implemented_dir = self.plans_dir / "implemented"
        
        # Ensure directories exist
        self.unimplemented_dir.mkdir(parents=True, exist_ok=True)
        self.implemented_dir.mkdir(parents=True, exist_ok=True)
    
    def get_unimplemented_plans(self) -> List[Path]:
        """Get all unimplemented plan files."""
        return list(self.unimplemented_dir.glob("*.md"))
    
    def get_implemented_plans(self) -> List[Path]:
        """Get all implemented plan files."""
        return list(self.implemented_dir.glob("*.md"))
    
    def parse_plan_file(self, file_path: Path) -> Dict[str, Any]:
        """Parse a plan markdown file and extract metadata."""
        try:
            content = file_path.read_text(encoding='utf-8')
            
            # Extract title
            title_match = re.search(r'^# (.+)$', content, re.MULTILINE)
            title = title_match.group(1) if title_match else file_path.stem
            
            # Extract completion checklist
            checklist_items = []
            for line in content.split('\n'):
                if line.strip().startswith('- [x]') or line.strip().startswith('- [X]'):
                    checklist_items.append(line.strip())
                elif line.strip().startswith('- [ ]'):
                    checklist_items.append(line.strip())
            
            # Count completed vs total items
            completed = len([item for item in checklist_items if item.startswith('- [x]') or item.startswith('- [X]')])
            total = len(checklist_items)
            
            return {
                'file_path': file_path,
                'title': title,
                'content': content,
                'checklist_items': checklist_items,
                'completed_count': completed,
                'total_count': total,
                'completion_percentage': (completed / total * 100) if total > 0 else 0
            }
            
        except Exception as e:
            logger.error(f"Error parsing plan file {file_path}: {e}")
            return {
                'file_path': file_path,
                'title': file_path.stem,
                'content': '',
                'checklist_items': [],
                'completed_count': 0,
                'total_count': 0,
                'completion_percentage': 0
            }
    
    def is_plan_complete(self, plan_data: Dict[str, Any]) -> bool:
        """Check if a plan is complete based on its checklist."""
        # A plan is complete if all checklist items are marked as done
        return plan_data['completed_count'] == plan_data['total_count'] and plan_data['total_count'] > 0
    
    def move_plan_to_implemented(self, plan_data: Dict[str, Any]) -> bool:
        """Move a completed plan from unimplemented to implemented."""
        try:
            source_path = plan_data['file_path']
            dest_path = self.implemented_dir / source_path.name
            
            # Add completion timestamp to the content
            completion_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            updated_content = plan_data['content'] + f"\n\n---\n\n**Completed on:** {completion_timestamp}\n**Status:** Implemented"
            
            # Write updated content to destination
            dest_path.write_text(updated_content, encoding='utf-8')
            
            # Remove source file
            source_path.unlink()
            
            logger.info(f"Moved plan '{plan_data['title']}' to implemented")
            return True
            
        except Exception as e:
            logger.error(f"Error moving plan {plan_data['title']}: {e}")
            return False
    
    def check_and_promote_plans(self) -> List[Dict[str, Any]]:
        """Check all unimplemented plans and promote completed ones."""
        promoted_plans = []
        
        for plan_file in self.get_unimplemented_plans():
            plan_data = self.parse_plan_file(plan_file)
            
            if self.is_plan_complete(plan_data):
                if self.move_plan_to_implemented(plan_data):
                    promoted_plans.append(plan_data)
        
        return promoted_plans
    
    def get_plan_status_summary(self) -> Dict[str, Any]:
        """Get a summary of plan status."""
        unimplemented_plans = [self.parse_plan_file(f) for f in self.get_unimplemented_plans()]
        implemented_plans = [self.parse_plan_file(f) for f in self.get_implemented_plans()]
        
        return {
            'unimplemented_count': len(unimplemented_plans),
            'implemented_count': len(implemented_plans),
            'total_count': len(unimplemented_plans) + len(implemented_plans),
            'unimplemented_plans': [p['title'] for p in unimplemented_plans],
            'implemented_plans': [p['title'] for p in implemented_plans],
            'completion_stats': {
                'total_completed_items': sum(p['completed_count'] for p in unimplemented_plans),
                'total_items': sum(p['total_count'] for p in unimplemented_plans),
                'overall_completion': sum(p['completion_percentage'] for p in unimplemented_plans) / len(unimplemented_plans) if unimplemented_plans else 0
            }
        }
    
    def create_plan(self, title: str, content: str) -> Path:
        """Create a new plan file."""
        # Generate filename from title
        filename = re.sub(r'[^a-zA-Z0-9\s-]', '', title.lower())
        filename = re.sub(r'\s+', '-', filename)
        filename = f"{filename}.md"
        
        file_path = self.unimplemented_dir / filename
        
        # Add metadata
        full_content = f"""# {title}

{content}

---

**Created:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**Status:** Unimplemented
"""
        
        file_path.write_text(full_content, encoding='utf-8')
        logger.info(f"Created new plan: {title}")
        
        return file_path

# Global plan manager instance
plan_manager = PlanManager()

def main():
    """Main function for command-line usage."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Manage service station operation plans")
    parser.add_argument("--check", action="store_true", help="Check and promote completed plans")
    parser.add_argument("--status", action="store_true", help="Show plan status summary")
    parser.add_argument("--list", action="store_true", help="List all plans")
    
    args = parser.parse_args()
    
    if args.check:
        promoted = plan_manager.check_and_promote_plans()
        if promoted:
            print(f"Promoted {len(promoted)} plans to implemented:")
            for plan in promoted:
                print(f"  - {plan['title']}")
        else:
            print("No plans ready for promotion")
    
    if args.status:
        summary = plan_manager.get_plan_status_summary()
        print(f"Plan Status Summary:")
        print(f"  Unimplemented: {summary['unimplemented_count']}")
        print(f"  Implemented: {summary['implemented_count']}")
        print(f"  Total: {summary['total_count']}")
        print(f"  Overall completion: {summary['completion_stats']['overall_completion']:.1f}%")
    
    if args.list:
        print("Unimplemented plans:")
        for plan in plan_manager.get_unimplemented_plans():
            plan_data = plan_manager.parse_plan_file(plan)
            print(f"  - {plan_data['title']} ({plan_data['completed_count']}/{plan_data['total_count']} complete)")
        
        print("\nImplemented plans:")
        for plan in plan_manager.get_implemented_plans():
            plan_data = plan_manager.parse_plan_file(plan)
            print(f"  - {plan_data['title']}")

if __name__ == "__main__":
    main() 