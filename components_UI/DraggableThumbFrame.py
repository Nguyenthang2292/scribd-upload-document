from PyQt5.QtCore import Qt, QMimeData
from PyQt5.QtGui import QPixmap, QImage, QDrag
from PyQt5.QtWidgets import QFrame, QWidget
from typing import List, Optional, Callable

class DraggableThumbFrame(QFrame):
    """
    A draggable thumbnail frame for PDF preview and reordering.
    
    This class provides drag-and-drop functionality for reordering PDF files
    in the merge interface, along with selection and double-click capabilities.
    """

    def __init__(
        self,
        parent: QWidget,
        idx: int,
        on_drag_drop: Callable[[int, int], None],
        on_double_click: Callable[[int, object], None],
        thumbnails: Optional[List[QPixmap]] = None,
    ) -> None:
        """Initialize the draggable thumbnail frame.
        
        Args:
            parent: Parent widget
            idx: Index of this frame
            on_drag_drop: Callback for drag and drop events
            on_double_click: Callback for double-click events
            thumbnails: List of thumbnail pixmaps
        """
        super().__init__(parent)
        self.idx = idx
        self.on_drag_drop = on_drag_drop
        self.on_double_click = on_double_click
        self.thumbnails = thumbnails or []
        self.drag_start_pos = None
        
        self.setAcceptDrops(True)

    def mousePressEvent(self, event) -> None:
        """Handle mouse press events to initiate drag operations."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_start_pos = event.pos()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event) -> None:
        """Handle mouse move events to create drag operations."""
        if not (event.buttons() & Qt.MouseButton.LeftButton):
            return
            
        if (event.pos() - self.drag_start_pos).manhattanLength() <= 10:
            return
            
        drag = QDrag(self)
        mime = QMimeData()
        mime.setText(str(self.idx))
        drag.setMimeData(mime)
        
        # Create faded drag preview
        pixmap = self.grab()
        img = pixmap.toImage().convertToFormat(QImage.Format_ARGB32)
        
        for y in range(img.height()):
            for x in range(img.width()):
                color = img.pixelColor(x, y)
                color.setAlpha(int(255 * 0.3))
                img.setPixelColor(x, y, color)
                
        faded_pixmap = QPixmap.fromImage(img)
        drag.setPixmap(faded_pixmap)
        drag.setHotSpot(event.pos())
        drag.exec_(Qt.DropAction.MoveAction)

    def dragEnterEvent(self, event) -> None:
        """Handle drag enter events."""
        if event.mimeData().hasText():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event) -> None:
        """Handle drop events for reordering."""
        from_idx = int(event.mimeData().text())
        to_idx = self.idx
        
        if from_idx != to_idx:
            self.on_drag_drop(from_idx, to_idx)
        event.acceptProposedAction()

    def mouseDoubleClickEvent(self, event) -> None:
        """Handle double-click events for selection."""
        self.on_double_click(self.idx, event)