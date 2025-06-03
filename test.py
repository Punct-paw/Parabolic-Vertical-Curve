import parabolic

def test_vertical_curve(pvi_station, pvi_elevation, length, g1, g2, station):
    print(f"\nTesting curve with PVI=({pvi_station}, {pvi_elevation}), Length={length}, G1={g1}, G2={g2}")
    curve=parabolic.VerticalParabolicCurve()
    curve.PVI=parabolic.VerticalPoint(station=pvi_station, elevation=pvi_elevation)
    curve.Length=length
    curve.g1=g1
    curve.g2=g2

    print(f"PVC: Station = {curve.PVC.station:.2f}, Elevation = {curve.PVC.elevation:.2f}")
    print(f"PVT: Station = {curve.PVT.station:.2f}, Elevation = {curve.PVT.elevation:.2f}")
    print(f"Elevation at station {station}: {curve.elevation_at(station):.5f}")
    print(f"Slope at station {station}: {curve.slope_at(station):.5f} ({curve.slope_at(station)*100:.2f}%)")

    distance=curve.distance_to_High_low_point()
    print(f"Distance to high/low point: {distance:.2f}" if distance is not None else "No high/low point")
    print(f"Curve type: {curve.Curve_type.name}")

if __name__=="__main__":
    #Test case 1
    test_vertical_curve(pvi_station=12000, pvi_elevation=135, length=1600, g1=0.0175, g2=-0.01, station=11360)