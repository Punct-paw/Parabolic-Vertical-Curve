from enum import Enum
from dataclasses import dataclass
from typing import Optional

class VerticalCurveType(Enum):
    "Enum for determining whether the curve is sag or crest"
    Sag=0
    Crest=1


@dataclass
# Purpose: Represents a point with a station (distance along the road) and elevation (height).
# distance_to: Calculates the horizontal distance between two points (ignores elevation)
class VerticalPoint:
    "Represent a point in a vertical profile with station and elevation"
    station:float=0.0
    elevation:float=0.0

    def distance_to(self, other:float) -> float:
        'Calculate the absolute horizontal distance to another station'
        return abs(self.station-other.station)

@dataclass
class TVerticalCurve:
    #Data structure for vertical parabolic curve properties
    g1:float=0.0    #Incoming grade (as a decimal) e.g. 0.02 for 2%
    g2:float=0.0    # Outgoing grade (as a decimal) e.g. -0.03 for -3%
    Length:float=0.0    #Horizontal length of the curve
    PVI:Optional[VerticalPoint]=None    #Point of Vertical Intersection
    PVC:Optional[VerticalPoint]=None    #Point of Vertical Curvature
    PVT:Optional[VerticalPoint]=None    #Point of Vertical Tangency
    Curve_type:Optional[VerticalCurveType]=None     #Crest or Sag
    High_low_point: Optional[VerticalPoint]=None     # HIgh or Low point
    is_initialized: bool=False

class VerticalParabolicCurve:
    # Models a vertical parabolic curve for the roadway vertical alignment

    #Initialize a new vertical parabolic curve with default values
    def __init__(self):
        self._data=TVerticalCurve(PVI=VerticalPoint(),PVC=VerticalPoint(), PVT=VerticalPoint(), High_low_point=VerticalPoint(), is_initialized=False)
    
    @property
    def PVC(self) ->VerticalPoint:
        "Get the point of vertical curvature (start of the curve)"
        return self._data.PVC
    
    @property
    def PVT(self)   ->VerticalPoint:
        "Get the point of vertical tangency"
        return self._data.PVT

    @property
    def PVI(self) ->VerticalPoint:
        "Get the point of vertical intersection"
        return self._data.PVI

    @PVI.setter
    def PVI(self, value:VerticalPoint) ->VerticalPoint:
        "Set the PVI and update the curve if possible"
        if value is None:
            raise ValueError("PVI cannot be None")
        self._data.PVI=value
        if self._data.Length>0 and self._data.g1 !=0 and self._data.g2 !=0:
            self._update_curve()

    @property
    def g1(self) ->float:
        "Get the incoming grade"
        return self._data.g1
    
    @g1.setter
    def g1(self, value:float) ->float:
        "Set the incoming grade and update the curve if possible"
        self._data.g1 = value
        if self._data.PVI is not None and self._data.Length>0 and self._data.g2!=0:
            self._update_curve()

    @property
    def g2(self) ->float:
        "Get the incoming grade"
        return self._data.g2
    
    @g2.setter
    def g2(self, value:float) ->float:
        "Set the incoming grade and update the curve if possible"
        self._data.g2 = value
        if self._data.PVI is not None and self._data.Length>0 and self._data.g1!=0:
            self._update_curve()
        
    @property
    def Length(self) ->float:
        "Get the horizontal length of the curve"
        return self._data.Length
    
    @Length.setter
    def Length(self, value:float) ->float:
        "Set the horizontal length of the curve and update the curve if possible"
        self._data.Length = value
        if self._data.PVI is not None and self._data.g2!=0 and self._data.g1!=0:
            self._update_curve()

    @property
    def Curve_type(self) ->VerticalCurveType:
        "Get the curve type (crest or sag)"
        return self._data.Curve_type
    
    @property
    def High_low_point(self) ->VerticalPoint:
        'Get the high or low point of the curve'
        return self._data.High_low_point
    
    def elevation_at(self,station:float) ->float:
        'Calculate the elevation at a given station along the curve'
        if not self._data.is_initialized:
            raise ValueError("Curve not initialized")
        if station< self._data.PVC.station or station> self._data.PVT.station:
            raise ValueError("Station must be within the curve length")
        
        return (self._data.g2-self._data.g1)/(2*self._data.Length)*(station-self._data.PVC.station)**2+self._data.g1*(station-self._data.PVC.station)+self._data.PVC.elevation
    
    def slope_at(self,station:float) ->float:
        'Calculate the elevation at a given station along the curve'
        if not self._data.is_initialized:
            raise ValueError("Curve not initialized")
        if station< self._data.PVC.station or station> self._data.PVT.station:
            raise ValueError("Station must be within the curve length")
        
        return (self._data.g2-self._data.g1)/(self._data.Length)*(station-self._data.PVC.station)+self._data.g1


    
    def distance_to_High_low_point(self)    ->float:
        'Calculate the horizontal distance from PVC to high/low point (if it exists)'
        if not self._data.is_initialized:
            raise ValueError("Curve not initialized")
        if self._data.High_low_point is None:
            return None
        return self._data.High_low_point.station-self._data.PVC.station
    

    def projectpoint_at(self,point:VerticalPoint) ->VerticalPoint:
        'Project a point onto the curve by finding the closest point'
        if not self._data.is_initialized:
            raise ValueError("Curve not initialized")
        if point is None:
            raise ValueError("Point cannot be none")
        
        if point.station<=self._data.PVC.station:
            return VerticalPoint(self._data.PVC.station,self._data.PVC.elevation)
        elif point.station>=self._data.PVT.station:
            return VerticalPoint(self._data.PVT.station,self._data.PVT.elevation)
        else:
            return VerticalPoint(point.station,self.elevation_at(point.station))

    def create_offset_curve(self, offset: float) -> 'VerticalParabolicCurve':
        """Create a parallel vertical curve offset vertically."""
        if not self._data.is_initialized:
            raise ValueError("Curve not initialized")

        offset_curve = VerticalParabolicCurve()
        offset_curve.PVI = VerticalPoint(self._data.PVI.station, self._data.PVI.elevation + offset)
        offset_curve.Length = self._data.length
        offset_curve.g1 = self._data.g1
        offset_curve.g2 = self._data.g2
        offset_curve._update_curve()
        return offset_curve

    def _update_curve(self):
        'Update all the geometric properties and points'
        self._update_PVC()
        self._update_PVT()
        self._update_CurveType()
        self._data.is_initialized=True

        self._update_high_low_point()
        self._data.is_initialized=True

    def _update_PVC(self):
        'Calculate the PVC based on PVI, Length, and the Grades'
        PVC_station=self._data.PVI.station-self._data.Length/2
        PVC_elevation=self._data.PVI.elevation-self._data.g1*self._data.Length/2
        self._data.PVC=VerticalPoint(PVC_station, PVC_elevation)

    def _update_PVT(self):
        'Calculate the PVT based on PVI, Length, and the Grades'
        PVT_station=self._data.PVI.station+self._data.Length/2
        PVT_elevation=self._data.PVI.elevation+self._data.g2*self._data.Length/2
        self._data.PVT=VerticalPoint(PVT_station, PVT_elevation)

    def _update_CurveType(self):
        'Determine if the curve is a sag or crest type'
        a=abs(self._data.g2)-abs(self._data.g1)
        if a>0 :
            self._data.Curve_type=VerticalCurveType.Sag
        else:
            self._data.Curve_type=VerticalCurveType.Crest

    def _update_high_low_point(self):
        'Calculate the high or low point of the curve based on Length, and the Grades'
        a=self._data.g2-self._data.g1
        if a==0:
            self._data.High_low_point= None
            self._data.is_initialized = True  # Still mark as initialized
            return
        X=-(self._data.g1/a)*self._data.Length
        if 0<=X<=self._data.Length:
            station=self._data.PVC.station+X
            elevation=self.elevation_at(station)
            self._data.High_low_point=VerticalPoint(station,elevation)
        else:
            self._data.High_low_point=None
            self._data.is_initialized = True  # Still mark as initialized
