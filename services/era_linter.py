"""
Era Language Linter - Detects anachronistic language.

Scans text for modern language that breaks the 1950s voice.
Provides suggestions for period-appropriate alternatives.
"""

import re
from typing import List, Dict, Tuple
from pathlib import Path


class EraLinter:
    """
    Scans text for modern language that breaks 1950s voice.
    
    Usage:
        linter = EraLinter()
        
        # Lint a chapter
        issues = linter.lint(chapter_text)
        
        # Get summary
        summary = linter.get_summary(issues)
        
        # Suggest alternatives
        alt = linter.suggest_alternative("stressed")
    """
    
    # Prohibited terms organized by category
    PROHIBITED = {
        "therapy_speak": [
            "trauma", "traumatic", "traumatized",
            "triggered", "triggering", "trigger warning",
            "processing", "process my feelings",
            "boundaries", "boundary", "set boundaries",
            "toxic", "toxicity", "toxic relationship",
            "gaslighting", "gaslight", "gaslighter",
            "codependent", "codependency",
            "enable", "enabler", "enabling behavior",
            "closure", "need closure", "get closure",
            "validate", "validation", "feel validated",
            "self-care", "self care",
            "safe space",
            "mindful", "mindfulness", "mindfully",
            "empower", "empowered", "empowerment",
            "unpack", "unpack that",
            "healing journey",
            "inner child",
            "coping mechanism",
            "red flag", "red flags",
            "narcissist", "narcissistic",
            "anxiety", "anxious",  # modern clinical usage
            "depression", "depressed",  # modern clinical usage
            "mental health",
            "therapy", "therapist",  # in modern sense
            "support system",
            "emotional labor",
            "lived experience",
        ],
        
        "corporate_jargon": [
            "leverage", "leveraging",
            "synergy", "synergize", "synergistic",
            "circle back",
            "pivot", "pivoting",
            "bandwidth", "no bandwidth",
            "stakeholder", "stakeholders",
            "deliverable", "deliverables",
            "optimize", "optimization", "optimizing",
            "proactive", "proactively",
            "scalable", "scale up",
            "paradigm", "paradigm shift",
            "actionable", "action items",
            "core competency",
            "best practices",
            "value proposition",
            "move the needle",
            "low-hanging fruit",
            "drill down",
            "take offline",
            "loop in",
            "on my radar",
            "unpack this",
            "double-click on",
            "align", "alignment",
            "optics",
            "bandwidth",
            "ecosystem",
        ],
        
        "contemporary_slang": [
            "24/7", "twenty-four seven",
            "bottom line",
            "at the end of the day",
            "game-changer", "game changer",
            "no-brainer", "no brainer",
            "deep dive",
            "moving forward",
            "reach out", "reaching out",
            "heads up", "heads-up",
            "touch base",
            "ballpark", "in the ballpark",
            "pushback", "push back",
            "reality check",
            "wake-up call",
            "on the same page",
            "think outside the box",
            "take it to the next level",
            "win-win",
            "100 percent", "one hundred percent",  # as agreement
            "absolutely",  # as emphatic yes
            "basically",
            "literally",  # emphatic usage
            "like",  # as filler
            "totally",
            "awesome",
            "amazing",
            "super",  # as intensifier
            "lifestyle",
            "networking",
            "multi-tasking", "multitasking",
            "downtime",
            "feedback",  # modern usage
        ],
        
        "technology_anachronisms": [
            "computer", "computers",  # rare in 1954
            "television",  # existed but not widespread
            "jet",  # commercial jets rare
            "atomic",  # except in specific contexts
            "satellite",
            "transistor",  # cutting edge in 1954
            "electronic",
            "automatic",  # some uses okay
            "plastic",  # common by 1954 but watch usage
        ],
    }
    
    # Period-accurate alternatives
    ALTERNATIVES = {
        # Emotional states
        "stressed": ["wound up", "wound tight", "on edge", "worked up", "keyed up"],
        "anxious": ["nervy", "jumpy", "jittery", "on edge", "uneasy"],
        "depressed": ["low", "blue", "down", "in the dumps", "feeling low"],
        "upset": ["rattled", "shaken", "put out", "sore"],
        "angry": ["sore", "steamed", "burned up", "hot under the collar"],
        "happy": ["pleased", "glad", "tickled", "in good spirits"],
        "scared": ["spooked", "rattled", "shook up"],
        
        # Relationships
        "relationship": ["situation", "arrangement", "understanding", "what we have"],
        "dating": ["going steady", "stepping out", "keeping company", "courting"],
        "boyfriend": ["fellow", "beau", "steady"],
        "girlfriend": ["girl", "steady", "sweetheart"],
        
        # General terms
        "issue": ["trouble", "problem", "matter", "concern"],
        "problem": ["trouble", "difficulty", "matter"],
        "situation": ["fix", "spot", "pickle", "jam"],
        "really": ["mighty", "awful", "plenty", "sure"],
        "very": ["mighty", "awful", "right", "plenty"],
        "great": ["swell", "grand", "fine", "first-rate"],
        "bad": ["rough", "tough", "no good"],
        "good": ["fine", "swell", "jake", "all right"],
        "okay": ["jake", "all right", "fine", "swell"],
        "yes": ["sure", "you bet", "all right"],
        "no": ["nope", "nothing doing", "no dice"],
        
        # Actions
        "talk": ["have a word", "chew the fat", "jaw"],
        "understand": ["get it", "follow", "savvy"],
        "leave": ["blow", "scram", "take off", "vamoose"],
        "hurry": ["step on it", "shake a leg", "get a move on"],
        
        # Money
        "money": ["dough", "bread", "scratch", "cabbage"],
        "expensive": ["steep", "pricey", "costs plenty"],
        "cheap": ["two-bit", "nickel-and-dime"],
        
        # People
        "person": ["fellow", "character", "customer"],
        "man": ["fellow", "guy", "joe"],
        "woman": ["gal", "dame", "lady"],
        "friend": ["pal", "buddy", "chum"],
    }
    
    def __init__(self, style_charter_path: str = None):
        """
        Initialize the linter.
        
        Args:
            style_charter_path: Optional path to style charter for custom rules
        """
        self.style_charter_path = style_charter_path
        self._compile_patterns()
    
    def _compile_patterns(self):
        """Compile regex patterns for efficient matching."""
        self.patterns = {}
        
        for category, terms in self.PROHIBITED.items():
            # Create word-boundary pattern for each term
            patterns = []
            for term in terms:
                # Escape special regex characters
                escaped = re.escape(term)
                # Add word boundaries
                patterns.append(rf'\b{escaped}\b')
            
            # Combine into single pattern
            self.patterns[category] = re.compile('|'.join(patterns), re.IGNORECASE)
    
    def lint(self, text: str) -> List[Dict]:
        """
        Scan text for anachronisms.
        
        Args:
            text: The text to lint
            
        Returns:
            List of flagged terms with line numbers and suggestions
        """
        issues = []
        lines = text.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            for category, pattern in self.patterns.items():
                matches = pattern.finditer(line)
                
                for match in matches:
                    term = match.group(0)
                    
                    # Get context (surrounding words)
                    start = max(0, match.start() - 30)
                    end = min(len(line), match.end() + 30)
                    context = line[start:end].strip()
                    
                    issues.append({
                        "line": line_num,
                        "column": match.start() + 1,
                        "term": term,
                        "category": category,
                        "context": f"...{context}...",
                        "suggestion": self.suggest_alternative(term.lower()),
                        "severity": self._get_severity(category)
                    })
        
        return issues
    
    def _get_severity(self, category: str) -> str:
        """Get severity level for a category."""
        severity_map = {
            "therapy_speak": "high",
            "corporate_jargon": "high",
            "contemporary_slang": "medium",
            "technology_anachronisms": "low"  # context-dependent
        }
        return severity_map.get(category, "medium")
    
    def suggest_alternative(self, term: str) -> str:
        """
        Get period-appropriate alternative for a term.
        
        Args:
            term: The anachronistic term
            
        Returns:
            Suggestion string with alternatives
        """
        term_lower = term.lower()
        
        # Check direct matches
        if term_lower in self.ALTERNATIVES:
            alts = self.ALTERNATIVES[term_lower]
            return f"Consider: {', '.join(alts)}"
        
        # Check partial matches
        for key, alts in self.ALTERNATIVES.items():
            if key in term_lower or term_lower in key:
                return f"Consider: {', '.join(alts)}"
        
        return "Rephrase in period voice (1950s)"
    
    def get_summary(self, issues: List[Dict]) -> Dict:
        """
        Generate summary of lint results.
        
        Args:
            issues: List of issues from lint()
            
        Returns:
            Summary statistics
        """
        if not issues:
            return {
                "total": 0,
                "by_category": {},
                "by_severity": {},
                "verdict": "CLEAN - No anachronisms detected"
            }
        
        by_category = {}
        by_severity = {}
        
        for issue in issues:
            cat = issue["category"]
            sev = issue["severity"]
            
            by_category[cat] = by_category.get(cat, 0) + 1
            by_severity[sev] = by_severity.get(sev, 0) + 1
        
        # Determine verdict
        high_count = by_severity.get("high", 0)
        if high_count > 5:
            verdict = "NEEDS WORK - Multiple high-severity anachronisms"
        elif high_count > 0:
            verdict = "REVIEW - Some high-severity anachronisms found"
        elif issues:
            verdict = "MINOR - Low-severity issues only"
        else:
            verdict = "CLEAN"
        
        return {
            "total": len(issues),
            "by_category": by_category,
            "by_severity": by_severity,
            "verdict": verdict
        }
    
    def get_report(self, text: str) -> str:
        """
        Generate full lint report as markdown.
        
        Args:
            text: The text to lint
            
        Returns:
            Formatted markdown report
        """
        issues = self.lint(text)
        summary = self.get_summary(issues)
        
        lines = [
            "# Era Language Lint Report",
            "",
            f"**Verdict:** {summary['verdict']}",
            f"**Total Issues:** {summary['total']}",
            "",
        ]
        
        if summary["by_category"]:
            lines.append("## By Category")
            for cat, count in summary["by_category"].items():
                lines.append(f"- {cat.replace('_', ' ').title()}: {count}")
            lines.append("")
        
        if summary["by_severity"]:
            lines.append("## By Severity")
            for sev, count in summary["by_severity"].items():
                lines.append(f"- {sev.title()}: {count}")
            lines.append("")
        
        if issues:
            lines.append("## Detailed Issues")
            lines.append("")
            
            # Group by line
            current_line = None
            for issue in sorted(issues, key=lambda x: x["line"]):
                if issue["line"] != current_line:
                    current_line = issue["line"]
                    lines.append(f"### Line {current_line}")
                
                lines.append(
                    f"- **{issue['term']}** ({issue['category']}, {issue['severity']})\n"
                    f"  Context: `{issue['context']}`\n"
                    f"  {issue['suggestion']}"
                )
            lines.append("")
        
        return "\n".join(lines)
    
    def lint_file(self, file_path: str) -> Tuple[List[Dict], Dict]:
        """
        Lint a file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Tuple of (issues list, summary dict)
        """
        path = Path(file_path)
        text = path.read_text(encoding='utf-8')
        
        issues = self.lint(text)
        summary = self.get_summary(issues)
        
        return issues, summary
