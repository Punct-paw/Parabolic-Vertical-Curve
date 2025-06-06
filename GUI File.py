import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QFormLayout, QLineEdit, QPushButton, QLabel
from PyQt6.QtGui import QPainter, QPen, QColor
from PyQt6.QtCore import Qt
from parabolic import VerticalParabolicCurve, VerticalPoint, VerticalCurveType

class CurveCanvas(QWidget):
    def __init__(self, curve, parent=None):
        super().__init__(parent)
        self.curve = curve
        self.calc_station = None
        self.calc_elevation = None
        self.setMinimumSize(400, 400)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), Qt.GlobalColor.white)

        if not self.curve._data.is_initialized:
            return

        width = self.width()
        height = self.height()
        pvc = self.curve.PVC
        pvt = self.curve.PVT
        pvi = self.curve.PVI
        high_low = self.curve.High_low_point

        # Determine plot ranges
        min_station = pvc.station - 0.1 * (pvt.station - pvc.station)
        max_station = pvt.station + 0.1 * (pvt.station - pvc.station)
        elevations = [self.curve.elevation_at(pvc.station + i * (pvt.station - pvc.station) / 49) for i in range(50)]
        if high_low:
            elevations.append(high_low.elevation)
        if self.calc_elevation is not None:
            elevations.append(self.calc_elevation)
        elevations.append(pvi.elevation)  # Include PVI elevation
        min_elev = min(elevations) - 0.1 * (max(elevations) - min(elevations))
        max_elev = max(elevations) + 0.1 * (max(elevations) - min(elevations))

        x_scale = (width - 100) / (max_station - min_station)
        y_scale = (height - 100) / (max_elev - min_elev) * 1.2  # Stretch y-axis for taller curve

        def to_screen(station, elevation):
            x = 50 + (station - min_station) * x_scale
            y = height - 50 - (elevation - min_elev) * y_scale
            return x, y

        # Draw axes
        painter.setPen(QPen(Qt.GlobalColor.black, 1))
        x_axis_y = height - 50
        y_axis_x = 50
        painter.drawLine(y_axis_x, 50, y_axis_x, x_axis_y)
        painter.drawLine(y_axis_x, x_axis_y, width - 50, x_axis_y)
        painter.drawText(width - 80, x_axis_y + 30, "Station")
        painter.drawText(y_axis_x - 40, 30, "Elevation")

        # Draw x-axis ticks (station)
        num_x_ticks = 5
        station_step = (max_station - min_station) / num_x_ticks
        for i in range(num_x_ticks + 1):
            station = min_station + i * station_step
            x, _ = to_screen(station, min_elev)
            painter.drawLine(int(x), x_axis_y - 5, int(x), x_axis_y + 5)
            painter.drawText(int(x) - 20, x_axis_y + 20, f"{station:.0f}")

        # Draw y-axis ticks (elevation)
        num_y_ticks = 5
        elev_step = (max_elev - min_elev) / num_y_ticks
        for i in range(num_y_ticks + 1):
            elev = min_elev + i * elev_step
            _, y = to_screen(min_station, elev)
            painter.drawLine(y_axis_x - 5, int(y), y_axis_x + 5, int(y))
            painter.drawText(y_axis_x - 40, int(y) + 5, f"{elev:.1f}")

        # Draw curve (connects PVC and PVT)
        painter.setPen(QPen(Qt.GlobalColor.blue, 2))
        points = []
        for i in range(50):
            station = pvc.station + (pvt.station - pvc.station) * i / 49
            elev = self.curve.elevation_at(station)
            x, y = to_screen(station, elev)
            points.append((x, y))
        for i in range(len(points) - 1):
            painter.drawLine(int(points[i][0]), int(points[i][1]), int(points[i+1][0]), int(points[i+1][1]))

        # Draw points (larger dots)
        painter.setPen(QPen(Qt.GlobalColor.red, 8))
        x, y = to_screen(pvc.station, pvc.elevation)
        painter.drawPoint(int(x), int(y))
        x, y = to_screen(pvt.station, pvt.elevation)
        painter.drawPoint(int(x), int(y))
        painter.setPen(QPen(Qt.GlobalColor.green, 8))
        x, y = to_screen(pvi.station, pvi.elevation)
        painter.drawPoint(int(x), int(y))
        if high_low:
            painter.setPen(QPen(Qt.GlobalColor.magenta, 8))
            x, y = to_screen(high_low.station, high_low.elevation)
            painter.drawPoint(int(x), int(y))
        if self.calc_station is not None and self.calc_elevation is not None:
            painter.setPen(QPen(Qt.GlobalColor.black, 8))
            x, y = to_screen(self.calc_station, self.calc_elevation)
            painter.drawPoint(int(x), int(y))

        # Draw legend (corrected colors)
        legend_x, legend_y = width - 100, 20
        painter.setPen(QPen(Qt.GlobalColor.blue, 2))
        painter.drawLine(legend_x - 20, legend_y - 5, legend_x - 10, legend_y - 5)
        painter.setPen(QPen(Qt.GlobalColor.black, 1))
        painter.drawText(legend_x, legend_y, "Blue: Curve")
        painter.setPen(QPen(Qt.GlobalColor.red, 8))
        painter.drawPoint(legend_x - 15, legend_y + 15)
        painter.setPen(QPen(Qt.GlobalColor.black, 1))
        painter.drawText(legend_x, legend_y + 20, "Red: PVC/PVT")
        painter.setPen(QPen(Qt.GlobalColor.green, 8))
        painter.drawPoint(legend_x - 15, legend_y + 35)
        painter.setPen(QPen(Qt.GlobalColor.black, 1))
        painter.drawText(legend_x, legend_y + 40, "Green: PVI")
        painter.setPen(QPen(Qt.GlobalColor.magenta, 8))
        painter.drawPoint(legend_x - 15, legend_y + 55)
        painter.setPen(QPen(Qt.GlobalColor.black, 1))
        painter.drawText(legend_x, legend_y + 60, "Magenta: High/Low")
        painter.setPen(QPen(Qt.GlobalColor.black, 8))
        painter.drawPoint(legend_x - 15, legend_y + 75)
        painter.setPen(QPen(Qt.GlobalColor.black, 1))
        painter.drawText(legend_x, legend_y + 80, "Black: Calc Point")

class VerticalCurveGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Vertical Parabolic Curve Calculator")
        self.setGeometry(100, 100, 600, 600)
        self.curve = VerticalParabolicCurve()
        self.setup_ui()

    def setup_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout()
        main_widget.setLayout(layout)
        form_layout = QFormLayout()

        # Input fields
        self.pvi_station = QLineEdit("1000.0")
        self.pvi_elevation = QLineEdit("100.0")
        self.g1 = QLineEdit("0.02")
        self.g2 = QLineEdit("-0.03")
        self.length = QLineEdit("200.0")
        self.calc_station = QLineEdit("1000.0")
        self.calculate_button = QPushButton("Calculate")
        self.calculate_button.clicked.connect(self.calculate)
        form_layout.addRow("PVI Station:", self.pvi_station)
        form_layout.addRow("PVI Elevation:", self.pvi_elevation)
        form_layout.addRow("Grade 1 (g1):", self.g1)
        form_layout.addRow("Grade 2 (g2):", self.g2)
        form_layout.addRow("Curve Length:", self.length)
        form_layout.addRow("Calc Station:", self.calc_station)
        form_layout.addRow(self.calculate_button)

        # Result labels
        self.pvc_label = QLabel("PVC: Not calculated")
        self.pvt_label = QLabel("PVT: Not calculated")
        self.pvi_label = QLabel("PVI: Not calculated")
        self.curve_type_label = QLabel("Curve Type: Not calculated")
        self.high_low_label = QLabel("High/Low Point: Not calculated")
        self.distance_label = QLabel("Distance to High/Low: Not calculated")
        self.elevation_label = QLabel("Elevation at Station: Not calculated")
        self.slope_label = QLabel("Slope at Station: Not calculated")
        form_layout.addRow(self.pvc_label)
        form_layout.addRow(self.pvt_label)
        form_layout.addRow(self.pvi_label)
        form_layout.addRow(self.curve_type_label)
        form_layout.addRow(self.high_low_label)
        form_layout.addRow(self.distance_label)
        form_layout.addRow(self.elevation_label)
        form_layout.addRow(self.slope_label)

        layout.addLayout(form_layout)
        self.canvas = CurveCanvas(self.curve)
        layout.addWidget(self.canvas)

    def calculate(self):
        try:
            station = float(self.pvi_station.text())
            elevation = float(self.pvi_elevation.text())
            g1 = float(self.g1.text())
            g2 = float(self.g2.text())
            length = float(self.length.text())
            calc_station = float(self.calc_station.text())

            self.curve.PVI = VerticalPoint(station, elevation)
            self.curve.g1 = g1
            self.curve.g2 = g2
            self.curve.Length = length

            self.pvc_label.setText(f"PVC: Station {self.curve.PVC.station:.2f}, Elevation {self.curve.PVC.elevation:.2f}")
            self.pvt_label.setText(f"PVT: Station {self.curve.PVT.station:.2f}, Elevation {self.curve.PVT.elevation:.2f}")
            self.pvi_label.setText(f"PVI: Station {self.curve.PVI.station:.2f}, Elevation {self.curve.PVI.elevation:.2f}")
            self.curve_type_label.setText(f"Curve Type: {self.curve.Curve_type.name if self.curve.Curve_type else 'None'}")
            high_low = self.curve.High_low_point
            self.high_low_label.setText(f"High/Low Point: ({high_low.station:.2f}, {high_low.elevation:.2f})" if high_low else "High/Low Point: None")
            distance = self.curve.distance_to_High_low_point()
            self.distance_label.setText(f"Distance to High/Low: {distance:.2f}" if distance is not None else "Distance to High/Low: None")
            calc_elevation = self.curve.elevation_at(calc_station)
            calc_slope = self.curve.slope_at(calc_station) * 100  # Convert to percentage
            self.elevation_label.setText(f"Elevation at Station: {calc_elevation:.2f}")
            self.slope_label.setText(f"Slope at Station: {calc_slope:.2f}%")
            self.canvas.calc_station = calc_station
            self.canvas.calc_elevation = calc_elevation
            self.canvas.update()
        except ValueError as e:
            self.pvc_label.setText(f"Error: {str(e)}")
            self.pvt_label.setText("")
            self.pvi_label.setText("")
            self.curve_type_label.setText("")
            self.high_low_label.setText("")
            self.distance_label.setText("")
            self.elevation_label.setText("")
            self.slope_label.setText("")
            self.canvas.calc_station = None
            self.canvas.calc_elevation = None
            self.canvas.update()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = VerticalCurveGUI()
    window.show()
    sys.exit(app.exec())
