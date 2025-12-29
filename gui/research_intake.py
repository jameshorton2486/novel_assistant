"""
Research Intake GUI
===================

PHASE 2 FEATURE

PyQt6 interface for research document upload and classification.

Features:
- Drag-and-drop file upload
- Classification preview (AI suggests, user confirms)
- Batch processing
- Integration with research governance pipeline

Dependencies: PyQt6
"""

# NOTE: This is a stub implementation
# Full implementation requires PyQt6: pip install PyQt6

try:
    from PyQt6.QtWidgets import (
        QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QLabel, QPushButton, QListWidget, QListWidgetItem,
        QComboBox, QTextEdit, QProgressBar, QFileDialog,
        QMessageBox, QFrame
    )
    from PyQt6.QtCore import Qt, QMimeData
    from PyQt6.QtGui import QDragEnterEvent, QDropEvent
    PYQT_AVAILABLE = True
except ImportError:
    PYQT_AVAILABLE = False


from pathlib import Path
from typing import List, Optional
import sys


class DropZone(QFrame if PYQT_AVAILABLE else object):
    """Drag-and-drop zone for file uploads."""
    
    def __init__(self, parent=None):
        if not PYQT_AVAILABLE:
            return
            
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setMinimumHeight(150)
        self.setStyleSheet("""
            QFrame {
                border: 2px dashed #aaa;
                border-radius: 10px;
                background-color: #f8f8f8;
            }
            QFrame:hover {
                border-color: #666;
                background-color: #f0f0f0;
            }
        """)
        
        layout = QVBoxLayout(self)
        self.label = QLabel("Drop files here\nor click to browse")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.label)
        
        self.files_dropped_callback = None
    
    def dragEnterEvent(self, event: 'QDragEnterEvent'):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
    
    def dropEvent(self, event: 'QDropEvent'):
        files = []
        for url in event.mimeData().urls():
            if url.isLocalFile():
                files.append(url.toLocalFile())
        
        if files and self.files_dropped_callback:
            self.files_dropped_callback(files)
    
    def mousePressEvent(self, event):
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Select Research Documents",
            "",
            "Documents (*.pdf *.docx *.md *.txt);;All Files (*)"
        )
        if files and self.files_dropped_callback:
            self.files_dropped_callback(files)


class ResearchIntakeWindow(QMainWindow if PYQT_AVAILABLE else object):
    """
    Main window for research intake.
    
    Workflow:
    1. Drop/select files
    2. AI classifies each file
    3. User confirms/adjusts classification
    4. Process (digest) approved files
    5. Review digests
    6. Approve for final placement
    """
    
    RESEARCH_CLASSES = [
        ("canon", "CANON - Sacred facts for the novel"),
        ("context", "CONTEXT - Background, never narrated"),
        ("artifact", "ARTIFACT - Scene triggers, in-world docs"),
        ("craft", "CRAFT - Writing guidance, meta-level")
    ]
    
    def __init__(self, base_dir: Path):
        if not PYQT_AVAILABLE:
            print("PyQt6 not installed. Install with: pip install PyQt6")
            return
            
        super().__init__()
        self.base_dir = Path(base_dir)
        self.pending_files: List[dict] = []
        
        self.setWindowTitle("Research Intake - Novel Assistant")
        self.setMinimumSize(800, 600)
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Build the interface."""
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        
        # Header
        header = QLabel("Research Intake")
        header.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(header)
        
        # Drop zone
        self.drop_zone = DropZone()
        self.drop_zone.files_dropped_callback = self._on_files_dropped
        layout.addWidget(self.drop_zone)
        
        # Intake queue
        queue_label = QLabel("Intake Queue")
        queue_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        layout.addWidget(queue_label)
        
        self.queue_list = QListWidget()
        self.queue_list.setMinimumHeight(200)
        self.queue_list.itemClicked.connect(self._on_item_selected)
        layout.addWidget(self.queue_list)
        
        # Classification panel
        class_panel = QHBoxLayout()
        
        class_panel.addWidget(QLabel("Classification:"))
        self.class_combo = QComboBox()
        for value, label in self.RESEARCH_CLASSES:
            self.class_combo.addItem(label, value)
        class_panel.addWidget(self.class_combo)
        
        self.classify_btn = QPushButton("Classify Selected")
        self.classify_btn.clicked.connect(self._on_classify)
        class_panel.addWidget(self.classify_btn)
        
        layout.addLayout(class_panel)
        
        # Action buttons
        btn_panel = QHBoxLayout()
        
        self.process_btn = QPushButton("Process All")
        self.process_btn.clicked.connect(self._on_process_all)
        btn_panel.addWidget(self.process_btn)
        
        self.clear_btn = QPushButton("Clear Queue")
        self.clear_btn.clicked.connect(self._on_clear)
        btn_panel.addWidget(self.clear_btn)
        
        layout.addLayout(btn_panel)
        
        # Progress
        self.progress = QProgressBar()
        self.progress.setVisible(False)
        layout.addWidget(self.progress)
        
        # Status
        self.status = QLabel("Ready. Drop files to begin.")
        layout.addWidget(self.status)
    
    def _on_files_dropped(self, files: List[str]):
        """Handle dropped files."""
        for filepath in files:
            path = Path(filepath)
            if path.suffix.lower() in ['.pdf', '.docx', '.md', '.txt']:
                self.pending_files.append({
                    "path": str(path),
                    "name": path.name,
                    "class": None,
                    "status": "pending"
                })
                
                item = QListWidgetItem(f"📄 {path.name} [unclassified]")
                self.queue_list.addItem(item)
        
        self.status.setText(f"{len(self.pending_files)} files in queue")
    
    def _on_item_selected(self, item: 'QListWidgetItem'):
        """Handle item selection."""
        pass  # Could show preview
    
    def _on_classify(self):
        """Classify selected item."""
        current = self.queue_list.currentRow()
        if current >= 0 and current < len(self.pending_files):
            class_value = self.class_combo.currentData()
            class_label = self.class_combo.currentText().split(" - ")[0]
            
            self.pending_files[current]["class"] = class_value
            self.pending_files[current]["status"] = "classified"
            
            # Update list
            name = self.pending_files[current]["name"]
            self.queue_list.item(current).setText(f"📄 {name} [{class_label}]")
            
            self.status.setText(f"Classified as {class_label}")
    
    def _on_process_all(self):
        """Process all classified files."""
        classified = [f for f in self.pending_files if f["status"] == "classified"]
        
        if not classified:
            QMessageBox.warning(self, "No Files", "No classified files to process.")
            return
        
        self.progress.setVisible(True)
        self.progress.setMaximum(len(classified))
        
        # This would integrate with research_ingest and research_digestor
        for i, file_info in enumerate(classified):
            self.progress.setValue(i + 1)
            self.status.setText(f"Processing {file_info['name']}...")
            
            # TODO: Actual processing
            # from services.research_ingest import ingest_file
            # from services.research_digestor import distill_document
            
        self.progress.setVisible(False)
        self.status.setText(f"Processed {len(classified)} files")
        
        QMessageBox.information(
            self, 
            "Complete", 
            f"Processed {len(classified)} files.\nReview digests in the research folder."
        )
    
    def _on_clear(self):
        """Clear the queue."""
        self.pending_files.clear()
        self.queue_list.clear()
        self.status.setText("Queue cleared")


def launch_intake_gui(base_dir: str = "."):
    """Launch the research intake GUI."""
    if not PYQT_AVAILABLE:
        print("=" * 50)
        print("PyQt6 is required for the GUI.")
        print("Install with: pip install PyQt6")
        print("=" * 50)
        return None
    
    from PyQt6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    window = ResearchIntakeWindow(Path(base_dir))
    window.show()
    return app.exec()


# For testing without full PyQt
def cli_intake(base_dir: str = "."):
    """Command-line intake alternative."""
    print("=" * 50)
    print("RESEARCH INTAKE (CLI Mode)")
    print("=" * 50)
    print()
    print("Drop files into: research/intake/")
    print("Then run classification manually.")
    print()
    print("For GUI mode, install PyQt6:")
    print("  pip install PyQt6")
    print()


if __name__ == "__main__":
    launch_intake_gui()
