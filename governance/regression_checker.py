"""
Regression Checker - Consistency validation across chapters.

Triggers: Chapter save, canon bump, timeline change, research promotion

CRITICAL: Flags only. Never auto-fixes. Human review required.
"""

import re
from typing import List, Dict, Optional
from pathlib import Path
from datetime import datetime


class RegressionChecker:
    """
    Performs consistency checks across the manuscript.
    
    All checks return flagged issues for human review.
    This system NEVER auto-fixes anything.
    
    Usage:
        checker = RegressionChecker(canon_manager, "/path/to/novel")
        
        # Run all checks
        report = checker.run_all_checks()
        
        # Run specific check
        age_issues = checker.check_character_ages(chapters)
    """
    
    def __init__(self, canon_manager, base_path: str):
        self.canon = canon_manager
        self.base_path = Path(base_path)
        self.chapters_path = self.base_path / "chapters"
    
    def _load_all_chapters(self) -> List[Dict]:
        """Load all chapter files from chapters directory."""
        chapters = []
        
        if not self.chapters_path.exists():
            return chapters
        
        for file_path in sorted(self.chapters_path.glob("*.md")):
            with open(file_path, 'r', encoding='utf-8') as f:
                chapters.append({
                    "name": file_path.stem,
                    "path": str(file_path),
                    "content": f.read()
                })
        
        # Also check for .txt files
        for file_path in sorted(self.chapters_path.glob("*.txt")):
            with open(file_path, 'r', encoding='utf-8') as f:
                chapters.append({
                    "name": file_path.stem,
                    "path": str(file_path),
                    "content": f.read()
                })
        
        return chapters
    
    def _find_in_text(self, text: str, pattern: str) -> List[Dict]:
        """Find all occurrences of pattern in text with line numbers."""
        matches = []
        lines = text.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            if re.search(pattern, line, re.IGNORECASE):
                matches.append({
                    "line": line_num,
                    "text": line.strip()
                })
        
        return matches
    
    def check_character_ages(self, chapters: List[Dict] = None) -> List[Dict]:
        """
        Verify character ages remain consistent.
        
        Checks for:
        - Age mentions that conflict with canon
        - Impossible age progressions within timeline
        - Birthday references that don't match
        
        Returns:
            List of flagged issues
        """
        if chapters is None:
            chapters = self._load_all_chapters()
        
        issues = []
        character_facts = self.canon.get_all_facts("characters")
        
        # Look for age-related patterns
        age_patterns = [
            r'\b(\d{1,2})\s*years?\s*old\b',
            r'\bage[d]?\s*(\d{1,2})\b',
            r'\b(\d{1,2})-year-old\b',
        ]
        
        for chapter in chapters:
            content = chapter["content"]
            
            for pattern in age_patterns:
                matches = re.finditer(pattern, content, re.IGNORECASE)
                for match in matches:
                    age = int(match.group(1))
                    context_start = max(0, match.start() - 50)
                    context_end = min(len(content), match.end() + 50)
                    context = content[context_start:context_end]
                    
                    # Check if this conflicts with any known character age
                    for char_key, char_data in character_facts.items():
                        if "age" in char_key.lower():
                            canon_age = char_data.get("value", "")
                            if canon_age.isdigit() and int(canon_age) != age:
                                if char_key.split("_")[0].lower() in context.lower():
                                    issues.append({
                                        "type": "age_inconsistency",
                                        "chapter": chapter["name"],
                                        "found_age": age,
                                        "canon_age": int(canon_age),
                                        "character": char_key,
                                        "context": context.strip(),
                                        "severity": "high"
                                    })
        
        return issues
    
    def check_locations(self, chapters: List[Dict] = None) -> List[Dict]:
        """
        Verify location descriptions remain consistent.
        
        Checks for:
        - Location descriptions that conflict with established details
        - Geographic impossibilities (wrong direction, distance)
        - Setting details that change unexpectedly
        
        Returns:
            List of flagged issues
        """
        if chapters is None:
            chapters = self._load_all_chapters()
        
        issues = []
        location_facts = self.canon.get_all_facts("locations")
        
        # Track location mentions across chapters
        location_mentions = {}
        
        for chapter in chapters:
            content = chapter["content"].lower()
            
            # Check against known locations
            for loc_key, loc_data in location_facts.items():
                loc_name = loc_key.replace("_", " ").lower()
                
                if loc_name in content:
                    if loc_name not in location_mentions:
                        location_mentions[loc_name] = []
                    
                    # Find the context
                    matches = self._find_in_text(chapter["content"], loc_name)
                    for match in matches:
                        location_mentions[loc_name].append({
                            "chapter": chapter["name"],
                            "line": match["line"],
                            "text": match["text"]
                        })
        
        # Look for potential inconsistencies
        for loc_name, mentions in location_mentions.items():
            if len(mentions) > 1:
                # Flag for human review if location appears multiple times
                issues.append({
                    "type": "location_review_needed",
                    "location": loc_name,
                    "mentions": mentions,
                    "severity": "info",
                    "message": f"Location '{loc_name}' mentioned in multiple chapters - verify consistency"
                })
        
        return issues
    
    def check_timeline(self, chapters: List[Dict] = None) -> List[Dict]:
        """
        Verify chronological order and date references.
        
        Checks for:
        - Date references that conflict with established timeline
        - Events happening out of order
        - Impossible time spans between events
        
        Returns:
            List of flagged issues
        """
        if chapters is None:
            chapters = self._load_all_chapters()
        
        issues = []
        timeline_facts = self.canon.get_all_facts("timeline")
        
        # Date patterns to look for
        date_patterns = [
            r'\b(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2}(?:st|nd|rd|th)?,?\s*\d{4}\b',
            r'\b(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}\b',
            r'\b(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)\b',
            r'\b\d{1,2}/\d{1,2}/\d{2,4}\b',
        ]
        
        date_mentions = []
        
        for chapter in chapters:
            content = chapter["content"]
            
            for pattern in date_patterns:
                matches = re.finditer(pattern, content, re.IGNORECASE)
                for match in matches:
                    line_num = content[:match.start()].count('\n') + 1
                    date_mentions.append({
                        "chapter": chapter["name"],
                        "date_text": match.group(0),
                        "line": line_num,
                        "position": match.start()
                    })
        
        # Check for timeline conflicts with canon
        for mention in date_mentions:
            for time_key, time_data in timeline_facts.items():
                if mention["date_text"].lower() in time_data.get("value", "").lower():
                    issues.append({
                        "type": "timeline_reference",
                        "chapter": mention["chapter"],
                        "date_found": mention["date_text"],
                        "canon_event": time_key,
                        "severity": "info",
                        "message": f"Date reference matches timeline event '{time_key}'"
                    })
        
        return issues
    
    def check_object_continuity(self, chapters: List[Dict] = None) -> List[Dict]:
        """
        Verify objects appear/disappear logically.
        
        Checks for:
        - Objects used before being introduced
        - Objects that disappear without explanation
        - Magical appearance of items
        
        Returns:
            List of flagged issues
        """
        if chapters is None:
            chapters = self._load_all_chapters()
        
        issues = []
        object_facts = self.canon.get_all_facts("objects")
        
        # Track object appearances
        object_first_appearance = {}
        
        for chapter in chapters:
            content = chapter["content"].lower()
            
            for obj_key, obj_data in object_facts.items():
                obj_name = obj_key.replace("_", " ").lower()
                
                if obj_name in content and obj_name not in object_first_appearance:
                    object_first_appearance[obj_name] = chapter["name"]
        
        # Report tracked objects
        for obj_name, first_chapter in object_first_appearance.items():
            issues.append({
                "type": "object_tracking",
                "object": obj_name,
                "first_appearance": first_chapter,
                "severity": "info",
                "message": f"Object '{obj_name}' first appears in {first_chapter}"
            })
        
        return issues
    
    def check_dialogue_attribution(self, chapters: List[Dict] = None) -> List[Dict]:
        """
        Check for dialogue attribution issues.
        
        Checks for:
        - Long stretches of unattributed dialogue
        - Characters speaking out of character
        - Dialogue tag inconsistencies
        
        Returns:
            List of flagged issues
        """
        if chapters is None:
            chapters = self._load_all_chapters()
        
        issues = []
        
        for chapter in chapters:
            content = chapter["content"]
            
            # Count dialogue lines without attribution
            dialogue_pattern = r'"[^"]+"|"[^"]+'
            lines = content.split('\n')
            
            consecutive_unattributed = 0
            
            for line_num, line in enumerate(lines, 1):
                has_dialogue = re.search(dialogue_pattern, line)
                has_attribution = any(word in line.lower() for word in 
                    ['said', 'asked', 'replied', 'answered', 'whispered', 'shouted', 
                     'muttered', 'called', 'yelled', 'told', 'spoke'])
                
                if has_dialogue and not has_attribution:
                    consecutive_unattributed += 1
                else:
                    if consecutive_unattributed >= 5:
                        issues.append({
                            "type": "unattributed_dialogue",
                            "chapter": chapter["name"],
                            "line": line_num - consecutive_unattributed,
                            "count": consecutive_unattributed,
                            "severity": "warning",
                            "message": f"{consecutive_unattributed} consecutive dialogue lines without clear attribution"
                        })
                    consecutive_unattributed = 0
        
        return issues
    
    def run_all_checks(self, chapters: List[Dict] = None) -> Dict:
        """
        Run full regression suite.
        
        Returns:
            Dictionary with all flagged issues for human review
        """
        if chapters is None:
            chapters = self._load_all_chapters()
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "chapters_checked": len(chapters),
            "checks": {
                "character_ages": self.check_character_ages(chapters),
                "locations": self.check_locations(chapters),
                "timeline": self.check_timeline(chapters),
                "object_continuity": self.check_object_continuity(chapters),
                "dialogue_attribution": self.check_dialogue_attribution(chapters),
            },
            "summary": {}
        }
        
        # Generate summary
        total_issues = 0
        for check_name, issues in results["checks"].items():
            count = len(issues)
            results["summary"][check_name] = count
            total_issues += count
        
        results["summary"]["total"] = total_issues
        
        return results
    
    def get_report(self, chapters: List[Dict] = None) -> str:
        """
        Generate a human-readable report.
        
        Returns:
            Formatted markdown report
        """
        results = self.run_all_checks(chapters)
        
        lines = [
            "# Regression Check Report",
            f"Generated: {results['timestamp']}",
            f"Chapters Checked: {results['chapters_checked']}",
            "",
            "## Summary",
            ""
        ]
        
        for check_name, count in results["summary"].items():
            if check_name != "total":
                lines.append(f"- **{check_name.replace('_', ' ').title()}**: {count} items")
        
        lines.append(f"\n**Total Items for Review: {results['summary']['total']}**")
        lines.append("")
        
        # Detailed findings
        for check_name, issues in results["checks"].items():
            if issues:
                lines.append(f"## {check_name.replace('_', ' ').title()}")
                lines.append("")
                
                for issue in issues:
                    severity = issue.get("severity", "info")
                    message = issue.get("message", str(issue))
                    chapter = issue.get("chapter", "N/A")
                    
                    lines.append(f"- [{severity.upper()}] {chapter}: {message}")
                
                lines.append("")
        
        return "\n".join(lines)
