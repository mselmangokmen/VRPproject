
from ctypes import c_bool

class myNode:
  def __init__(self,id,name,lon, lat,X,Y,doluluk,merkezmi):
    self.id = id
    self.name=name
    self.lon = lon # longitute
    self.lat = lat # latitude
    self.X=X
    self.Y=Y
    self.orjDoluluk=doluluk

