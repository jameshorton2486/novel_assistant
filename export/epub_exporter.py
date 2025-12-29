"""
EPUB Exporter - E-reader compatible format.

Creates EPUB files compatible with:
- Kindle (via Send to Kindle)
- Apple Books
- Kobo
- Other e-readers
"""

from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
import uuid

try:
    from ebooklib import epub
    EPUB_AVAILABLE = True
except ImportError:
    EPUB_AVAILABLE = False


class EpubExporter:
    """
    Exports manuscript as EPUB for e-readers.
    
    Features:
    - Table of contents generation
    - Chapter navigation
    - Basic CSS styling
    - Metadata embedding
    
    Usage:
        exporter = EpubExporter()
        
        # Export manuscript
        exporter.export(chapters, metadata, "book.epub")
    """
    
    # Default CSS for e-reader compatibility
    DEFAULT_CSS = '''
    body {
        font-family: Georgia, serif;
        line-height: 1.6;
        margin: 1em;
    }
    
    h1 {
        text-align: center;
        margin-top: 3em;
        margin-bottom: 2em;
        font-size: 1.5em;
    }
    
    p {
        text-indent: 1.5em;
        margin: 0;
        padding: 0;
    }
    
    p.first {
        text-indent: 0;
    }
    
    p.scene-break {
        text-align: center;
        text-indent: 0;
        margin: 1em 0;
    }
    
    .title-page {
        text-align: center;
        margin-top: 30%;
    }
    
    .title-page h1 {
        font-size: 2em;
        margin-bottom: 0.5em;
    }
    
    .title-page .author {
        font-size: 1.2em;
        margin-top: 1em;
    }
    '''
    
    def __init__(self):
        if not EPUB_AVAILABLE:
            raise ImportError(
                "ebooklib is required for EPUB export. "
                "Install with: pip install ebooklib"
            )
    
    def export(self, chapters: List[Dict], metadata: Dict,
               output_path: str, cover_image: str = None) -> str:
        """
        Export manuscript as EPUB.
        
        Args:
            chapters: List of {"name": str, "content": str}
            metadata: {"title": str, "author": str, "description": str, "language": str}
            output_path: Where to save the file
            cover_image: Optional path to cover image
            
        Returns:
            Path to the exported file
        """
        book = epub.EpubBook()
        
        # Set metadata
        book.set_identifier(str(uuid.uuid4()))
        book.set_title(metadata.get("title", "Untitled"))
        book.set_language(metadata.get("language", "en"))
        book.add_author(metadata.get("author", "Unknown"))
        
        if metadata.get("description"):
            book.add_metadata("DC", "description", metadata["description"])
        
        # Add CSS
        nav_css = epub.EpubItem(
            uid="style_nav",
            file_name="style/nav.css",
            media_type="text/css",
            content=self.DEFAULT_CSS
        )
        book.add_item(nav_css)
        
        # Add cover if provided
        if cover_image and Path(cover_image).exists():
            with open(cover_image, 'rb') as f:
                book.set_cover("cover.jpg", f.read())
        
        # Create title page
        title_page = self._create_title_page(metadata)
        book.add_item(title_page)
        
        # Create chapters
        epub_chapters = []
        for i, chapter in enumerate(chapters):
            epub_chapter = self._create_chapter(chapter, i + 1)
            book.add_item(epub_chapter)
            epub_chapters.append(epub_chapter)
        
        # Define table of contents
        book.toc = [title_page] + epub_chapters
        
        # Add navigation files
        book.add_item(epub.EpubNcx())
        book.add_item(epub.EpubNav())
        
        # Define spine (reading order)
        book.spine = ['nav', title_page] + epub_chapters
        
        # Write the book
        epub.write_epub(output_path, book, {})
        
        return output_path
    
    def _create_title_page(self, metadata: Dict) -> epub.EpubHtml:
        """Create the title page."""
        title = metadata.get("title", "Untitled")
        author = metadata.get("author", "")
        
        content = f'''
        <html>
        <head>
            <title>{title}</title>
            <link href="style/nav.css" rel="stylesheet" type="text/css"/>
        </head>
        <body>
            <div class="title-page">
                <h1>{title}</h1>
                <p class="author">by</p>
                <p class="author">{author}</p>
            </div>
        </body>
        </html>
        '''
        
        chapter = epub.EpubHtml(
            title="Title Page",
            file_name="title.xhtml",
            lang="en"
        )
        chapter.content = content
        
        return chapter
    
    def _create_chapter(self, chapter_data: Dict, chapter_num: int) -> epub.EpubHtml:
        """Create a chapter."""
        name = chapter_data.get("name", f"Chapter {chapter_num}")
        content = chapter_data.get("content", "")
        
        # Convert content to HTML
        html_content = self._text_to_html(content)
        
        full_content = f'''
        <html>
        <head>
            <title>{name}</title>
            <link href="style/nav.css" rel="stylesheet" type="text/css"/>
        </head>
        <body>
            <h1>{name}</h1>
            {html_content}
        </body>
        </html>
        '''
        
        chapter = epub.EpubHtml(
            title=name,
            file_name=f"chapter_{chapter_num:02d}.xhtml",
            lang="en"
        )
        chapter.content = full_content
        
        return chapter
    
    def _text_to_html(self, text: str) -> str:
        """Convert plain text to HTML paragraphs."""
        paragraphs = text.split('\n\n')
        html_parts = []
        
        for i, para in enumerate(paragraphs):
            para = para.strip()
            if not para:
                continue
            
            # Check for scene break
            if para in ['#', '* * *', '***', '---']:
                html_parts.append('<p class="scene-break">#</p>')
                continue
            
            # Escape HTML characters
            para = para.replace('&', '&amp;')
            para = para.replace('<', '&lt;')
            para = para.replace('>', '&gt;')
            
            # Replace line breaks within paragraph
            para = para.replace('\n', '<br/>')
            
            # First paragraph class
            css_class = 'first' if i == 0 else ''
            
            html_parts.append(f'<p class="{css_class}">{para}</p>')
        
        return '\n'.join(html_parts)
    
    def validate_epub(self, file_path: str) -> Dict:
        """
        Basic validation of EPUB file.
        
        Args:
            file_path: Path to the EPUB file
            
        Returns:
            Validation results
        """
        try:
            book = epub.read_epub(file_path)
            
            return {
                "valid": True,
                "title": book.get_metadata("DC", "title"),
                "author": book.get_metadata("DC", "creator"),
                "chapters": len([i for i in book.get_items() 
                               if i.get_type() == epub.ITEM_DOCUMENT])
            }
        except Exception as e:
            return {
                "valid": False,
                "error": str(e)
            }
