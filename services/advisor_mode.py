"""
AI Advisor Mode - Proactive editorial suggestions.

CRITICAL: This is NOT a co-writer. This is an editorial advisor.
Outputs guidance only, NEVER prose.
"""

from typing import Dict, List, Optional
from pathlib import Path
from datetime import datetime


class AdvisorMode:
    """
    Provides proactive suggestions without writing prose.
    
    Trigger Conditions:
    - Manual button press ("Run Advisor")
    - End of chapter editing session
    - Scheduled periodic review
    
    IMPORTANT: This system provides GUIDANCE ONLY.
    It should never generate prose or rewrite content.
    
    Usage:
        advisor = AdvisorMode(model_router, canon_manager, era_linter)
        
        # Analyze single chapter
        analysis = advisor.analyze_chapter(chapter_text, "Chapter 5")
        
        # Get recommendations across manuscript
        recs = advisor.get_recommendations(all_chapters)
    """
    
    def __init__(self, model_router, canon_manager, era_linter):
        """
        Initialize advisor.
        
        Args:
            model_router: ModelRouter instance
            canon_manager: CanonManager instance
            era_linter: EraLinter instance
        """
        self.router = model_router
        self.canon = canon_manager
        self.linter = era_linter
        
        # Theme tracking definitions
        self.character_arcs = {
            "tommy": {
                "arc": "Complicity → moral awakening → consequences",
                "keywords": ["silent", "witness", "guilt", "complicit", "knew", "said nothing"],
                "progression_markers": ["ignored", "questioned", "confronted", "acted"]
            },
            "jenny": {
                "arc": "Desire → agency → trapped choices",
                "keywords": ["want", "choose", "trapped", "freedom", "escape"],
                "progression_markers": ["dreamed", "planned", "attempted", "accepted"]
            },
            "rafael": {
                "arc": "Dignity → sacrifice → tragedy",
                "keywords": ["pride", "dignity", "sacrifice", "protect", "honor"],
                "progression_markers": ["endured", "protected", "gave", "lost"]
            }
        }
    
    def analyze_chapter(self, chapter_text: str, chapter_name: str) -> Dict:
        """
        Full chapter analysis.
        
        Returns guidance only, never prose.
        
        Args:
            chapter_text: The chapter content
            chapter_name: Name/identifier for the chapter
            
        Returns:
            Analysis results with actionable guidance
        """
        results = {
            "chapter": chapter_name,
            "analyzed_at": datetime.now().isoformat(),
            "word_count": len(chapter_text.split()),
            "analyses": {}
        }
        
        # Run all analyses
        results["analyses"]["revision_priority"] = self._calculate_revision_priority(chapter_text)
        results["analyses"]["tension_analysis"] = self._analyze_tension(chapter_text)
        results["analyses"]["theme_tracking"] = self._track_themes(chapter_text)
        results["analyses"]["era_violations"] = self.linter.lint(chapter_text)
        results["analyses"]["era_summary"] = self.linter.get_summary(results["analyses"]["era_violations"])
        
        # Canon validation if available
        if self.canon:
            results["analyses"]["canon_conflicts"] = self.canon.validate_against_canon(chapter_text)
        
        # Calculate overall health score
        results["health_score"] = self._calculate_health_score(results["analyses"])
        results["top_priorities"] = self._get_top_priorities(results["analyses"])
        
        return results
    
    def _calculate_revision_priority(self, text: str) -> Dict:
        """
        What to revise next - prioritized recommendations.
        
        Evaluates:
        - Sentence variety
        - Dialogue/prose balance
        - Paragraph length variation
        - Opening hook strength
        - Ending resonance
        """
        lines = text.split('\n')
        paragraphs = [p for p in text.split('\n\n') if p.strip()]
        sentences = [s.strip() for s in text.replace('\n', ' ').split('.') if s.strip()]
        
        analysis = {
            "priority_areas": [],
            "metrics": {}
        }
        
        # Check sentence length variation
        if sentences:
            lengths = [len(s.split()) for s in sentences]
            avg_length = sum(lengths) / len(lengths)
            length_variance = sum((l - avg_length) ** 2 for l in lengths) / len(lengths)
            
            analysis["metrics"]["avg_sentence_length"] = round(avg_length, 1)
            analysis["metrics"]["sentence_variance"] = round(length_variance, 1)
            
            if length_variance < 20:
                analysis["priority_areas"].append({
                    "area": "sentence_variety",
                    "priority": "medium",
                    "guidance": "Sentences have similar lengths. Vary rhythm with short punchy sentences and longer flowing ones."
                })
        
        # Check dialogue balance
        dialogue_count = text.count('"')
        if dialogue_count < 4:
            analysis["priority_areas"].append({
                "area": "dialogue",
                "priority": "low",
                "guidance": "Light on dialogue. Consider adding character interaction."
            })
        
        # Check paragraph length
        if paragraphs:
            para_lengths = [len(p.split()) for p in paragraphs]
            long_paras = sum(1 for l in para_lengths if l > 150)
            
            if long_paras > len(paragraphs) * 0.3:
                analysis["priority_areas"].append({
                    "area": "paragraph_length",
                    "priority": "medium",
                    "guidance": "Several long paragraphs. Break up for better pacing."
                })
        
        # Check opening
        first_para = paragraphs[0] if paragraphs else ""
        if len(first_para.split()) > 100:
            analysis["priority_areas"].append({
                "area": "opening",
                "priority": "high",
                "guidance": "Opening paragraph is dense. Consider a sharper hook."
            })
        
        return analysis
    
    def _analyze_tension(self, text: str) -> List[Dict]:
        """
        Where tension drops - specific scenes flagged.
        
        Looks for:
        - Long descriptive passages without action
        - Excessive introspection
        - Missing stakes
        - Resolution without buildup
        """
        issues = []
        paragraphs = [p for p in text.split('\n\n') if p.strip()]
        
        # Tension indicators
        tension_words = ['but', 'however', 'suddenly', 'fear', 'danger', 'risk', 
                        'must', 'need', 'desperate', 'urgent', 'quick', 'hurry']
        action_verbs = ['ran', 'grabbed', 'shouted', 'jumped', 'threw', 'pushed',
                       'pulled', 'fought', 'struck', 'fled']
        
        for i, para in enumerate(paragraphs):
            para_lower = para.lower()
            
            # Check for tension words
            tension_count = sum(1 for word in tension_words if word in para_lower)
            action_count = sum(1 for verb in action_verbs if verb in para_lower)
            
            # Long paragraph with no tension
            word_count = len(para.split())
            if word_count > 100 and tension_count == 0 and action_count == 0:
                issues.append({
                    "paragraph": i + 1,
                    "type": "low_tension",
                    "word_count": word_count,
                    "guidance": "Long passage with low tension. Consider adding conflict or stakes.",
                    "preview": para[:100] + "..."
                })
            
            # Excessive introspection check (lots of "I thought", "I felt", etc.)
            introspection = para_lower.count(' thought') + para_lower.count(' felt') + \
                           para_lower.count(' wondered') + para_lower.count(' realized')
            
            if introspection > 3:
                issues.append({
                    "paragraph": i + 1,
                    "type": "excessive_introspection",
                    "count": introspection,
                    "guidance": "Heavy on internal thought. Show through action instead."
                })
        
        return issues
    
    def _track_themes(self, text: str) -> Dict:
        """
        Theme tracking - where thematic elements appear.
        
        Tracks:
        - Tommy: Complicity → moral awakening → consequences
        - Jenny: Desire → agency → trapped choices
        - Rafael: Dignity → sacrifice → tragedy
        """
        text_lower = text.lower()
        
        theme_analysis = {
            "characters": {},
            "overall_themes": {
                "silence_complicity": 0,
                "dignity_exploitation": 0,
                "love_sacrifice": 0,
                "escape_freedom": 0
            }
        }
        
        # Check each character arc
        for char_name, arc_data in self.character_arcs.items():
            char_analysis = {
                "arc": arc_data["arc"],
                "keyword_hits": 0,
                "progression_markers_found": [],
                "presence_score": 0
            }
            
            # Count keyword hits
            for keyword in arc_data["keywords"]:
                count = text_lower.count(keyword)
                char_analysis["keyword_hits"] += count
            
            # Check progression markers
            for marker in arc_data["progression_markers"]:
                if marker in text_lower:
                    char_analysis["progression_markers_found"].append(marker)
            
            # Calculate presence score (0-100)
            char_analysis["presence_score"] = min(100, char_analysis["keyword_hits"] * 10 + 
                                                  len(char_analysis["progression_markers_found"]) * 15)
            
            theme_analysis["characters"][char_name] = char_analysis
        
        # Track overall themes
        silence_words = ["silent", "silence", "quiet", "unsaid", "unspoken", "secret"]
        dignity_words = ["dignity", "pride", "respect", "worth", "honor"]
        love_words = ["love", "heart", "care", "protect", "together"]
        escape_words = ["escape", "free", "freedom", "away", "leave", "run"]
        
        for word in silence_words:
            theme_analysis["overall_themes"]["silence_complicity"] += text_lower.count(word)
        for word in dignity_words:
            theme_analysis["overall_themes"]["dignity_exploitation"] += text_lower.count(word)
        for word in love_words:
            theme_analysis["overall_themes"]["love_sacrifice"] += text_lower.count(word)
        for word in escape_words:
            theme_analysis["overall_themes"]["escape_freedom"] += text_lower.count(word)
        
        return theme_analysis
    
    def _check_historical_accuracy(self, text: str) -> List[Dict]:
        """
        Historical accuracy issues - delegates to era linter.
        """
        return self.linter.lint(text)
    
    def _calculate_health_score(self, analyses: Dict) -> Dict:
        """Calculate overall chapter health score."""
        score = 100
        issues = []
        
        # Deduct for era violations
        era_summary = analyses.get("era_summary", {})
        era_high = era_summary.get("by_severity", {}).get("high", 0)
        era_medium = era_summary.get("by_severity", {}).get("medium", 0)
        
        score -= era_high * 5
        score -= era_medium * 2
        
        if era_high > 0:
            issues.append(f"{era_high} high-severity anachronisms")
        
        # Deduct for tension issues
        tension_issues = len(analyses.get("tension_analysis", []))
        score -= tension_issues * 3
        
        if tension_issues > 0:
            issues.append(f"{tension_issues} tension/pacing issues")
        
        # Deduct for canon conflicts
        canon_conflicts = len(analyses.get("canon_conflicts", []))
        score -= canon_conflicts * 10
        
        if canon_conflicts > 0:
            issues.append(f"{canon_conflicts} potential canon conflicts")
        
        # Cap at 0
        score = max(0, score)
        
        # Determine grade
        if score >= 90:
            grade = "A"
        elif score >= 80:
            grade = "B"
        elif score >= 70:
            grade = "C"
        elif score >= 60:
            grade = "D"
        else:
            grade = "F"
        
        return {
            "score": score,
            "grade": grade,
            "issues": issues
        }
    
    def _get_top_priorities(self, analyses: Dict) -> List[Dict]:
        """Get top 3 priorities for revision."""
        priorities = []
        
        # High-severity era violations first
        era_summary = analyses.get("era_summary", {})
        if era_summary.get("by_severity", {}).get("high", 0) > 0:
            priorities.append({
                "priority": 1,
                "area": "Language",
                "issue": "High-severity anachronisms detected",
                "action": "Review and replace modern language with period alternatives"
            })
        
        # Canon conflicts
        if analyses.get("canon_conflicts"):
            priorities.append({
                "priority": 2,
                "area": "Consistency",
                "issue": "Potential conflicts with established canon",
                "action": "Verify facts against canon reference"
            })
        
        # Tension issues
        tension = analyses.get("tension_analysis", [])
        if tension:
            priorities.append({
                "priority": 3,
                "area": "Pacing",
                "issue": f"{len(tension)} sections with low tension",
                "action": "Add conflict, stakes, or forward motion"
            })
        
        return priorities[:3]
    
    def get_recommendations(self, chapters: List[Dict]) -> List[Dict]:
        """
        Get prioritized recommendations across all chapters.
        
        Args:
            chapters: List of {"name": str, "content": str}
            
        Returns:
            Prioritized list of recommendations
        """
        all_analyses = []
        
        for chapter in chapters:
            analysis = self.analyze_chapter(chapter["content"], chapter["name"])
            all_analyses.append(analysis)
        
        # Sort by health score (lowest first = needs most work)
        all_analyses.sort(key=lambda x: x["health_score"]["score"])
        
        recommendations = []
        
        for analysis in all_analyses:
            if analysis["health_score"]["score"] < 80:
                recommendations.append({
                    "chapter": analysis["chapter"],
                    "health_score": analysis["health_score"]["score"],
                    "grade": analysis["health_score"]["grade"],
                    "priorities": analysis["top_priorities"],
                    "era_issues": analysis["analyses"]["era_summary"].get("total", 0)
                })
        
        return recommendations
    
    def get_report(self, chapter_text: str, chapter_name: str) -> str:
        """
        Generate full advisory report as markdown.
        
        Args:
            chapter_text: The chapter content
            chapter_name: Name of the chapter
            
        Returns:
            Formatted markdown report
        """
        analysis = self.analyze_chapter(chapter_text, chapter_name)
        
        lines = [
            f"# Advisory Report: {chapter_name}",
            f"Generated: {analysis['analyzed_at']}",
            "",
            f"## Health Score: {analysis['health_score']['score']}/100 ({analysis['health_score']['grade']})",
            "",
        ]
        
        if analysis["health_score"]["issues"]:
            lines.append("### Issues Affecting Score")
            for issue in analysis["health_score"]["issues"]:
                lines.append(f"- {issue}")
            lines.append("")
        
        lines.append("## Top Priorities")
        for priority in analysis["top_priorities"]:
            lines.append(f"\n### Priority {priority['priority']}: {priority['area']}")
            lines.append(f"**Issue:** {priority['issue']}")
            lines.append(f"**Action:** {priority['action']}")
        
        lines.append("\n## Era Language")
        era = analysis["analyses"]["era_summary"]
        lines.append(f"**Verdict:** {era.get('verdict', 'N/A')}")
        lines.append(f"**Total Issues:** {era.get('total', 0)}")
        
        lines.append("\n## Theme Tracking")
        themes = analysis["analyses"]["theme_tracking"]
        for char, data in themes.get("characters", {}).items():
            lines.append(f"\n### {char.title()}")
            lines.append(f"- Arc: {data['arc']}")
            lines.append(f"- Presence Score: {data['presence_score']}/100")
            if data["progression_markers_found"]:
                lines.append(f"- Markers Found: {', '.join(data['progression_markers_found'])}")
        
        lines.append("\n---")
        lines.append("*This is advisory guidance only. Human judgment required for all changes.*")
        
        return "\n".join(lines)
