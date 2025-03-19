from PyQt6.QtWidgets import (QApplication, QWidget,
        QVBoxLayout, QPushButton, QLabel, QLineEdit,
          QProgressBar, QFileDialog, QHBoxLayout, 
          QGridLayout, QStackedWidget, QSizePolicy, 
          QSpacerItem, QComboBox, QMessageBox,QInputDialog)
from PyQt6.QtCore import pyqtSlot,QRegularExpression, Qt, QDir
from PyQt6.QtGui import QImage, QPixmap, QRegularExpressionValidator

import pandas as pd
import sys
import pickle
import os
os.environ['QT_QPA_PLATFORM'] = 'xcb'

# Imports for MainWindow 
from CentralNode import CentralNode
import FunctionHandler
import ImageHandler
import ModelHandler

class MainWindow(QWidget):
    """
    The main window of the PyQt6 GUI application.

    This class sets up the main user interface (UI) for the application, including the layout and controls.
    It handles user interaction and connects buttons to specific functionalities such as loading CSV files, 
    selecting output folders, and building models. It also manages the progress bar and status label.

    Attributes:
        number_of_pages (int): The number of pages in the GUI (used for stacked widgets).
        current_control (int): The index of the current page being displayed in the GUI.
        controlStack (QStackedWidget): Stack widget used to manage different pages.
        Image_Display1 (QLabel): Label for displaying images.
        load_csv_button (QPushButton): Button to load a CSV file.
        select_folder_button (QPushButton): Button to select an output folder.
        build_model_button (QPushButton): Button to trigger model building.
        progress_bar (QProgressBar): Progress bar to indicate task progress.
        status_label (QLabel): Label to display the current status message.
        next_button (QPushButton): Button to navigate to the next page when the task is complete.
    """

    def __init__(self):
        """
        Initializes the MainWindow and sets up the UI.

        This method sets the window title, size, and initializes the layout for the GUI.
        It also creates a stacked widget to manage multiple pages and prepares the initial layout.

        It does not take any parameters and sets up default values for essential attributes such as:
            - `number_of_pages`: The number of pages in the GUI.
            - `current_control`: The current page index (default is 0).
            - `controlStack`: A stacked widget to manage different pages.
        """
        super().__init__()
        self.setWindowTitle("PyQt6 GUI Template")
        self.setGeometry(0, 0, 1000, 800)
        self.number_of_pages = 3  # Number of pages in the GUI 
        self.current_control = 0  # Current page of the GUI
        self.controlStack = QStackedWidget(self)
        self.default_values={'n_clusters':10, 'filters': ['threshold_li', 'threshold_mean']}
        self.filter=self.default_values['filters'][1]
        self.init_ui()

    def init_ui(self):
        """
        Initializes the user interface of the application by setting up the layout
        and adding buttons, labels, and other UI elements to the window.
        """
        # Main Layout Setup
        self.outerLayout = QGridLayout()
        # self.displayLayout = QHBoxLayout()  # For image display (commented out)
        self.sidebuttonLayout = QVBoxLayout()  # For right-side buttons
        self.bottomPanelLayout = QHBoxLayout()  # For bottom buttons
        self.ButtonStack = QStackedWidget(self)  # Rotating button side panel
        self.SliderStack = QStackedWidget(self)  # Rotating slider bottom panel

        # Initializes connection to CentralNode
        self.Central_Connection = CentralNode(self)
        self.Central_Connection.update_image.connect(self.display_image)

        # Initialize new button stacks and add them to the layout
        self.init_new_button_stacks()
        self.sidebuttonLayout.addWidget(self.ButtonStack)
        self.bottomPanelLayout.addWidget(self.SliderStack)

        # Universal widgets
        ###################
        # Page navigation Button
        self.next_button = self.make_button('Next Page', self.update_control_stack)
        self.next_button.setVisible(False)
        self.outerLayout.addWidget(self.next_button, 0, 0, 1, 1, Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight)
        
        # Vertical spacer to adjust layout positioning
        verticalSpacer = QSpacerItem(10, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        self.outerLayout.addItem(verticalSpacer, 0, 0, 1, 0)

        # Image Display widget
        self.Image_Display1 = QLabel(self)  # Image display
        self.Image_Display1.setFixedSize(500, 500)
        self.outerLayout.addWidget(self.Image_Display1, 0, 0, 0, 0, Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignLeft)

        # Spacer to adjust layout
        verticalSpacer = QSpacerItem(200, 200, QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Expanding)
        self.outerLayout.addItem(verticalSpacer, 1, 1, 1, 0)

        # Add side button layout and bottom panel layout to the main layout
        self.outerLayout.addLayout(self.sidebuttonLayout, 0, 1, 1, 1)  # Right panel for buttons
        self.outerLayout.addLayout(self.bottomPanelLayout, 1, 0, 1, 2)  # Bottom panel for buttons

        # Set the main layout of the window
        self.setLayout(self.outerLayout)
        
        # Initially, show the first page
        self.controlStack.setCurrentIndex(0)


    # UI Helper Functions
    #####################

    def init_new_button_stacks(self):
        """
        Initializes the button stacks for each page (page1, page2, page3).
        """
        self.init_page1()
        self.init_page2()
        self.init_page3()

    def update_control_stack(self):
        """
        Updates the current set of pages and controls for the stacked widget.
        Moves to the next page and updates button visibility accordingly.
        """
        self.current_control += 1
        self.next_button.setVisible(False)

        if self.current_control >= self.number_of_pages:
            # Show the last page
            self.ButtonStack.setCurrentIndex(self.number_of_pages)
            self.SliderStack.setCurrentIndex(self.number_of_pages)
            self.next_button.setVisible(False)
        else:
            self.ButtonStack.setCurrentIndex(self.current_control)
            self.SliderStack.setCurrentIndex(self.current_control)

    def make_button(self, name, action):
        """
        Creates a QPushButton, connects it to a specified action, and sets its size.

        Args:
            name (str): The text label of the button.
            action (function): The function to connect to the button's clicked signal.

        Returns:
            QPushButton: The created button widget.
        """
        button = QPushButton(name, self)
        button.clicked.connect(action)
        button.setFixedSize(100, 30)
        return button

    def progress_bar(self, Layout):
        """
        Creates and adds a progress bar widget to the specified layout.

        Args:
            Layout (QLayout): The layout to add the progress bar to.
        """
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setRange(0, 100)
        Layout.addWidget(self.progress_bar)
        
        self.status_label = QLabel('Status: Ready', self)
        Layout.addWidget(self.status_label)

    def image_display_visable(self):
        """
        Toggles the visibility of the image display widget.
        """
        if self.Image_Display1.isVisible():
            self.Image_Display1.setVisible(False)
        else:
            self.Image_Display1.setVisible(True)

    def display_image(self, image_data):
        """
        Receives image data from CentralNode and displays it in the image display widget.

        Args:
            image_data (QImage): The image data to be displayed.
        """
        pixmap = QPixmap.fromImage(image_data)
        self.Image_Display1.setPixmap(pixmap)
        self.next_button.setVisible(True)

    def filter_changed(self, filter_text):
        """
        Updates the current filter when the user selects a new one from the dropdown.

        Args:
            filter_text (str): The name of the selected filter.
        """
        self.filter = filter_text
        # Update the label (if needed)
        self.filter_label.setText(f"Thresholding function: {filter_text}")
        # In PyQt6, we use setCurrentText to change the displayed selected item
        self.filter_combo_box.setCurrentText(filter_text)


    ##### Page Initialization Functions ###########

    def init_page1(self):
        """
        Initializes the layout and widgets for page 1 of the application.
        Adds buttons and actions for selecting an image.
        
        Returns:
            QWidget: The layout widget for page 1.
        """
        self.page1_widget = QWidget()
        self.b1_page = QHBoxLayout()
        
        # Image selection button
        self.select_image_button = self.make_button('Select Image', self.load_image)
        self.b1_page.addWidget(self.select_image_button, alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight)
        
        self.page1_widget.setLayout(self.b1_page)
        self.ButtonStack.addWidget(self.page1_widget)
        return self.page1_widget

    def init_page2(self):
        """
        Initializes the layout and widgets for page 2 of the application.
        Adds a button for applying a filter and a dropdown for filter selection.

        Returns:
            QWidget: The layout widget for page 2.
        """
        self.page2_widget = QWidget()
        self.b2_page = QGridLayout()

        # Horizontal Spacer
        horizontalSpacer = QSpacerItem(20, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        self.b2_page.addItem(horizontalSpacer, 0, 0)

        # Filter button and label
        self.filter_button = self.make_button("Apply Filter", self.apply_filter)
        self.b2_page.addWidget(self.filter_button, 0, 1)
        intial_label = "Thresholding function: " + self.default_values['filters'][0]
        self.filter_label = QLabel(intial_label)
        self.b2_page.addWidget(self.filter_label, 2, 1)
        self.b2_page.setAlignment(self.filter_label, Qt.AlignmentFlag.AlignBottom)
        self.b2_page.setAlignment(self.filter_button, Qt.AlignmentFlag.AlignRight)

        # Filter combo box
        self.filter_combo_box = QComboBox(self)
        self.filter_combo_box.addItems(self.default_values['filters'])
        self.filter_combo_box.currentTextChanged.connect(self.filter_changed)
        self.b2_page.addWidget(self.filter_combo_box, 3, 1, 1, 0)
        self.b2_page.setAlignment(self.filter_combo_box, Qt.AlignmentFlag.AlignTop)
        self.filter_combo_box.setFixedSize(150, 30)

        self.page2_widget.setLayout(self.b2_page)
        self.ButtonStack.addWidget(self.page2_widget)
        return self.page2_widget

    def init_page3(self):
        """
        Initializes the layout and widgets for page 3 of the application.
        Adds a button for saving the image.

        Returns:
            QWidget: The layout widget for page 3.
        """
        self.page3_widget = QWidget()
        self.b3_page = QHBoxLayout()

        # Horizontal Spacer
        horizontalSpacer = QSpacerItem(20, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        self.b3_page.addItem(horizontalSpacer)

        # Save image button
        self.save_image_button = self.make_button('Save Image', self.save_single_image)
        self.b3_page.addWidget(self.save_image_button)
        self.b2_page.setAlignment(self.save_image_button, Qt.AlignmentFlag.AlignRight)

        self.page3_widget.setLayout(self.b3_page)
        self.ButtonStack.addWidget(self.page3_widget)
        return self.page3_widget

    def init_page4(self):
        """
        Initializes the layout and widgets for page 4 of the application.
        Adds input fields for entering the number of clusters and building the model.

        Returns:
            QWidget: The layout widget for page 4.
        """
        self.page4_widget = QWidget()
        self.b4_page = QHBoxLayout()
        
        # Clusters input field
        self.b4_page.addWidget(QLabel("Enter number of clusters: "))
        self.clusters_input = QLineEdit(self)
        self.clusters_input.setText(str(self.default_values["n_clusters"]))  
        self.clusters_input.setPlaceholderText("Enter Number of Clusters")
        regex = QRegularExpression(r"^[0-9]*$")  # Allows only digits
        validator = QRegularExpressionValidator(regex)
        self.clusters_input.setValidator(validator)
        self.b4_page.addWidget(self.clusters_input)

        # Build model button
        self.build_model_button = self.make_button('Build Model', self.build_model)
        self.build_model_button.setVisible(False)  # Initially hidden
        self.bottomPanelLayout.addWidget(self.build_model_button)

        self.page4_widget.setLayout(self.b4_page)
        self.ButtonStack.addWidget(self.page4_widget)
        return self.page4_widget


    # Functions that communicate with other classes
    ###############################################

    @pyqtSlot(QImage)
    def displayImage(self, Image):
        """
        Slot function that is called when an image is received.

        Args:
            Image (QImage): The image to be displayed.
        """
        if Image.isNull():
            print("Invalid Image received!")
            return
        else:
            self.Image_Display1.setPixmap(QPixmap.fromImage(Image))

    @pyqtSlot()
    def load_image(self):
        """
        Opens a file dialog to load an image and sends it to the CentralNode for processing.
        """
        print("Loading image...") 
        file, _ = QFileDialog.getOpenFileName(self, "Open Image file", QDir.homePath(), "*.tif")
        if file:
            self.Central_Connection.load_image(file)
            self.select_image_button.setVisible(False)
            self.next_button.setVisible(True)

    @pyqtSlot()
    def apply_filter(self):
        """
        Applies the selected filter to the loaded image.
        """
        print('Applying filter')
        self.Central_Connection.apply_filter(self.filter)

    @pyqtSlot()
    def save_single_image(self):
        """
        Opens a file dialog to save the image to a specified file path.
        """
        file_path, _ = QFileDialog.getSaveFileName(self, 'Save Image', '', 'Image Files (*.png *.jpg *.bmp *.tiff);;All Files (*)')

        if file_path:  # If the user selected a path
            self.Central_Connection.save_single_image(file_path)         
        else:
            # If the user canceled or an invalid path is returned
            QMessageBox.warning(self, "Error", "Saving the image failed. No valid file path.")

    @pyqtSlot()
    def load_csv(self):
        """
        Opens a file dialog to load a CSV file and updates the UI with the selected file's path.
        """
        file, _ = QFileDialog.getOpenFileName(self, "Open CSV File", "", "CSV Files (*.csv)")
        if file:
            self.entries['Image sets to build'].setText(file)

    @pyqtSlot()
    def select_folder(self):
        """
        Opens a folder dialog to select a folder for saving model output.
        """
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder:
            self.entries['Model output folder'].setText(folder)

    @pyqtSlot()
    def update_controls(self):
        """
        Updates the controls in the CentralNode.
        """
        self.Central_Connection.update_controls()

    @ pyqtSlot()
    def build_model(self):
        """ To do: add communication to central node"""
        build_model = True
        csv = self.entries['Image sets to build'].text()
        entries = self.entries
        outpth = self.entries['Model output folder'].text() 
        self.worker = build_model
        self.worker.progress_changed.connect(self.update_progress)
        self.worker.status_updated.connect(self.update_status)
        self.worker.start()

    @ pyqtSlot()
    def update_progress(self, progress):
        """
        Updates the progress bar with the current progress value.

        This method receives the current progress value (an integer) from the worker thread and updates the progress bar
        accordingly.

        Args:
            progress (int): The current progress value (0 to 100).
        """
        self.progress_bar.setValue(progress)

    @ pyqtSlot()
    def update_status(self, status):
        """
        Updates the status label with a new status message.

        This method receives a status message from the worker thread and updates the status label to reflect the current 
        state of the process (e.g., "Modeling initiated", "Modeling completed").

        Args:
            status (str): The new status message to display."""
        self.status_label.setText(f"Status: {status}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
