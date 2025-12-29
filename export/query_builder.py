"""
Query Package Builder - Agent submission materials.

Generates:
- Query letter
- Synopsis (various lengths)
- Sample chapters package
- Comp title suggestions
"""

from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime


class QueryBuilder:
    """
    Builds query packages for agent submissions.
    
    Components:
    - Query letter template
    - Short synopsis (1 page)
    - Long synopsis (3-5 pages)
    - First 3 chapters package
    - Comp titles with rationale
    
    Usage:
        builder = QueryBuilder(model_router)
        
        # Generate query letter
        letter = builder.generate_query_letter(metadata, synopsis)
        
        # Build full package
        package = builder.build_package(chapters, metadata)
    """
    
    # Query letter template
    QUERY_TEMPLATE = '''Dear {agent_name},

{hook}

{book_description}

{title_word_count_genre}

{bio}

{closing}

Sincerely,
{author_name}
'''
    
    def __init__(self, model_router=None):
        """
        Initialize builder.
        
        Args:
            model_router: Optional ModelRouter for AI-assisted generation
        """
        self.router = model_router
    
    def generate_query_letter(self, metadata: Dict, synopsis: str,
                               agent_name: str = "[Agent Name]") -> str:
        """
        Generate a query letter.
        
        Args:
            metadata: {"title", "author", "word_count", "genre", "bio"}
            synopsis: Short synopsis of the book
            agent_name: Name of the agent (for personalization)
            
        Returns:
            Formatted query letter
        """
        title = metadata.get("title", "UNTITLED")
        author = metadata.get("author", "")
        word_count = metadata.get("word_count", 0)
        genre = metadata.get("genre", "literary fiction")
        bio = metadata.get("bio", "")
        comps = metadata.get("comp_titles", [])
        
        # Format word count
        if word_count:
            word_count_str = f"{word_count:,}"
        else:
            word_count_str = "[WORD COUNT]"
        
        # Build hook (first compelling sentence)
        # This would ideally be customized per book
        hook = synopsis.split('.')[0] + '.' if synopsis else "[HOOK - First compelling sentence about your book]"
        
        # Build book description (2-3 paragraphs from synopsis)
        book_description = synopsis[:500] if synopsis else "[BOOK DESCRIPTION - 2-3 paragraphs]"
        
        # Title/word count/genre line
        comp_str = ""
        if comps:
            comp_str = f" Comparable titles include {' and '.join(comps[:2])}."
        
        title_line = (
            f"{title.upper()} is a {genre} novel complete at {word_count_str} words.{comp_str}"
        )
        
        # Bio
        if not bio:
            bio = "[YOUR BIO - Relevant credentials, publications, platform]"
        
        # Build letter
        letter = self.QUERY_TEMPLATE.format(
            agent_name=agent_name,
            hook=hook,
            book_description=book_description,
            title_word_count_genre=title_line,
            bio=bio,
            closing="Thank you for your time and consideration.",
            author_name=author or "[Your Name]"
        )
        
        return letter
    
    def generate_short_synopsis(self, chapters: List[Dict], 
                                  metadata: Dict) -> str:
        """
        Generate 1-page synopsis (approximately 500 words).
        
        Args:
            chapters: List of chapter data
            metadata: Book metadata
            
        Returns:
            Short synopsis text
        """
        if not self.router:
            return self._generate_synopsis_template(chapters, metadata, "short")
        
        # Combine chapter content for context
        chapter_summaries = []
        for ch in chapters:
            # Get first 500 chars of each chapter
            preview = ch.get("content", "")[:500]
            chapter_summaries.append(f"{ch['name']}: {preview}...")
        
        prompt = f'''Generate a 1-page synopsis (approximately 500 words) for this novel:

Title: {metadata.get("title", "Untitled")}
Genre: {metadata.get("genre", "literary fiction")}

Chapter Previews:
{chr(10).join(chapter_summaries[:6])}

Requirements:
1. Write in present tense
2. Include main characters and their arcs
3. Reveal the ending (agents need to know how it ends)
4. Focus on emotional journey and stakes
5. Keep under 500 words

Generate the synopsis:'''
        
        from models.model_router import ModelType
        response = self.router.generate(prompt, ModelType.CLAUDE_SONNET, max_tokens=1000)
        
        return response
    
    def generate_long_synopsis(self, chapters: List[Dict],
                                 metadata: Dict) -> str:
        """
        Generate 3-5 page synopsis (approximately 1500-2500 words).
        
        Args:
            chapters: List of chapter data
            metadata: Book metadata
            
        Returns:
            Long synopsis text
        """
        if not self.router:
            return self._generate_synopsis_template(chapters, metadata, "long")
        
        # Build detailed chapter breakdown
        chapter_details = []
        for ch in chapters:
            preview = ch.get("content", "")[:1000]
            chapter_details.append(f"## {ch['name']}\n{preview}...")
        
        prompt = f'''Generate a detailed 3-5 page synopsis (1500-2500 words) for this novel:

Title: {metadata.get("title", "Untitled")}
Genre: {metadata.get("genre", "literary fiction")}

Chapter Content:
{chr(10).join(chapter_details[:8])}

Requirements:
1. Write in present tense
2. Cover all major plot points
3. Include character development arcs
4. Reveal all twists and the ending
5. Show cause and effect between events
6. Maintain narrative flow
7. Target 1500-2500 words

Generate the detailed synopsis:'''
        
        from models.model_router import ModelType
        response = self.router.generate(prompt, ModelType.CLAUDE_SONNET, max_tokens=4000)
        
        return response
    
    def _generate_synopsis_template(self, chapters: List[Dict],
                                      metadata: Dict, length: str) -> str:
        """Generate synopsis template when AI is not available."""
        word_target = "500" if length == "short" else "1500-2500"
        
        template = f'''SYNOPSIS TEMPLATE - {metadata.get("title", "UNTITLED")}

[Target: {word_target} words, present tense]

SETUP:
[Introduce protagonist, their world, and what they want]

CATALYST:
[The event that sets the story in motion]

RISING ACTION:
[Key events that escalate the conflict]

MIDPOINT:
[Major revelation or turning point]

COMPLICATIONS:
[Things get worse, stakes increase]

CLIMAX:
[The major confrontation or decision]

RESOLUTION:
[How it ends, what the protagonist learned/lost/gained]

---
Chapters to cover:
'''
        for ch in chapters:
            template += f"- {ch['name']}\n"
        
        return template
    
    def suggest_comp_titles(self, metadata: Dict, themes: List[str] = None) -> List[Dict]:
        """
        Suggest comparable titles for querying.
        
        Args:
            metadata: Book metadata
            themes: List of major themes
            
        Returns:
            List of comp title suggestions with rationale
        """
        if not self.router:
            return self._default_comp_suggestions(metadata)
        
        prompt = f'''Suggest 5 comparable titles for this novel that would work in a query letter:

Title: {metadata.get("title", "Untitled")}
Genre: {metadata.get("genre", "literary fiction")}
Setting: {metadata.get("setting", "")}
Themes: {", ".join(themes) if themes else ""}
Description: {metadata.get("description", "")}

Requirements for good comp titles:
1. Published within last 5 years
2. Same or adjacent genre
3. Similar in tone, theme, or audience
4. Reasonably successful but not mega-bestsellers
5. Explainable connection

Format as JSON array with: title, author, year, connection'''
        
        from models.model_router import ModelType
        response = self.router.generate(prompt, ModelType.CLAUDE_HAIKU)
        
        # Try to parse response
        try:
            import json
            import re
            json_match = re.search(r'\[[\s\S]*\]', response)
            if json_match:
                return json.loads(json_match.group())
        except:
            pass
        
        return self._default_comp_suggestions(metadata)
    
    def _default_comp_suggestions(self, metadata: Dict) -> List[Dict]:
        """Return default comp suggestions for historical fiction."""
        return [
            {
                "title": "Water for Elephants",
                "author": "Sara Gruen",
                "year": 2006,
                "connection": "Circus setting, forbidden romance, historical period"
            },
            {
                "title": "The Night Circus",
                "author": "Erin Morgenstern",
                "year": 2011,
                "connection": "Circus world, magical realism, atmospheric"
            },
            {
                "title": "The Book of Night Women",
                "author": "Marlon James",
                "year": 2009,
                "connection": "Historical fiction exploring labor exploitation"
            }
        ]
    
    def build_package(self, chapters: List[Dict], metadata: Dict,
                       output_dir: str, sample_chapters: int = 3) -> Dict:
        """
        Build complete query package.
        
        Args:
            chapters: All chapter data
            metadata: Book metadata
            output_dir: Directory to save files
            sample_chapters: Number of sample chapters to include
            
        Returns:
            Paths to all generated files
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        package = {
            "generated_at": datetime.now().isoformat(),
            "files": {}
        }
        
        # Generate short synopsis
        short_synopsis = self.generate_short_synopsis(chapters, metadata)
        short_path = output_path / "synopsis_short.md"
        short_path.write_text(short_synopsis, encoding='utf-8')
        package["files"]["short_synopsis"] = str(short_path)
        
        # Generate long synopsis
        long_synopsis = self.generate_long_synopsis(chapters, metadata)
        long_path = output_path / "synopsis_long.md"
        long_path.write_text(long_synopsis, encoding='utf-8')
        package["files"]["long_synopsis"] = str(long_path)
        
        # Generate query letter
        query_letter = self.generate_query_letter(metadata, short_synopsis)
        query_path = output_path / "query_letter.md"
        query_path.write_text(query_letter, encoding='utf-8')
        package["files"]["query_letter"] = str(query_path)
        
        # Compile sample chapters
        sample_content = []
        for ch in chapters[:sample_chapters]:
            sample_content.append(f"# {ch['name']}\n\n{ch['content']}")
        
        samples_path = output_path / "sample_chapters.md"
        samples_path.write_text("\n\n---\n\n".join(sample_content), encoding='utf-8')
        package["files"]["sample_chapters"] = str(samples_path)
        
        # Comp titles
        comps = self.suggest_comp_titles(metadata)
        comp_content = "# Comparable Titles\n\n"
        for comp in comps:
            comp_content += f"## {comp['title']} by {comp['author']} ({comp.get('year', 'N/A')})\n"
            comp_content += f"{comp.get('connection', '')}\n\n"
        
        comp_path = output_path / "comp_titles.md"
        comp_path.write_text(comp_content, encoding='utf-8')
        package["files"]["comp_titles"] = str(comp_path)
        
        # Package manifest
        manifest_path = output_path / "package_manifest.md"
        manifest_content = f'''# Query Package: {metadata.get("title", "Untitled")}

Generated: {package["generated_at"]}

## Contents

1. **Query Letter** - {package["files"]["query_letter"]}
2. **Short Synopsis** (1 page) - {package["files"]["short_synopsis"]}
3. **Long Synopsis** (3-5 pages) - {package["files"]["long_synopsis"]}
4. **Sample Chapters** (first {sample_chapters}) - {package["files"]["sample_chapters"]}
5. **Comparable Titles** - {package["files"]["comp_titles"]}

## Metadata

- **Title:** {metadata.get("title", "Untitled")}
- **Author:** {metadata.get("author", "")}
- **Genre:** {metadata.get("genre", "literary fiction")}
- **Word Count:** {metadata.get("word_count", "TBD")}

## Submission Checklist

- [ ] Personalize query letter for each agent
- [ ] Check agent's specific submission requirements
- [ ] Verify word count is accurate
- [ ] Update bio with relevant credentials
- [ ] Format per agent guidelines (some want DOCX, some want in email body)
'''
        manifest_path.write_text(manifest_content, encoding='utf-8')
        package["files"]["manifest"] = str(manifest_path)
        
        return package
