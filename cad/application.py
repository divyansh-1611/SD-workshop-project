import os

from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *

from cad.sketch import Sketch
from cad.solver import *

directory = os.path.dirname(__file__)


def icon_path(name: str) -> str:
    return os.path.join(directory, 'icons', name)


class Application(QMainWindow):

    def __init__(self, *args):
        super().__init__(*args)

        self.sketch = None

        self.menu = None
        self.toolBar = None
        self.toolBarGroup = None

        self.initSketch()
        self.initMenuBar()
        self.initToolBar()
        self.initStatusBar()
        self.initGeometry()

        self.setWindowTitle('PIXOR-Cad')

    def initSketch(self):
        self.sketch = Sketch(self)
        self.setCentralWidget(self.sketch)

    def initMenuBar(self):
        self.menu = self.menuBar()

        file = self.menu.addMenu('File')
        file.addAction(self.exitAction())
        file.addAction(self.openAction())
        file.addAction(self.saveAction())
        file.addAction(self.saveasAction())

        edit = self.menu.addMenu('Edit')
        edit.addAction(self.undoAction())
        edit.addAction(self.RedoAction())
        edit.addAction(self.ClrundoAction())
        edit.addAction(self.Clrredoaction())

        view = self.menu.addMenu("View")
        view.addAction(self.CreateShortcuts())
        view.addAction(self.ChangeContrast())
        view.addAction(self.zoomi())
        view.addAction(self.zoomo())

        help = self.menu.addMenu("Help")
        help.addAction(self.aboutus())
        help.addAction(self.VersionDetails())

    def undoAction(self):
        action = QAction('Undo', self.menu)
        action.setShortcut('Ctrl+Z')
        action.setStatusTip('Undo')
        action.setToolTip('Undo')
        return action
    
    def RedoAction(self):
        action = QAction("Redo", self.menu)
        action.setStatusTip("Redo")
        action.setToolTip("Redo")
        action.setShortcut("Ctrl+Y")    
        return action
    
    def ClrundoAction(self):
        action = QAction('Clear Undo', self)
        action.setShortcut('Ctrl+Shift+Z')
        action.setStatusTip('Clear Undo')
        action.setToolTip('Clear Undo')
        return action

    def Clrredoaction(self):
        action = QAction('Clear Redo', self)
        action.setShortcut('Ctrl+Shift+Y')
        action.setStatusTip('Clear Redo')
        action.setToolTip('Clear Redo')
        return action

    def CreateShortcuts(self):
        action = QAction('Create Shortcuts', self)
        action.setStatusTip('Create Shortcuts')
        action.setToolTip('Create Shortcuts')
        return action

    def ChangeContrast(self):
        action = QAction('Change Contrast', self)
        action.setStatusTip('Change Contrast')
        action.setToolTip('Change Contrast')
        return action

    def saveasAction(self):
        action = QAction("Save as", self)
        action.setStatusTip("Save as")
        action.setToolTip("Save as")
        return action
    
    def zoomi(self):
        action = QAction('Zoom In', self)
        action.setStatusTip('Zoom In')
        action.setToolTip('Zoom In')
        return action

    def zoomo(self):
        action = QAction('Zoom Out', self)
        action.setStatusTip('Zoom Out')
        action.setToolTip('Zoom Out')
        return action

    def aboutus(self):
        action = QAction('About Us', self)
        action.setStatusTip('About Us')
        action.setToolTip('About Us')
        return action

    def VersionDetails(self):
        action = QAction('Version Details', self)
        action.setStatusTip('Version Details')
        action.setToolTip('Version Details')
        return action
    
    def copyAction(self):
        action = QAction('Copy', self.menu)
        action.setShortcut('Ctrl+C')
        action.setStatusTip('Copy')
        action.setToolTip('Copy')
        return action

    def pasteAction(self):
        action = QAction('Paste', self.menu)
        action.setShortcut('Ctrl+V')
        action.setStatusTip('Paste')
        action.setToolTip('Paste')
        return action

    def deleteAction(self):
        action = QAction('Delete', self.menu)
        action.setShortcut('Delete')
        action.setStatusTip('Delete')
        action.setToolTip('Delete')
        return action

    def exitAction(self):
        action = QAction('Exit', self.menu)
        action.setShortcut('Ctrl+Q')
        action.setToolTip('Close application')
        action.setStatusTip('Close application')
        action.triggered.connect(self.close)
        return action

    def saveAction(self):
        action = QAction('Save As', self.menu)
        action.setShortcut('Ctrl+S')
        action.setToolTip('Save current application')
        action.setStatusTip('Save current application')
        action.triggered.connect(self.showSaveDialog)
        return action

    def openAction(self):
        action = QAction('Open', self.menu)
        action.setShortcut('Ctrl+O')
        action.setToolTip('Open file')
        action.setStatusTip('Open file')
        action.triggered.connect(self.showOpenDialog)
        return action

    def initToolBar(self):
        self.toolBar = self.addToolBar('Drawing')
        self.toolBarGroup = QActionGroup(self.toolBar)

        default = self.disableAction()

        actions = [
            default,
            self.lineAction(),
            self.pointAction(),
            self.parallelAction(),
            # self.perpendicularAction(),
            self.verticalAction(),
            self.horizontalAction(),
            self.coincidentAction(),
            self.fixedAction(),
            self.angleAction(),
            self.lengthAction(),
        ]

        for action in actions:
            action.setCheckable(True)
            action.setParent(self.toolBar)
            self.toolBar.addAction(action)
            self.toolBarGroup.addAction(action)

        default.setChecked(True)

    def pointAction(self):
        action = QAction('Point')
        action.setShortcut('Ctrl+P')
        action.setToolTip('Draw point')
        action.setStatusTip('Draw point')
        action.setIcon(QIcon(icon_path('point.png')))
        action.triggered.connect(self.pointActionHandler)
        return action

    def pointActionHandler(self):
        self.sketch.handler = PointDrawing()

    def lineAction(self):
        action = QAction('Line')
        action.setShortcut('Ctrl+L')
        action.setToolTip('Draw line')
        action.setStatusTip('Draw line')
        action.setIcon(QIcon(icon_path('line.png')))
        action.triggered.connect(self.lineActionHandler)
        return action

    def lineActionHandler(self):
        self.sketch.handler = LineDrawing()

    def horizontalAction(self):
        action = QAction('Horizontal')
        action.setToolTip('Horizontal constraint')
        action.setStatusTip('Horizontal constraint')
        action.setIcon(QIcon(icon_path('horizontal.png')))
        action.triggered.connect(self.horizontalActionHandler)
        return action

    def horizontalActionHandler(self):
        self.sketch.handler = HorizontalHandler()

    def verticalAction(self):
        action = QAction('Vertical')
        action.setToolTip('Vertical constraint')
        action.setStatusTip('Vertical constraint')
        action.setIcon(QIcon(icon_path('vertical.png')))
        action.triggered.connect(self.verticalActionHandler)
        return action

    def verticalActionHandler(self):
        self.sketch.handler = VerticalHandler()

    def angleAction(self):
        action = QAction('Angle')
        action.setToolTip('Angle constraint')
        action.setStatusTip('Angle constraint')
        action.setIcon(QIcon(icon_path('angle.png')))
        action.triggered.connect(self.angleActionHandler)
        return action

    def angleActionHandler(self):

        def askAngleValue():
            label = 'Input angle value:'
            title = 'Set angle constraint'
            return QInputDialog.getDouble(self.sketch.parent(), title, label, 0)

        angle, ok = askAngleValue()
        if ok:
            self.sketch.handler = AngleHandler(angle)

    def lengthAction(self):
        action = QAction('Length')
        action.setToolTip('Length constraint')
        action.setStatusTip('Length constraint')
        action.setIcon(QIcon(icon_path('length.png')))
        action.triggered.connect(self.lengthActionHandler)
        return action

    def lengthActionHandler(self):

        def askLengthValue():
            label = 'Input length value:'
            title = 'Set length constraint'
            return QInputDialog.getDouble(self.sketch.parent(), title, label, 0, 0)

        length, ok = askLengthValue()
        if ok:
            self.sketch.handler = LengthHandler(length)

    def parallelAction(self):
        action = QAction('Parallel')
        action.setToolTip('Parallel constraint')
        action.setStatusTip('Parallel constraint')
        action.setIcon(QIcon(icon_path('parallel.png')))
        action.triggered.connect(self.parallelsActionHandler)
        return action

    def parallelsActionHandler(self):
        self.sketch.handler = ParallelHandler()

    def perpendicularAction(self):
        action = QAction('Perpendicular')
        action.setToolTip('Perpendicular constraint')
        action.setStatusTip('Perpendicular constraint')
        action.setIcon(QIcon(icon_path('perpendicular.png')))
        action.triggered.connect(self.perpendicularActionHandler)
        return action

    def perpendicularActionHandler(self):
        pass

    def coincidentAction(self):
        action = QAction('Coincident')
        action.setToolTip('Coincident constraint')
        action.setStatusTip('Coincident constraint')
        action.setIcon(QIcon(icon_path('coincident.png')))
        action.triggered.connect(self.coincidentActionHandler)
        return action

    def coincidentActionHandler(self):
        self.sketch.handler = CoincidentHandler()

    def fixedAction(self):
        action = QAction('Fixed')
        action.setToolTip('Fixed constraint')
        action.setStatusTip('Fixed constraint')
        action.setIcon(QIcon(icon_path('fixed.png')))
        action.triggered.connect(self.fixedActionHandler)
        return action

    def fixedActionHandler(self):

        def askCoordinateValue():
            label = 'Enter coordinate:'
            title = 'Set fixing constraint'
            return QInputDialog.getDouble(self.sketch.parent(), title, label, 0)

        x, ok = askCoordinateValue()
        if ok:
            y, ok = askCoordinateValue()
            if ok:
                self.sketch.handler = FixingHandler(x, y)

    def disableAction(self):
        action = QAction('Disable')
        action.setToolTip('Choose action')
        action.setStatusTip('Choose action')
        action.setIcon(QIcon(icon_path('cursor.png')))
        action.triggered.connect(self.disableActionHandler)
        return action

    def disableActionHandler(self):
        for action in self.toolBarGroup.actions():
            action.setChecked(False)

        self.toolBarGroup.actions()[0].setChecked(True)

    def initStatusBar(self):
        self.statusBar().showMessage('Ready')

    def initGeometry(self):
        desktop = QDesktopWidget()
        self.setGeometry(desktop.availableGeometry())

    def showOpenDialog(self):
        ext = '*.json'
        title = 'Open from'
        default = '/home/cad.json'
        files = QFileDialog().getOpenFileName(self, title, default, ext, options=0)

        if files and files[0]:
            with open(files[0], 'r') as fp:
                fp.read()

    def showSaveDialog(self):
        ext = '*.json'
        title = 'Save as'
        default = '/home/cad.json'
        files = QFileDialog().getSaveFileName(self, title, default, ext, options=0)

        if files and files[0]:
            with open(files[0], 'w') as fp:
                fp.write('')

    def keyPressEvent(self, event):
        self.sketch.keyPressEvent(event)

        if event.key() == Qt.Key_Escape:
            return self.disableActionHandler()

    def closeEvent(self, event):
        title = 'Close application'
        question = 'Are you sure you want to quit?'

        default = QMessageBox.No
        buttons = QMessageBox.No | QMessageBox.Yes

        answer = QMessageBox().question(self, title, question, buttons, default)
        if answer == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()
