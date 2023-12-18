import SVGrandomizer
from PyQt5.QtSvg import QSvgWidget
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtWidgets import QApplication, QWidget, QGridLayout, QDesktopWidget, QCheckBox, QVBoxLayout, QSizePolicy, QHBoxLayout
from numpy import interp
import sys

imageWidth = 400
imageHeight = 400
inputFile = '8398873_3862879.svg'
#inputFile = '23672634_6829620.svg'
#inputFile = '13900614_5367491.svg'
#inputFile = '4948955_94190.svg'
gridItems = [[]]

modifyPosition = True
modifyRotation = True
modifySize = True

numRows = 2
numCols = 3


class CheckboxWidget(QWidget):
    def __init__(self, label, initialValue=True, parent=None):
        super(CheckboxWidget, self).__init__(parent)
        self.checkbox = QCheckBox(label)
        self.checkbox.setChecked(initialValue)
        
        # Style the checkbox
        self.checkbox.setStyleSheet(
            "QCheckBox { font-size: 8px; background-color: white ; border-radius: 2px; font: Serif;}"
            "QCheckBox::indicator { width: 12px; height: 12px; }"
        )

        layout = QVBoxLayout(self)
        layout.addWidget(self.checkbox)
        self.setLayout(layout)

        

# For the visualization - it is best to use a square size of the grid (so the images looks better)
class GridItem(QWidget):
    clicked = pyqtSignal()

    def __init__(self, parent=None):
        super(GridItem, self).__init__(parent)
        self.setFixedSize(imageWidth, imageHeight)  # Set the size of each grid item

        self.widgetSvg = QSvgWidget(parent=self)
        self.widgetSvg.setGeometry(0, 0, imageWidth, imageHeight)

        self.clicked.connect(self.ReactToClick)

    def SetPosition(self, row, col):
        self.row = row
        self.col = col
        self.imgName = "imageGrid/svgImage" + str(row) + str(col) + ".svg"

    def SetImageParameters(self, imagePickProbability, imageSimilarity):
        self.imagePickProbability = imagePickProbability
        self.imageSimilarity = imageSimilarity
        self.RegenerateImage()

    def ReactToClick(self):
        print("Click has been called on image " + self.imgName)
        self.RegenerateImage()
        
    def mousePressEvent(self, event):
        self.clicked.emit()
        
    def RegenerateImage(self):
        print("regenerating " + str(self.row) + " " + str(self.col))
        SVGrandomizer.createSVGFile(inputFile, self.imgName, self.imagePickProbability, self.imageSimilarity, modifyPosition, modifyRotation, modifySize)
        with open(self.imgName, 'rb') as svg_file:
            svg_data = svg_file.read().decode("utf-8").encode("utf-8")
        self.svgFile = svg_data
        
        self.widgetSvg.load(self.svgFile)
        self.widgetSvg.repaint()
        print("loaded SVG " + str(self.row) + " " + str(self.col))


# We havea  grid of size numRows x numCols
# imagePickProbability is on the X axis - on left 0, on right 1
# imageSimilarity is on the Y axis - on top 1, on right 0
# Top left image should be the most similiar to the real image
class Main(QWidget):
    clicked = pyqtSignal()

    def __init__(self, parent=None):
        super(Main, self).__init__(parent)

        self.setGeometry(0, 0, 1100, 1100)
        
        # Add three checkboxes for modifying position, orientation, and size
        self.positionCheckbox = CheckboxWidget("Modify Position", initialValue=True)
        self.orientationCheckbox = CheckboxWidget("Modify Orientation", initialValue=True)
        self.sizeCheckbox = CheckboxWidget("Modify Size", initialValue=True)

        # Connect checkboxes to corresponding slots
        self.positionCheckbox.checkbox.stateChanged.connect(self.toggleModifyPosition)
        self.orientationCheckbox.checkbox.stateChanged.connect(self.toggleModifyRotation)
        self.sizeCheckbox.checkbox.stateChanged.connect(self.toggleModifySize)

        # Create a grid of widgets
        self.topWidget = QWidget()
        self.topWidget.setFixedHeight(50)
        self.top_layout = QHBoxLayout(self.topWidget)
        self.bottom_layout = QGridLayout()
        self.generateTopGrid()
        self.generateBottomGrid()
        
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.topWidget)
        #main_layout.addLayout(self.top_layout)
        main_layout.addLayout(self.bottom_layout)

        # Set the size policy to allow the window to be resizable
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
    def toggleModifyPosition(self, state):
        global modifyPosition
        modifyPosition = state == Qt.Checked

    def toggleModifyRotation(self, state):
        global modifyRotation
        modifyRotation = state == Qt.Checked

    def toggleModifySize(self, state):
        global modifySize
        modifySize = state == Qt.Checked

    def resizeEvent(self, event):
        self.regenerateLayouts()

    def regenerateLayouts(self):
        self.clearLayout(self.top_layout)
        self.clearLayout(self.bottom_layout)
        self.generateTopGrid()
        self.generateBottomGrid()

    def clearLayout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)
                widget.deleteLater()

    def generateTopGrid(self):
        self.top_layout.addWidget(self.positionCheckbox)
        self.top_layout.addWidget(self.orientationCheckbox)
        self.top_layout.addWidget(self.sizeCheckbox)
        
    def generateBottomGrid(self):
        screen_width, screen_height = self.width(), self.height()

        portraitMargin = 30
        # portrait
        if screen_width < screen_height:
            global numCols, numRows
            numRows = 3
            numCols = 2
            portraitMargin = 15

        global imageWidth, imageHeight
        margin = 30
        imageWidth = (screen_width - (numCols - 1) * margin) // numCols
        imageHeight = (screen_height - (numRows - 1) * margin) // numRows - portraitMargin

        global gridItems
        gridItems = [[GridItem(self) for col in range(numCols)] for row in range(numRows)]

        # Create a grid of widgets
        for row in range(numRows):
            for col in range(numCols):
                widget = gridItems[row][col]
                widget.SetPosition(row, col)
                imagePickProbability = interp(row + 0.7, [0, numRows], [0, 1])
                imageSimilarity = interp(col + 0.5, [0, numCols], [1, 0])
                widget.SetImageParameters(imagePickProbability, imageSimilarity)
                self.bottom_layout.addWidget(widget, row + 1, col)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main = Main()
    main.show()
    sys.exit(app.exec_())