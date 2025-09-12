#!BPY

"""
__author__= "Lauri Peltonen a.k.a. Zan (modified by J05HYYY to include textures)"
__version__= "0.1"
"""

import gzip
import math
import os
import sys
from struct import unpack

HAS_XML = False
try:
  import xml.dom.minidom   # To read materials.xml
  HAS_XML = True
except:
  HAS_XML = False

BOUNDINGSPHERE = 0
VERTEXLIST = 1
NORMALLIST = 2
TEXTURECOORDLIST = 3
COLORLIST = 4
POINTS = 9
TRIANGLES = 10
TRIANGLESTRIPS = 11
TRIANGLEFANS = 12

MATERIAL = 0
INDEX = 1

VERTICES = 0x01
NORMALS = 0x02
COLORS = 0x04
TEXCOORDS = 0x08

FG_ROOT = os.environ.get("FG_ROOT", "/usr/share/games/flightgear/")
MaterialList = { }

MaterialListRed = { }
MaterialListBlue = { }
MaterialListGreen = { }
MaterialListAlpha = { }

class BTG:
# Helper functions

  # Returns the tile width in degrees on current latitude
  def span(self, lat):
    lat = abs(lat)
    if lat >= 89: return 360
    elif lat >= 88: return 8
    elif lat >= 86: return 4
    elif lat >= 83: return 2
    elif lat >= 76: return 1
    elif lat >= 62: return 0.5
    elif lat >= 22: return 0.25
    elif lat >= 0: return 0.125
    return 360

  # Convert cartesian coordinates to geoidic
  def cartToGeod(self, x, y, z):
    lon = math.atan2(y, x)
    lat = pi/2 - math.atan2(math.sqrt(x*x+y*y), z)
    rad = math.sqrt(x*x+y*y+z*z)
    return (lon, lat, rad)

  # Convert geoidic coordinates to cartesian
  def geodToCart(self, lon, lat, rad):
    lon = (lon * math.pi) / 180
    lat = (lat * math.pi) / 180
    x = math.cos(lon) * math.cos(lat) * rad
    y = math.sin(lon) * math.cos(lat) * rad
    z = math.sin(lat) * rad
    return (x, y, z)


  def read_vertex(self, data):
    (vertex, ) = unpack("<H", data)
    self.faceidx.append(vertex)
    return

  def read_normal(self, data):
    (normal, ) = unpack("<H", data)
    self.normalidx.append(normal)
    return

  def read_color(self, data):
    (color, ) = unpack("<H", data)
    self.coloridx.append(color)
    return

  def read_texcoord(self, data):
    (texcoord, ) = unpack("<H", data)
    self.texcoordidx.append(texcoord)
    return
  

  def parse_property(self, objtype, proptype, data):
    # Only geometry objects may have properties
    # and they have type >= 9 (POINTS)
    if objtype >= POINTS:
      if proptype == MATERIAL:

        if not data in self.materials:
          self.materials.append(data)

        self.material = self.materials.index(data) + 1  # Make sure material is always > 0
        self.materialname = data

      elif proptype == INDEX:    
        (idx, ) = unpack("B", data[:1])
        self.readers = []
        if idx & VERTICES: self.readers.append(self.read_vertex)
        if idx & NORMALS: self.readers.append(self.read_normal)
        if idx & COLORS: self.readers.append(self.read_color)
        if idx & TEXCOORDS: self.readers.append(self.read_texcoord)

        if objtype == POINTS:
          self.readers = [self.read_vertex]

        if len(self.readers) == 0:
          self.readers = [self.read_vertex, self.read_texcoord]
    return

  def add_face(self, n1, n2, n3):
#    print("add face", n1,n2,n3)

    face = {}

    f = [0, 0, 0]
    f[0] = self.faceidx[n1]
    f[1] = self.faceidx[n2]
    f[2] = self.faceidx[n3]

    face["verts"] = f

    if self.material:
      face["material"] = [self.material - 1, self.materialname]

    #for n, ve in enumerate(v):
    #  if not ve in self.objvertices:
    #    self.objvertices.append(ve)
        # self.mesh.verts.extend([[ve["x"], ve["y"], ve["z"]]])
        # f[n] = len(self.mesh.verts) - 1
    #  else: 
    #    f[n] = self.objvertices.index(ve)
         
    #self.mesh.faces.extend([self.mesh.verts[f[0]], self.mesh.verts[f[1]], self.mesh.verts[f[2]]])

#    if len(self.normals) > 0:

    if not "material" in face:
      face["material"] = [0, "Default"]

    if self.material:
      texturepath = None

    totest=face["material"][1].decode('utf-8')

    if totest in MaterialList:
        texturepath = MaterialList[totest]
    if texturepath is not None:
        # Load texture
        if os.path.isfile(FG_ROOT + texturepath):
            face["image"]=FG_ROOT + "Textures.High/" + texturepath
            print("%s%s%s" % (FG_ROOT,"Textures.High/",texturepath))
        elif os.path.isfile(FG_ROOT + "Textures/" + texturepath):
            face["image"]=FG_ROOT + "Textures/" + texturepath
            print("%s%s%s" % (FG_ROOT,"Textures/",texturepath))

#      face["material"] = self.materials.index(self.material)
#      face["files"] = [self.material - 1, self.material]
    #  if len(self.mesh.faces)>0: self.mesh.faces[-1].mat = 0

#    if face["files"][1] in MaterialList:
#      texturepath = MaterialList[face["files"][1]]
#      if texturepath is not None:
#        # Load texture
#        if os.path.isfile(FG_ROOT + "Textures.High/" + texturepath):
#          face["image"]=FG_ROOT + "Textures.High/" + texturepath
#        elif os.path.isfile(FG_ROOT + "Textures/" + texturepath):
#          face["image"]=FG_ROOT + "Textures/" + texturepath

    if len(self.texcoordidx)>0:
      face["texcoords"] = [self.texcoordidx[n1], self.texcoordidx[n2], self.texcoordidx[n3]]

    if len(self.coloridx)>0:
      face["color"] = [self.coloridx[n1], self.coloridx[n2], self.coloridx[n3]]
      print(face["color"])

    self.faces.append(face)

    #  uv1 = Blender.Mathutils.Vector(self.texcoords[self.texcoordidx[n1]]["x"], self.texcoords[self.texcoordidx[n1]]["y"])
    #  uv2 = Blender.Mathutils.Vector(self.texcoords[self.texcoordidx[n2]]["x"], self.texcoords[self.texcoordidx[n2]]["y"])
    #  uv3 = Blender.Mathutils.Vector(self.texcoords[self.texcoordidx[n3]]["x"], self.texcoords[self.texcoordidx[n3]]["y"])
    #  if len(self.mesh.faces)>0: self.mesh.faces[-1].uv = (uv1, uv2, uv3)

    #if len(self.normalidx)>0:
    #  no1 = Blender.Mathutils.Vector(self.normals[self.normalidx[n1]]["x"], self.normals[self.normalidx[n1]]["y"], self.normals[self.normalidx[n1]]["z"])
    #  no2 = Blender.Mathutils.Vector(self.normals[self.normalidx[n2]]["x"], self.normals[self.normalidx[n2]]["y"], self.normals[self.normalidx[n2]]["z"])
    #  no3 = Blender.Mathutils.Vector(self.normals[self.normalidx[n3]]["x"], self.normals[self.normalidx[n3]]["y"], self.normals[self.normalidx[n3]]["z"])
      # no = (no1 + no2 + no3) / 3.0        # Calculate the mean value of the 3 vectors
      # Set normals to vectors instead of face?
    #  self.mesh.verts[f[0]].no = no1
    #  self.mesh.verts[f[1]].no = no2
    #  self.mesh.verts[f[2]].no = no3

    #if len(self.coloridx)>0:
    #  co1 = Blender.Mesh.MCol()
    #  co1.r = self.colors[self.coloridx[n1]]["red"]
    #  co1.g = self.colors[self.coloridx[n1]]["green"]
    #  co1.b = self.colors[self.coloridx[n1]]["blue"]
    #  co1.a = self.colors[self.coloridx[n1]]["alpha"]
    #  print(co1.r)

    if "color" in face:
        print(self.colors[self.coloridx[n1]]["red"])

    #  if len(self.mesh.faces)>0: self.mesh.faces[-1].col.extend([co1])

    return


  def parse_element(self, objtype, nbytes, data):
    if objtype == BOUNDINGSPHERE:
      (bs_x, bs_y, bs_z, bs_rad ) = unpack("<dddf", data[:28])
      self.boundingspheres.append({"x":bs_x, "y":bs_y, "z":bs_z, "radius":bs_rad})

    elif objtype == VERTEXLIST:
      scale_factor = float(os.environ.get("SCALE_FACTOR", "0.001"))

      for n in range(0, int(nbytes/12)):    # One vertex is 12 bytes (3 * 4 bytes)
        (v_x, v_y, v_z) = unpack("<fff", data[n*12:(n+1)*12])
        if scale_factor == 1:
            # No scaling required
            self.vertices.append({"x":v_x, "y":v_y, "z":v_z})
        else:
            self.vertices.append({"x":scale_factor*v_x, "y":scale_factor*v_y, "z":scale_factor*v_z})

    elif objtype == NORMALLIST:
      for n in range(0, int(nbytes/3)):    # One normal is 3 bytes ( 3 * 1 )
        (n_x, n_y, n_z) = unpack("BBB", data[n*3:(n+1)*3])
        self.normals.append({"x":n_x/127.5-1, "y":n_y/127.5-1, "z":n_z/127.5-1})

    elif objtype == TEXTURECOORDLIST:
      for n in range(0, int(nbytes/8)):    # One texture coord is 8 bytes ( 2 * 4 )
        (t_x, t_y) = unpack("<ff", data[n*8:(n+1)*8])
        self.texcoords.append({"x":t_x, "y":t_y})

    elif objtype == COLORLIST:
      print(">>", nbytes)
      for n in range(0, int(nbytes/16)):    # Color is 16 bytes ( 4 * 4 )
        (r, g, b, a) = unpack("<ffff", data[n*16:(n+1)*16])
        self.colors.append({"red":r, "green":g, "blue":b, "alpha":a}) 
 
    else:
      # Geometry objects
      self.faceidx = []
      self.normalidx = []
      self.texcoordidx = []
      self.coloridx = []

      n = 0
      while n < nbytes:
        for reader in self.readers:
          reader(data[n:n+2])
          n = n + 2

      if objtype == POINTS:
        #print(len(self.faceidx), "points")
        # This was WAY too slow so not doing it right now!
        for n in range(0, len(self.faceidx)):
          self.points.append([self.vertices[self.faceidx[n]], self.material])
          # Add points as "empty"s, this is quite stupid, but what is a better way?
          #ob = Blender.Object.New("Empty")
          #ob.setLocation(self.vertices[n]["x"], self.vertices[n]["y"], self.vertices[n]["z"])
          #ob.setName(self.materialname)
          # ob = self.scn.objects.new("Empty")
          #self.scn.link(ob)
          
      elif objtype == TRIANGLES:
        for n in range(0, int(len(self.faceidx)/3)):
          self.add_face(3*n, 3*n+1, 3*n+2)

      elif objtype == TRIANGLESTRIPS:
        for n in range(0, len(self.faceidx)-2):
          if n % 2 == 0:
            self.add_face(n, n+1, n+2)
          else:
            self.add_face(n, n+2, n+1)

      elif objtype == TRIANGLEFANS:
        for n in range(1, len(self.faceidx)-1):
          self.add_face(0, n, n+1)

    return


  def read_objects(self, batch):
    for object in range(0, self.nobjects):
      # print("Importing object",object,"/",self.nobjects)

      #print("Loading object", self.name + str(object))

      # Clear all variables for this object
      self.readers = [self.read_vertex, self.read_texcoord] 
      self.materialname = None
      self.objvertices = []

      # Object header
      try:
        obj_data = self.f.read(5)
      except:
        print("Error in file format (object header)")
        return

      (object_type, object_properties, object_elements) = unpack("<BHH", obj_data)

      # print("Properties", object_properties)
      # Read properties
      for property in range(0, object_properties):
        try:
          prop_data = self.f.read(5)
        except:
          print("Error in file format (object properties)")
          return

        (property_type, databytes) = unpack("<BI", prop_data)

        try:
          data = self.f.read(databytes)
        except:
          print("Error in file format (property data)")
          return

        # Parse property if this is a geometry object
        self.parse_property(object_type, property_type, data)


      # print("Elements", object_elements)
      # Read elements
      for element in range(0, object_elements):
        try:
          elem_data = self.f.read(4)
        except:
          print("Error in file format (object elements)")
          return

        (databytes, ) = unpack("<I", elem_data)

        # Read element data
        try:
          data = self.f.read(databytes)
        except:
          print("Error in file format (element data)")
          return

        # Parse element data
        self.parse_element(object_type, databytes, data)

      # Normals do not currently work from loading
      # So let's recalculate them.
      # self.mesh.calcNormals()

      # Add this object to scene
      # ob = self.scn.objects.new(self.mesh, self.name)

      # If loading batch, rotate and place tiles correctly
#      if batch:
      if True:
        # print(self.center_lon, self.center_lat)
        ca = math.cos(self.center_lon/180.0*math.pi)
        sa = math.sin(self.center_lon/180.0*math.pi)
        cb = math.cos(-self.center_lat/180.0*math.pi)
        sb = math.sin(-self.center_lat/180.0*math.pi)

        if not batch:
          self.x = 0
          self.y = 0

        # mat = Blender.Mathutils.Matrix([ca*cb, -sa, ca*sb, 0], [sa*cb, ca, sa*sb, 0], [-sb, 0, cb, 0], [0, self.x*22, self.y*14, 0])
        #ob.setMatrix(mat)

    return

  def write_ac3d(self, path):
    try:
      f = open(path, "wt")
    except:
      print("Could not open outfile for writing")
      return

    f.write("AC3Db\r\n")

    # Materials
    mats = len(self.materials)
    for n, material in enumerate(self.materials):
      material=material.decode('utf-8')
      c = float(n) / float(mats)
      outRed=0
      outGreen=0
      outBlue=0
      outAlpha=0
      if material in MaterialListRed:
          outRed=float(MaterialListRed[material])
      if material in MaterialListGreen:
          outGreen=float(MaterialListGreen[material])
      if material in MaterialListBlue:
          outBlue=float(MaterialListBlue[material])
      if material in MaterialListAlpha:
          outAlpha=float(MaterialListAlpha[material])
      f.write("MATERIAL \"%s\" rgb %f %f %f  amb 1 1 1  emis 0.0 0.0 0.0  spec 0.0 0.0 0.0  shi 0  trans 0.0\r\n" % (material, outRed, outGreen, outBlue))

    f.write("OBJECT world\r\n")

    #if self.matrix:
    #  f.write("rot %f %f %f  %f %f %f  %f %f %f\r\n" % (self.matrix[0][0], self.matrix[0][1], self.matrix[0][2], self.matrix[1][0], self.matrix[1][1], self.matrix[1][2], self.matrix[2][0], self.matrix[2][1], self.matrix[2][2]))

    donealready = []

    f.write("kids %d\r\n" % len(self.faces))
    numberOfNewObjects = 0;
    # Write everything as 1 object
    for face in self.faces:
        f.write("OBJECT poly\r\n")
        f.write("name \"%s-%d\"\r\n" % (self.base, numberOfNewObjects))
        if "image" in face:
            f.write("texture \"%s\"\r\n" % face["image"])
        f.write("numvert %s\r\n" % 3)
        index=0
        for vert in face["verts"]:
           f.write("%f %f %f\r\n" % (self.vertices[vert]["x"], self.vertices[vert]["y"], self.vertices[vert]["z"]))
           donealready.append(index)
           index=index+1
        f.write("numsurf %d\r\n" % 1)
        f.write("SURF 0x%d%d\r\n" % (2,0))
        if "material" in face: f.write("mat %d\r\n" % self.materials.index(face["material"][1]))
        f.write("refs %d\r\n" % len(face["verts"]))
        for n in range(0,len(face["verts"])):
               for answer, vert in enumerate(face["verts"]):
                    if vert == face["verts"][n]:
                        f.write("%d %f %f\r\n" % (answer, self.texcoords[face["texcoords"][n]]["x"], self.texcoords[face["texcoords"][n]]["y"]))
        numberOfNewObjects=numberOfNewObjects+1
        f.write("kids 0\r\n")

    mat = None

    f.close()

    print("Bounding spheres, remember the last one for reverse conversion!")
    for sp in self.boundingspheres:
      print(sp)

    return

  def load(self, path, outpath, batch):
    self.name = path.split('\\')[-1].split('/')[-1]

    # parse the file
    try:
      # Check if the file is gzipped, if so -> use built in gzip
      if self.name[-7:].lower() == ".btg.gz":
        self.f = gzip.open(path, "rb")
        self.base = self.name[:-7]
      elif self.name[-4:].lower() == ".btg":
        self.f = open(path, "rb")
        self.base = self.name[:-4]
      else:
        return  # Not a btg file!
    except:
      print("Cannot open file", path)
      return

    # Parse the coordinates from the filename, if possible
    try:
      self.index = int(self.base)
    except:
      print("Could not parse tile location from filename")
      if batch:
        return  # Tile can not be placed properly so discard it
    else:
      self.lon = self.index >> 14
      self.index = self.index - (self.lon << 14)
      self.lon = self.lon - 180

      self.lat = self.index >> 6
      self.index = self.index - (self.lat << 6)
      self.lat = self.lat - 90

      self.y = self.index >> 3
      self.index = self.index - (self.y << 3)
      self.x = self.index

      self.center_lat = self.lat + self.y / 8.0 + 0.0625
      self.center_lon = self.span(self.center_lat)
      if self.center_lon >= 1.0: self.center_lon = self.lon + self.center_lon / 2.0
      else: self.center_lon = self.lon + self.x * self.center_lon * self.center_lon / 2.0

      ca = math.cos(self.center_lon/180.0*math.pi)
      sa = math.sin(self.center_lon/180.0*math.pi)
      cb = math.cos(-self.center_lat/180.0*math.pi)
      sb = math.sin(-self.center_lat/180.0*math.pi)

      self.matrix = [[ca*cb, -sa, ca*sb], [sa*cb, ca, sa*sb], [-sb, 0, cb]]

      print("Tile location:")
      print("  Lat:", self.lat, " Lon:", self.lon)
      print("  X:", self.x, " Y:", self.y)
      print("  Tile span (width)", self.span(self.lat), " degrees")
      print("  Center:", self.center_lat, self.center_lon)

    # Read file contents
    self.f.seek(0)

    # Read and unpack header
    try:
      header = self.f.read(8)
      nobjects_ushort = self.f.read(2)
    except:
      print("File in wrong format")
      return

    (version, magic, creation_time) = unpack("<HHI", header)

    if version >= 7:
      (self.nobjects, ) = unpack("<H", nobjects_ushort)
    else:
      (self.nobjects, ) = unpack("<h", nobjects_ushort)

    if not magic == 0x5347:
      print("Magic is not correct ('SG')")
      return

    # Read objects
    self.read_objects(batch)

    # Now it is loaded! Hoorrah!
    self.f.close()

    # Write everything to outfile
    self.write_ac3d(outpath)

    return


  # Main loader
  def __init__(self, path, outfile, batch = False):
    self.f = None
    self.mesh = None
    self.scn = None

    self.name = ""
    self.base = ""
    self.index = 0

    self.x = 0
    self.y = 0
    self.lat = 0
    self.lon = 0
    self.center_lat = 0
    self.center_lon = 0

    self.boundingspheres = []
    self.vertices = []
    self.normals = []
    self.texcoords = []
    self.colors = []
    self.points = []
    self.faces = []

    self.faceidx = []
    self.normalidx = []
    self.texcoordidx = []
    self.coloridx = []

    self.objvertices = []

    self.nobjects = 0
    self.objects = []

    self.readers = []
    self.materials = []
    self.material = ""
    self.materialname = ""

    self.matrix = None

    if batch:
      try:
        files= [ f for f in os.listdir(path) if f.lower().endswith('.btg.gz') or f.lower().endswith('.btg')]
      except:
        print("Cannot open path")
        return

      if not files:
        print("No files!")
        return

      for f in files:
        self.boundingspheres = []
        self.vertices = []
        self.normals = []
        self.texcoords = []
        self.colors = []

        self.load(path + f, outfile, True)

    else:
      self.load(path, outfile, False)

    return


def import_batch(path, outpath):
  BTG(path, outpath, True)
  return

def import_obj(path, outpath):
  BTG(path, outpath, False)
  return

def usage():
  print("Usage: python btg_to_ac3d.py [input] [output]")
  return


def main(path, outpath):
  global MaterialList
  global MaterialListRed
  global MaterialListBlue
  global MaterialListGreen
  global MaterialListAlpha

  # Find materials node if any
  if FG_ROOT is not None and HAS_XML:
    try:  # Try to load materials.xml
      matxml = xml.dom.minidom.parse(FG_ROOT + "Materials/default/" + "global-summer.xml")

      proplist = matxml.getElementsByTagName("PropertyList")[0]

      if proplist is not None:
        mlist = matxml.getElementsByTagName("material")

        if mlist is not None:
            # Find the material's texture
            texturepath = None
            for e in mlist:
               for nameNode in e.getElementsByTagName("name"):
                   for tname in nameNode.childNodes:
                       if tname.nodeType == tname.TEXT_NODE:  # Name was found
                            for texNode in e.getElementsByTagName("texture"):
                                for tpath in texNode.childNodes:
                                    if tpath.nodeType == tpath.TEXT_NODE:  # texture was found
                                        MaterialList[tname.nodeValue] = tpath.nodeValue  # Store texture path
                                        break
                                    for tredNode in e.getElementsByTagName("r"):
                                          for tred in tredNode.childNodes:
                                              if tred.nodeType == tred.TEXT_NODE:  # red was found
                                                  MaterialListRed[tname.nodeValue] = tred.nodeValue
                                                  print(tred.nodeValue)
                                                  break
                                          break  # go for the next red
                                    for tblueNode in e.getElementsByTagName("b"):
                                        for tblue in tblueNode.childNodes:
                                            if tblue.nodeType == tblue.TEXT_NODE:  # blue was found
                                                MaterialListBlue[tname.nodeValue] = tblue.nodeValue
                                                break
                                        break  # go for the next blue
                                    for tgreenNode in e.getElementsByTagName("g"):
                                        for tgreen in tgreenNode.childNodes:
                                            if tgreen.nodeType == tgreen.TEXT_NODE:  # green was found
                                                MaterialListGreen[tname.nodeValue] = tgreen.nodeValue
                                                break
                                        break  # go for the next green
                                    for talphaNode in e.getElementsByTagName("a"):
                                        for talpha in talphaNode.childNodes:
                                            if talpha.nodeType == talpha.TEXT_NODE:  # alpha was found
                                                MaterialListAlpha[tname.nodeValue] = talpha.nodeValue
                                                break
                                        break  # go for the next alpha
    except Exception as ex:
      print(f"Could not load materials.xml: {ex}")
      MaterialList = { }

  print("Loading file", path)
  import_obj(path, outpath)


if __name__ == "__main__":
  if len(sys.argv) != 3:
    usage()
    sys.exit()

  main(sys.argv[1], sys.argv[2])
