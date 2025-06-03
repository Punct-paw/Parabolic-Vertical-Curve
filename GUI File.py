### Explanation of the Code Line by Line

This code creates a simpler GUI than the previous version, focusing on core functionality: input fields, basic outputs (PVC and PVT), and a minimal curve visualization. Below, I’ll explain each line to help you understand, keeping it beginner-friendly.

#### Imports
```python
import sys
```
- **What it does**: Imports the `sys` module, which helps the program interact with the operating system (e.g., to exit the application).
- **Why**: Needed to run the PyQt6 application and handle system-level operations.

```python
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QFormLayout, QLineEdit, QPushButton, QLabel
```
- **What it does**: Imports specific classes from PyQt6’s widget module.
  - `QApplication`: Manages the entire GUI application.
  - `QMainWindow`: The main window of the app.
  - `QWidget`: A basic container for other widgets.
  - `QVBoxLayout`: Arranges widgets vertically.
  - `QFormLayout`: Creates a form with labels and input fields.
  - `QLineEdit`: A text box for user input.
  - `QPushButton`: A clickable button.
  - `QLabel`: A text label to display information.
- **Why**: These are the building blocks for creating the GUI.

```python
from PyQt6.QtGui import QPainter, QPen, QColor
```
- **What it does**: Imports tools for drawing.
  - `QPainter`: Used to draw shapes (like lines and points) on the canvas.
  - `QPen`: Defines how lines and points look (color, thickness).
  - `QColor`: Specifies colors for drawing.
- **Why**: Needed to draw the curve and points on the canvas.

```python
from PyQt6.QtCore import Qt
```
- **What it does**: Imports `Qt`, which contains constants like colors (e.g., `Qt.GlobalColor.white`) and alignment options.
- **Why**: Used to set colors and other properties in the GUI.

```python
from parabolic import VerticalParabolicCurve, VerticalPoint
```
- **What it does**: Imports the `VerticalParabolicCurve` and `VerticalPoint` classes from your `parabolic.py` file.
- **Why**: Allows the GUI to use your curve calculations and point definitions.

#### CurveCanvas Class
This class creates a canvas to draw the curve and key points.

```python
class CurveCanvas(QWidget):
```
- **What it does**: Defines a new class `CurveCanvas` that inherits from `QWidget`, making it a custom widget for drawing.
- **Why**: We need a special area to draw the curve visually.

```python
    def __init__(self, curve, parent=None):
```
- **What it does**: The constructor (initializer) for `CurveCanvas`. Takes a `curve` (your `VerticalParabolicCurve` object) and an optional `parent` widget.
- **Why**: Sets up the canvas with the curve data it will display.

```python
        super().__init__(parent)
```
- **What it does**: Calls the parent class (`QWidget`) constructor to initialize the widget.
- **Why**: Ensures the widget is properly set up as a PyQt6 widget.

```python
        self.curve = curve
```
- **What it does**: Stores the `curve` object in the canvas for use in drawing.
- **Why**: The canvas needs access to the curve’s data (like PVC, PVT) to draw it.

```python
        self.setMinimumSize(300, 200)
```
- **What it does**: Sets the minimum size of the canvas to 300 pixels wide and 200 pixels tall.
- **Why**: Ensures the canvas is large enough to show the curve clearly.

```python
    def paintEvent(self, event):
```
- **What it does**: Defines a special method that PyQt6 calls automatically when the widget needs to be drawn (e.g., when the window opens or is refreshed).
- **Why**: This is where we put all the drawing code for the curve.

```python
        painter = QPainter(self)
```
- **What it does**: Creates a `QPainter` object to draw on this widget.
- **Why**: The painter is like a paintbrush that draws lines, points, and text.

```python
        painter.fillRect(self.rect(), Qt.GlobalColor.white)
```
- **What it does**: Fills the entire canvas with a white background.
- **Why**: Clears the canvas and sets a clean background before drawing.

```python
        if not self.curve._data.is_initialized:
            return
```
- **What it does**: Checks if the curve is initialized (has valid data). If not, it exits the method.
- **Why**: Prevents drawing if the curve isn’t ready (e.g., before the user clicks "Calculate").

```python
        width = self.width()
        height = self.height()
```
- **What it does**: Gets the current width and height of the canvas.
- **Why**: Needed to scale the drawing to fit the canvas size.

```python
        pvc = self.curve.PVC
        pvt = self.curve.PVT
```
- **What it does**: Gets the PVC (start) and PVT (end) points of the curve.
- **Why**: These points define the curve’s range for drawing.

```python
        min_station = pvc.station
        max_station = pvt.station
```
- **What it does**: Sets the minimum and maximum station values (horizontal range) based on PVC and PVT.
- **Why**: Defines the x-axis range for the curve.

```python
        min_elev = min(pvc.elevation, pvt.elevation) - 5
        max_elev = max(pvc.elevation, pvt.elevation) + 5
```
- **What it does**: Finds the minimum and maximum elevations, adding a 5-unit buffer for better display.
- **Why**: Defines the y-axis range, ensuring all points fit with some padding.

```python
        x_scale = (width - 40) / (max_station - min_station)
        y_scale = (height - 40) / (max_elev - min_elev)
```
- **What it does**: Calculates scaling factors to convert curve coordinates (stations, elevations) to canvas pixels, leaving a 20-pixel margin on each side.
- **Why**: Scales the curve to fit the canvas size.

```python
        def to_screen(station, elevation):
            x = 20 + (station - min_station) * x_scale
            y = height - 20 - (elevation - min_elev) * y_scale
            return x, y
```
- **What it does**: Defines a helper function to convert curve coordinates (station, elevation) to canvas coordinates (x, y).
- **Why**: Maps real-world curve data to pixel positions on the screen. The y-coordinate is flipped (height - y) because the canvas’s y-axis increases downward.

```python
        painter.setPen(QPen(Qt.GlobalColor.blue, 2))
```
- **What it does**: Sets the drawing pen to blue with a thickness of 2 pixels.
- **Why**: Prepares to draw the curve in blue.

```python
        points = []
        for i in range(50):
            station = min_station + (max_station - min_station) * i / 49
            elev = self.curve.elevation_at(station)
            x, y = to_screen(station, elev)
            points.append((x, y))
```
- **What it does**: Creates a list of 50 points along the curve by calculating stations between PVC and PVT, getting their elevations using `elevation_at`, and converting to canvas coordinates.
- **Why**: Generates points to draw a smooth curve by connecting them.

```python
        for i in range(len(points) - 1):
            painter.drawLine(int(points[i][0]), int(points[i][1]), int(points[i+1][0]), int(points[i+1][1]))
```
- **What it does**: Draws lines between consecutive points to form the curve.
- **Why**: Connects the points to visualize the parabolic curve.

```python
        painter.setPen(QPen(Qt.GlobalColor.red, 5))
```
- **What it does**: Changes the pen to red with a thickness of 5 pixels.
- **Why**: Prepares to draw the PVC and PVT points.

```python
        for point in [pvc, pvt]:
            x, y = to_screen(point.station, point.elevation)
            painter.drawPoint(int(x), int(y))
```
- **What it does**: Draws red points at the PVC and PVT locations.
- **Why**: Highlights the start and end points of the curve.

```python
        painter.setPen(QPen(Qt.GlobalColor.black, 1))
```
- **What it does**: Sets the pen to black with a thickness of 1 pixel.
- **Why**: Prepares to draw the legend text.

```python
        painter.drawText(width - 80, 20, "Blue: Curve")
        painter.drawText(width - 80, 40, "Red: PVC/PVT")
```
- **What it does**: Draws two lines of text in the top-right corner as a legend.
- **Why**: Explains that blue lines represent the curve and red dots represent PVC/PVT points.

#### VerticalCurveGUI Class
This class creates the main window with input fields, a button, output labels, and the canvas.

```python
class VerticalCurveGUI(QMainWindow):
```
- **What it does**: Defines the main window class, inheriting from `QMainWindow`.
- **Why**: Creates the main application window.

```python
    def __init__(self):
```
- **What it does**: The constructor for the main window.
- **Why**: Sets up the window and its contents.

```python
        super().__init__()
```
- **What it does**: Calls the parent class (`QMainWindow`) constructor.
- **Why**: Initializes the window properly.

```python
        self.setWindowTitle("Simple Curve Calculator")
```
- **What it does**: Sets the window’s title to “Simple Curve Calculator.”
- **Why**: Gives the window a descriptive name.

```python
        self.setGeometry(100, 100, 500, 400)
```
- **What it does**: Sets the window’s position (100 pixels from top-left) and size (500x400 pixels).
- **Why**: Positions and sizes the window on the screen.

```python
        self.curve = VerticalParabolicCurve()
```
- **What it does**: Creates a new `VerticalParabolicCurve` object.
- **Why**: The GUI needs a curve object to calculate and display data.

```python
        self.setup_ui()
```
- **What it does**: Calls a method to set up the user interface.
- **Why**: Organizes the setup code in a separate method for clarity.

```python
    def setup_ui(self):
```
- **What it does**: Defines a method to create the GUI layout and widgets.
- **Why**: Keeps the UI setup separate from the constructor.

```python
        main_widget = QWidget()
```
- **What it does**: Creates a container widget to hold all other widgets.
- **Why**: The main window needs a central widget to organize the layout.

```python
        self.setCentralWidget(main_widget)
```
- **What it does**: Sets `main_widget` as the main content area of the window.
- **Why**: Tells PyQt6 where to place the layout.

```python
        layout = QVBoxLayout()
```
- **What it does**: Creates a vertical layout to arrange widgets top-to-bottom.
- **Why**: Organizes the form and canvas vertically.

```python
        main_widget.setLayout(layout)
```
- **What it does**: Assigns the vertical layout to the main widget.
- **Why**: Connects the layout to the widget.

```python
        form_layout = QFormLayout()
```
- **What it does**: Creates a form layout for input fields and labels.
- **Why**: Makes it easy to align labels with input boxes.

```python
        self.pvi_station = QLineEdit("1000.0")
        self.pvi_elevation = QLineEdit("100.0")
        self.g1 = QLineEdit("0.02")
        self.g2 = QLineEdit("-0.03")
        self.length = QLineEdit("200.0")
```
- **What it does**: Creates text input fields with default values (e.g., PVI station = 1000.0).
- **Why**: Allows users to enter curve parameters.

```python
        self.calculate_button = QPushButton("Calculate")
```
- **What it does**: Creates a button labeled “Calculate.”
- **Why**: Lets users trigger the curve calculation.

```python
        self.calculate_button.clicked.connect(self.calculate)
```
- **What it does**: Links the button’s click event to the `calculate` method.
- **Why**: Makes the button call the `calculate` method when clicked.

```python
        form_layout.addRow("PVI Station:", self.pvi_station)
        form_layout.addRow("PVI Elevation:", self.pvi_elevation)
        form_layout.addRow("Grade 1 (g1):", self.g1)
        form_layout.addRow("Grade 2 (g2):", self.g2)
        form_layout.addRow("Curve Length:", self.length)
        form_layout.addRow(self.calculate_button)
```
- **What it does**: Adds input fields and the button to the form layout, each with a label.
- **Why**: Creates a neat form where each input has a descriptive label.

```python
        self.pvc_label = QLabel("PVC: Not calculated")
        self.pvt_label = QLabel("PVT: Not calculated")
```
- **What it does**: Creates labels to display PVC and PVT results.
- **Why**: Shows the calculated results to the user.

```python
        form_layout.addRow(self.pvc_label)
        form_layout.addRow(self.pvt_label)
```
- **What it does**: Adds the output labels to the form layout.
- **Why**: Places the results below the inputs.

```python
        layout.addLayout(form_layout)
```
- **What it does**: Adds the form layout to the main vertical layout.
- **Why**: Integrates the form into the main window.

```python
        self.canvas = CurveCanvas(self.curve)
```
- **What it does**: Creates a `CurveCanvas` widget, passing the curve object.
- **Why**: Adds the drawing area to the GUI.

```python
        layout.addWidget(self.canvas)
```
- **What it does**: Adds the canvas to the main vertical layout.
- **Why**: Places the canvas below the form in the window.

```python
    def calculate(self):
```
- **What it does**: Defines the method called when the “Calculate” button is clicked.
- **Why**: Handles the curve calculation and updates the GUI.

```python
        try:
```
- **What it does**: Starts a block to catch errors (e.g., invalid inputs).
- **Why**: Prevents the program from crashing if the user enters bad data.

```python
            station = float(self.pvi_station.text())
            elevation = float(self.pvi_elevation.text())
            g1 = float(self.g1.text())
            g2 = float(self.g2.text())
            length = float(self.length.text())
```
- **What it does**: Converts the text from input fields to numbers (floats).
- **Why**: Gets the user’s input as numbers to use in calculations.

```python
            self.curve.PVI = VerticalPoint(station, elevation)
            self.curve.g1 = g1
            self.curve.g2 = g2
            self.curve.Length = length
```
- **What it does**: Sets the curve’s PVI, grades, and length using the input values.
- **Why**: Updates the curve object with user data to perform calculations.

```python
            self.pvc_label.setText(f"PVC: Station {self.curve.PVC.station:.2f}, Elevation {self.curve.PVC.elevation:.2f}")
            self.pvt_label.setText(f"PVT: Station {self.curve.PVT.station:.2f}, Elevation {self.curve.PVT.elevation:.2f}")
```
- **What it does**: Updates the output labels with the calculated PVC and PVT values, formatted to 2 decimal places.
- **Why**: Shows the results to the user.

```python
            self.canvas.update()
```
- **What it does**: Tells the canvas to redraw itself.
- **Why**: Updates the curve visualization with the new calculations.

```python
        except ValueError:
            self.pvc_label.setText("Error: Invalid input")
            self.pvt_label.setText("")
            self.canvas.update()
```
- **What it does**: If an error occurs (e.g., user enters letters instead of numbers), it shows an error message and clears the other label and canvas.
- **Why**: Handles invalid inputs gracefully.

#### Main Execution
```python
if __name__ == '__main__':
```
- **What it does**: Checks if the script is being run directly (not imported as a module).
- **Why**: Ensures the following code runs only when you execute this file.

```python
    app = QApplication(sys.argv)
```
- **What it does**: Creates the main application object, passing command-line arguments.
- **Why**: Initializes the PyQt6 application.

```python
    window = VerticalCurveGUI()
```
- **What it does**: Creates an instance of the main window.
- **Why**: Sets up the GUI window.

```python
    window.show()
```
- **What it does**: Displays the window on the screen.
- **Why**: Makes the GUI visible to the user.

```python
    sys.exit(app.exec())
```
- **What it does**: Starts the application’s event loop and exits when the window is closed.
- **Why**: Runs the GUI and handles user interactions until the program ends.

### How to Use
1. **Save the files**:
   - Save your original code as `parabolic.py`.
   - Save the above code as `vertical_curve_gui.py` in the same directory.
2. **Install PyQt6**: Run `pip install PyQt6` in your terminal or command prompt.
3. **Run the GUI**: Execute `python vertical_curve_gui.py`.
4. **Interact**:
   - Enter values in the text fields (e.g., PVI Station: 1000, PVI Elevation: 100, g1: 0.02, g2: -0.03, Length: 200).
   - Click “Calculate” to see the PVC and PVT values and the curve drawn on the canvas.
   - If you enter invalid data (e.g., letters), it will show “Error: Invalid input.”

### What’s Simplified
- **Fewer outputs**: Only shows PVC and PVT, skipping curve type and high/low point to reduce complexity.
- **Basic visualization**: Draws the curve and PVC/PVT points without axes or high/low point.
- **Minimal legend**: Just text explaining the curve (blue) and points (red).
- **Smaller canvas**: Reduced size for simplicity.
- **Fewer points**: Uses 50 points to draw the curve (instead of 100) to lighten the load.

This code is beginner-friendly, focusing on core functionality while still providing a functional GUI. Let me know if you need further clarification or want to add specific features!