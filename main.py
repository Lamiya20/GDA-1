import sys
import matplotlib
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QAction, QFileDialog, QWidget, QHBoxLayout, QCheckBox, QLabel

matplotlib.use('Qt5Agg')

from PyQt5 import QtCore, QtGui, QtWidgets

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import pandas as pd
import sys

#New change
#New change 2
#New change 3
#New change 4
#Create the canvas in the PyQT for the plot/map
class MplCanvas(FigureCanvasQTAgg):

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        self.sc = MplCanvas(self, width=15, height=10, dpi=100)

        self.showStreet = 0
        self.showIntersection = 0
        self.showStreetName = 0

        self.filePath = ""

        self.graph()

        # Create toolbar, passing canvas as first parament, parent (self, the MainWindow) as second.
        toolbar = NavigationToolbar(self.sc, self)

        #Menubar at the top
        menubar = self.menuBar()
        fileMenu = menubar.addMenu('File')
        # self.resize(500, 500)

        #Set the Open Excel file and Exit button and their corresponding actions
        openAction = QAction('Open Excel File', self)
        openAction.triggered.connect(self.openExcel)
        fileMenu.addAction(openAction)

        closeAction = QAction('Exit', self)
        closeAction.triggered.connect(self.close)
        fileMenu.addAction(closeAction)


        #Set checkboxes, default to unchecked
        self.b1 = QCheckBox("Show streets")
        self.b1.setChecked(False)
        self.b1.stateChanged.connect(self.showStreetButton)

        self.b2 = QCheckBox("Show intersections")
        self.b2.setChecked(False)
        self.b2.stateChanged.connect(self.showIntersectionButton)

        self.b3 = QCheckBox("Show street names")
        self.b3.setChecked(False)
        self.b3.stateChanged.connect(self.showStreetNameButton)

        self.l1 = QLabel()
        self.l1.setText("Plot Options")



        layout = QtWidgets.QGridLayout()
        layout.addWidget(self.l1, 0, 0, 1, 1)
        layout.addWidget(self.b1, 0, 1, 1, 1)
        layout.addWidget(self.b2, 0, 2, 1, 1)
        layout.addWidget(self.b3, 0, 3, 1, 1)
        layout.addWidget(self.sc, 1, 0, 1, 4)
        layout.addWidget(toolbar, 2, 0, 1, 4, alignment=Qt.AlignCenter)





        # Create a placeholder widget to hold our toolbar and canvas.
        widget = QtWidgets.QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)
        self.setWindowTitle("Map Plotter")

        self.show()



    def openExcel(self):
        ExcelPath, _ = QFileDialog.getOpenFileName()
        if ExcelPath.split(".")[-1] == "xlsx":
            print(ExcelPath)
            self.filePath = ExcelPath
            self.subset_a, self.subset_b, self.df_road_int = self.processData()
            self.graph()
        else:
            print("Please select a valid excel file")
            self.openExcel()


    #Helper function for showing 3 different buttons for showing street,intersections and streetname
    def showStreetButton(self):
        print("show street")
        if self.showStreet == 0:
            self.showStreet = 1
        else:
            self.showStreet = 0
        self.graph()

    def showIntersectionButton(self):
        print("show intersection")
        if self.showIntersection == 0:
            self.showIntersection = 1
        else:
            self.showIntersection = 0
        self.graph()

    def showStreetNameButton(self):
        print("show street name")
        if self.showStreetName == 0:
            self.showStreetName = 1
        else:
            self.showStreetName = 0
        self.graph()

    def graph(self):
        if self.filePath == "":
            print("No file selected")
            return

        print(self.showStreet, self.showIntersection, self.showStreetName)

        # adding the subplot
        plot1 = self.sc

        self.sc.axes.clear()
        for index, row in self.df_road_int.iterrows():
            x_values = [row['X_x'], row['X_y']]
            y_values = [row['Y_x'], row['Y_y']]
            #Plot streets and intersections
            if self.showStreet == 1:
                self.sc.axes.plot(x_values, y_values, 'b', marker='.', linestyle="solid")
            x_avg = (row['X_x'] + row['X_y']) / 2
            y_avg = (row['Y_x'] + row['Y_y']) / 2
            #Show street name if set
            if self.showStreetName == 1:
                self.sc.axes.text(x_avg, y_avg, row['name'])
        #Show intersection Lights and Crosswalk information
        if self.showIntersection == 1:
            self.sc.axes.scatter(self.subset_a.X, self.subset_a.Y, s=120, c='r', label='Traffic Light')
            self.sc.axes.scatter(self.subset_b.X, self.subset_b.Y, marker='X', s=120, c='g', label='Crosswalk')
            self.sc.axes.legend()
        self.sc.draw()

    def processData(self):
        print(self.filePath)
        xls = pd.ExcelFile(self.filePath)
        print(xls.sheet_names)
        
        #Read 3 sheets from the excel file
        df1 = pd.read_excel(xls, 'Intersections')
        df2 = pd.read_excel(xls, 'InstalledFeatures')
        df3 = pd.read_excel(xls, 'Roads')

        
        #Merge different intersections and installedfeatures table on common field
        df_int_feat = pd.merge(df1, df2, left_on='ID', right_on='intersectionID')
        df_int_feat = df_int_feat.sort_values('FeatureID')
        df_int_feat = df_int_feat.drop(['Unnamed: 0_x', 'ID_x', 'Unnamed: 0_y', 'ID_y', 'intersectionID'], axis=1)

        cond = df_int_feat.FeatureID < 2
        self.subset_a = df_int_feat[cond].dropna()
        self.subset_b = df_int_feat[~cond].dropna()

        #Merge Roads and intersections table on commonn field
        self.df_road_int = pd.merge(df3, df1, left_on='startNodeID', right_on='ID')
        self.df_road_int = pd.merge(self.df_road_int, df1, left_on='endNodeID', right_on='ID')
        self.df_road_int = self.df_road_int.drop(
            ['Unnamed: 0_x', 'ID_x', 'Unnamed: 0_y', 'ID_y', 'startNodeID', 'endNodeID', 'Unnamed: 0'], axis=1)

        return self.subset_a, self.subset_b, self.df_road_int


app = QtWidgets.QApplication(sys.argv)
w = MainWindow()
app.exec_()
