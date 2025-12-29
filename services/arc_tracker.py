"""
Arc Tracker - Narrative arc tracking across chapters.

Tracks character arcs, thematic development, and story progression
to ensure coherent development throughout the manuscript.
"""

from typing import Dict, List, Optional
from pathlib import Path
from datetime import datetime
import json


class ArcTracker:
    """
    Tracks narrative arcs across the manuscript.
    
    Features:
    - Character arc progression
    - Thematic element tracking
    - Beat sheet alignment
    - Subplot tracking
    
    Usage:
        tracker = ArcTracker("/path/to/novel")
        
        # Add arc definition
        tracker.define_arc("tommy", {...})
        
        # Track chapter
        tracker.track_chapter("Chapter 1", chapter_text)
        
        # Get arc report
        report = tracker.get_arc_report("tommy")
    """
    
    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
        self.arcs_file = self.base_path / "reference" / "arcs.json"
        self.tracking_file = self.base_path / "reference" / "arc_tracking.json"
        
        self._load_data()
    
    def _load_data(self):
        """Load arc definitions and tracking data."""
        # Load arc definitions
        if self.arcs_file.exists():
            with open(self.arcs_file, 'r', encoding='utf-8') as f:
                self.arcs = json.load(f)
        else:
            self.arcs = self._create_default_arcs()
            self._save_arcs()
        
        # Load tracking data
        if self.tracking_file.exists():
            with open(self.tracking_file, 'r', encoding='utf-8') as f:
                self.tracking = json.load(f)
        else:
            self.tracking = {"chapters": {}, "last_updated": None}
            self._save_tracking()
    
    def _create_default_arcs(self) -> Dict:
        """Create default arc definitions for the novel."""
        return {
            "character_arcs": {
                "tommy": {
                    "name": "Tommy",
                    "arc_description": "Complicity → Moral Awakening → Consequences",
                    "stages": [
                        {
                            "name": "Innocence",
                            "description": "Arrives naive, focused on music career",
                            "markers": ["new", "dream", "music", "opportunity"],
                            "expected_chapters": [1, 2]
                        },
                        {
                            "name": "Witness",
                            "description": "Sees injustice, remains silent",
                            "markers": ["silent", "witness", "saw", "didn't speak"],
                            "expected_chapters": [3, 4, 5]
                        },
                        {
                            "name": "Complicity",
                            "description": "Benefits from the system",
                            "markers": ["knew", "complicit", "guilty", "wrong"],
                            "expected_chapters": [5, 6, 7]
                        },
                        {
                            "name": "Crisis",
                            "description": "Confronts moral failure",
                            "markers": ["couldn't", "must", "choice", "decide"],
                            "expected_chapters": [8, 9]
                        },
                        {
                            "name": "Action/Consequence",
                            "description": "Acts and faces results",
                            "markers": ["finally", "acted", "consequence", "cost"],
                            "expected_chapters": [10, 11, 12]
                        }
                    ]
                },
                "jenny": {
                    "name": "Jenny",
                    "arc_description": "Desire → Agency → Trapped Choices",
                    "stages": [
                        {
                            "name": "Aspiration",
                            "description": "Dreams of escape through art",
                            "markers": ["dream", "someday", "want", "fly"],
                            "expected_chapters": [1, 2, 3]
                        },
                        {
                            "name": "Connection",
                            "description": "Forms relationships (Tommy, Rafael)",
                            "markers": ["together", "understand", "feel"],
                            "expected_chapters": [3, 4, 5]
                        },
                        {
                            "name": "Agency",
                            "description": "Makes active choices",
                            "markers": ["choose", "decide", "my choice", "will"],
                            "expected_chapters": [6, 7, 8]
                        },
                        {
                            "name": "Trapped",
                            "description": "Realizes constraints",
                            "markers": ["can't", "trapped", "no choice", "cage"],
                            "expected_chapters": [8, 9, 10]
                        },
                        {
                            "name": "Resolution",
                            "description": "Accepts or breaks free",
                            "markers": ["accept", "leave", "stay", "forward"],
                            "expected_chapters": [11, 12]
                        }
                    ]
                },
                "rafael": {
                    "name": "Rafael",
                    "arc_description": "Dignity → Sacrifice → Tragedy",
                    "stages": [
                        {
                            "name": "Dignity",
                            "description": "Maintains pride despite circumstances",
                            "markers": ["pride", "dignity", "work", "respect"],
                            "expected_chapters": [2, 3, 4]
                        },
                        {
                            "name": "Protection",
                            "description": "Shields others from danger",
                            "markers": ["protect", "safe", "keep", "guard"],
                            "expected_chapters": [5, 6, 7]
                        },
                        {
                            "name": "Sacrifice",
                            "description": "Gives up self for others",
                            "markers": ["sacrifice", "give", "cost", "price"],
                            "expected_chapters": [8, 9, 10]
                        },
                        {
                            "name": "Tragedy",
                            "description": "The cost becomes clear",
                            "markers": ["lost", "gone", "never", "end"],
                            "expected_chapters": [10, 11, 12]
                        }
                    ]
                }
            },
            "thematic_arcs": {
                "silence_complicity": {
                    "name": "Silence and Complicity",
                    "description": "The cost of staying silent in face of injustice",
                    "markers": ["silent", "quiet", "said nothing", "watched", "didn't stop"],
                    "progression": ["ignorance", "awareness", "complicity", "guilt", "reckoning"]
                },
                "american_dream": {
                    "name": "American Dream",
                    "description": "Promise vs reality of opportunity",
                    "markers": ["dream", "America", "opportunity", "promise", "lie"],
                    "progression": ["hope", "pursuit", "obstacle", "disillusion", "redefine"]
                },
                "belonging": {
                    "name": "Belonging and Exclusion",
                    "description": "Who belongs, who is cast out",
                    "markers": ["belong", "outsider", "one of us", "them", "family"],
                    "progression": ["seeking", "finding", "threatened", "lost", "redefined"]
                }
            },
            "plot_beats": {
                "act_1": {
                    "name": "Setup (Chapters 1-3)",
                    "beats": ["Hook", "Establish World", "Introduce Triangle", "Inciting Incident"]
                },
                "act_2a": {
                    "name": "Confrontation Part 1 (Chapters 4-6)",
                    "beats": ["Rising Action", "Deepen Relationships", "First Major Conflict"]
                },
                "midpoint": {
                    "name": "Midpoint (Chapter 7)",
                    "beats": ["Major Revelation", "Stakes Raised", "Point of No Return"]
                },
                "act_2b": {
                    "name": "Confrontation Part 2 (Chapters 8-9)",
                    "beats": ["Complications", "Dark Night", "All Is Lost Moment"]
                },
                "act_3": {
                    "name": "Resolution (Chapters 10-12)",
                    "beats": ["Climax", "Resolution", "New Equilibrium"]
                }
            }
        }
    
    def _save_arcs(self):
        """Save arc definitions."""
        self.arcs_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.arcs_file, 'w', encoding='utf-8') as f:
            json.dump(self.arcs, f, indent=2)
    
    def _save_tracking(self):
        """Save tracking data."""
        self.tracking_file.parent.mkdir(parents=True, exist_ok=True)
        self.tracking["last_updated"] = datetime.now().isoformat()
        with open(self.tracking_file, 'w', encoding='utf-8') as f:
            json.dump(self.tracking, f, indent=2)
    
    def define_arc(self, arc_type: str, arc_id: str, definition: Dict):
        """
        Define or update an arc.
        
        Args:
            arc_type: "character_arcs", "thematic_arcs", or "plot_beats"
            arc_id: Unique identifier for the arc
            definition: Arc definition dict
        """
        if arc_type not in self.arcs:
            self.arcs[arc_type] = {}
        
        self.arcs[arc_type][arc_id] = definition
        self._save_arcs()
    
    def track_chapter(self, chapter_name: str, chapter_text: str, 
                      chapter_number: int = None) -> Dict:
        """
        Analyze and track arc elements in a chapter.
        
        Args:
            chapter_name: Name/identifier of chapter
            chapter_text: Chapter content
            chapter_number: Optional chapter number for sequence tracking
            
        Returns:
            Tracking results for this chapter
        """
        text_lower = chapter_text.lower()
        
        results = {
            "chapter": chapter_name,
            "chapter_number": chapter_number,
            "analyzed_at": datetime.now().isoformat(),
            "word_count": len(chapter_text.split()),
            "character_arcs": {},
            "thematic_arcs": {},
            "detected_beats": []
        }
        
        # Track character arcs
        for char_id, char_arc in self.arcs.get("character_arcs", {}).items():
            char_result = {
                "name": char_arc["name"],
                "stages_detected": [],
                "marker_counts": {}
            }
            
            for stage in char_arc.get("stages", []):
                stage_markers_found = []
                for marker in stage.get("markers", []):
                    count = text_lower.count(marker)
                    if count > 0:
                        stage_markers_found.append({"marker": marker, "count": count})
                        char_result["marker_counts"][marker] = count
                
                if stage_markers_found:
                    char_result["stages_detected"].append({
                        "stage": stage["name"],
                        "markers_found": stage_markers_found,
                        "expected": chapter_number in stage.get("expected_chapters", []) if chapter_number else None
                    })
            
            results["character_arcs"][char_id] = char_result
        
        # Track thematic arcs
        for theme_id, theme_arc in self.arcs.get("thematic_arcs", {}).items():
            theme_result = {
                "name": theme_arc["name"],
                "marker_hits": 0,
                "markers_found": []
            }
            
            for marker in theme_arc.get("markers", []):
                count = text_lower.count(marker)
                if count > 0:
                    theme_result["markers_found"].append({"marker": marker, "count": count})
                    theme_result["marker_hits"] += count
            
            results["thematic_arcs"][theme_id] = theme_result
        
        # Store in tracking
        self.tracking["chapters"][chapter_name] = results
        self._save_tracking()
        
        return results
    
    def get_arc_report(self, arc_id: str) -> Dict:
        """
        Get comprehensive report for a specific arc across all chapters.
        
        Args:
            arc_id: Character or theme arc ID
            
        Returns:
            Arc progression report
        """
        report = {
            "arc_id": arc_id,
            "generated_at": datetime.now().isoformat(),
            "chapters": [],
            "progression": [],
            "gaps": [],
            "recommendations": []
        }
        
        # Find arc definition
        arc_def = None
        arc_type = None
        
        if arc_id in self.arcs.get("character_arcs", {}):
            arc_def = self.arcs["character_arcs"][arc_id]
            arc_type = "character"
        elif arc_id in self.arcs.get("thematic_arcs", {}):
            arc_def = self.arcs["thematic_arcs"][arc_id]
            arc_type = "thematic"
        
        if not arc_def:
            return {"error": f"Arc not found: {arc_id}"}
        
        report["arc_name"] = arc_def.get("name")
        report["arc_description"] = arc_def.get("arc_description") or arc_def.get("description")
        report["arc_type"] = arc_type
        
        # Gather data from tracked chapters
        for chapter_name, chapter_data in self.tracking.get("chapters", {}).items():
            if arc_type == "character":
                arc_data = chapter_data.get("character_arcs", {}).get(arc_id, {})
            else:
                arc_data = chapter_data.get("thematic_arcs", {}).get(arc_id, {})
            
            if arc_data:
                report["chapters"].append({
                    "chapter": chapter_name,
                    "data": arc_data
                })
        
        # Analyze progression
        if arc_type == "character" and "stages" in arc_def:
            stages_found = set()
            for chapter in report["chapters"]:
                for stage in chapter["data"].get("stages_detected", []):
                    stages_found.add(stage["stage"])
            
            expected_stages = [s["name"] for s in arc_def["stages"]]
            report["progression"] = list(stages_found)
            report["gaps"] = [s for s in expected_stages if s not in stages_found]
            
            if report["gaps"]:
                report["recommendations"].append({
                    "type": "missing_stages",
                    "message": f"Arc stages not yet found: {', '.join(report['gaps'])}"
                })
        
        return report
    
    def get_manuscript_overview(self) -> Dict:
        """
        Get overview of all arc tracking across manuscript.
        
        Returns:
            Summary of all arcs and their status
        """
        overview = {
            "generated_at": datetime.now().isoformat(),
            "chapters_tracked": len(self.tracking.get("chapters", {})),
            "character_arcs": {},
            "thematic_arcs": {},
            "overall_health": {}
        }
        
        # Summarize each character arc
        for char_id in self.arcs.get("character_arcs", {}).keys():
            report = self.get_arc_report(char_id)
            overview["character_arcs"][char_id] = {
                "name": report.get("arc_name"),
                "stages_found": len(report.get("progression", [])),
                "stages_missing": len(report.get("gaps", [])),
                "chapters_present": len(report.get("chapters", []))
            }
        
        # Summarize each thematic arc
        for theme_id in self.arcs.get("thematic_arcs", {}).keys():
            report = self.get_arc_report(theme_id)
            total_hits = sum(
                ch["data"].get("marker_hits", 0) 
                for ch in report.get("chapters", [])
            )
            overview["thematic_arcs"][theme_id] = {
                "name": report.get("arc_name"),
                "total_marker_hits": total_hits,
                "chapters_present": len(report.get("chapters", []))
            }
        
        # Calculate overall health
        total_stages = sum(
            len(arc.get("stages", [])) 
            for arc in self.arcs.get("character_arcs", {}).values()
        )
        found_stages = sum(
            data["stages_found"] 
            for data in overview["character_arcs"].values()
        )
        
        if total_stages > 0:
            overview["overall_health"]["arc_completion"] = round(found_stages / total_stages * 100, 1)
        else:
            overview["overall_health"]["arc_completion"] = 0
        
        return overview
    
    def get_visualization_data(self) -> Dict:
        """
        Get data formatted for visualization.
        
        Returns:
            Data structure suitable for charts/graphs
        """
        chapters = sorted(
            self.tracking.get("chapters", {}).items(),
            key=lambda x: x[1].get("chapter_number", 0) or 0
        )
        
        viz_data = {
            "chapters": [ch[0] for ch in chapters],
            "character_presence": {},
            "theme_intensity": {}
        }
        
        # Build character presence data
        for char_id in self.arcs.get("character_arcs", {}).keys():
            viz_data["character_presence"][char_id] = []
            
            for chapter_name, chapter_data in chapters:
                char_data = chapter_data.get("character_arcs", {}).get(char_id, {})
                total_markers = sum(char_data.get("marker_counts", {}).values())
                viz_data["character_presence"][char_id].append(total_markers)
        
        # Build theme intensity data
        for theme_id in self.arcs.get("thematic_arcs", {}).keys():
            viz_data["theme_intensity"][theme_id] = []
            
            for chapter_name, chapter_data in chapters:
                theme_data = chapter_data.get("thematic_arcs", {}).get(theme_id, {})
                viz_data["theme_intensity"][theme_id].append(
                    theme_data.get("marker_hits", 0)
                )
        
        return viz_data
