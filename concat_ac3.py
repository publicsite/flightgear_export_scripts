#!/usr/bin/python

#Authors: J05HYYY, benxyzzy

import math
import os
from pathlib import Path
import sys

import inspect
import traceback


FG_ROOT = os.environ.get("FG_ROOT", "/usr/share/games/flightgear/")

FG_SCENERY = os.environ.get("FG_SCENERY", "/usr/share/games/flightgear/Scenery/")

def usage():
    print("Usage: python concat_ac3.py [file]")
    return


def log_exceptions(exclude_args=None, exclude_exceptions=None):
    if exclude_args is None:
        exclude_args = set()
    if exclude_exceptions is None:
        exclude_exceptions = tuple()
    else:
        exclude_exceptions = tuple(exclude_exceptions)

    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except exclude_exceptions:
                raise
            except Exception:
                # Get function signature to match args to parameter names
                sig = inspect.signature(func)
                bound_args = sig.bind_partial(*args, **kwargs)
                bound_args.apply_defaults()  # Ensure defaults are included

                # Filter out excluded arguments
                filtered_args = {k: v for k, v in bound_args.arguments.items() if k not in exclude_args}

                print(f"Exception in function: {func.__name__}", file=sys.stderr)
                print(f"Arguments (excluding {exclude_args}): {filtered_args}", file=sys.stderr)
                print("Traceback:", file=sys.stderr)
                traceback.print_exc(file=sys.stderr)

                raise

        return wrapper

    return decorator


# Convert geodetic coordinates to Cartesian
def geodToCart(lat, lon, alt):
    flattening = 298.257223563
    squash = (1 - 1 / flattening)
    e2 = math.fabs(1 - squash * squash)

    a = 6378137.0

    lambda1 = math.radians(lon)
    phi = math.radians(lat)
    h = alt

    sphi = math.sin(phi)

    n = a / math.sqrt(1 - e2 * sphi * sphi)
    cphi = math.cos(phi)
    slambda = math.sin(lambda1)
    clambda = math.cos(lambda1)
    x = (h + n) * cphi * clambda
    y = (h + n) * cphi * slambda
    z = (h + n - e2 * n) * sphi
    return x, y, z

@log_exceptions(exclude_args={"globalMaterials", "mainBody"}, exclude_exceptions=(FileNotFoundError,))
def processACFile(ACFilePath, splitExtension, splitLine, globalMaterials=None, mainBody=None, numberOfObjects=0):
    if globalMaterials is None:
        globalMaterials = []
    if mainBody is None:
        mainBody = []
    scale_factor = float(os.environ.get("SCALE_FACTOR", "0.001"))

    materialsRelationship = []

    numvert = None
    verts_written = None
    with open(ACFilePath, "r") as ACFile:
        for line2 in ACFile:
            if numvert is not None:
                # We're in a vert block
                if scale_factor == 1:
                    # No scaling required so leave the line of text unchanged
                    mainBody.append(line2.strip())
                else:
                    vert = [scale_factor*float(el) for el in line2.strip().split(" ")]
                    mainBody.append(" ".join([str(el) for el in vert]))
                verts_written += 1
                if verts_written == numvert:
                    # end of block of verts
                    numvert = None
                    verts_written = None
            elif line2.strip().startswith("numvert "):
                # Possible start of vert block
                splitLine2 = line2.strip().split(" ")
                this_numvert = int(splitLine2[1])
                if this_numvert > 0:
                    numvert = this_numvert
                    verts_written = 0

                    mainBody.append(line2.strip())
            elif line2.strip() == "AC3Db":
                continue
            elif line2.strip() == "OBJECT world":
                mainBody.append("OBJECT poly")
                mainBody.append("name \"_" + str(numberOfObjects) + "_" + splitExtension[0] + "\"")
                numberOfObjects = numberOfObjects + 1
                heading = 0
                pitch = 0
                roll = 0
                if len(splitLine) < 7:
                    heading = math.radians(float(splitLine[5]))
                    pitch = math.radians(float(0))
                    roll = math.radians(float(0))
                elif len(splitLine) < 8:
                    heading = math.radians(float(splitLine[5]))
                    pitch = math.radians(float(splitLine[6]))
                    roll = math.radians(float(0))
                elif len(splitLine) < 9:
                    heading = math.radians(float(splitLine[5]))
                    pitch = math.radians(float(splitLine[6]))
                    roll = math.radians(float(splitLine[7]))

                ca = math.cos(roll)
                sa = math.sin(roll)
                cd = math.cos(heading)
                sd = math.sin(heading)
                cr = math.cos(pitch)
                sr = math.sin(pitch)

                rotationMatrix = [[0 for x in range(3)] for y in range(3)]
                rotationMatrix[0][0] = cd * cr
                rotationMatrix[0][1] = cd * sr * sa - sd * ca
                rotationMatrix[0][2] = cd * sr * ca + sd * sa
                rotationMatrix[1][0] = sd * cr
                rotationMatrix[1][1] = sd * sr * sa + cd * ca
                rotationMatrix[1][2] = sd * sr * ca  - cd * sa
                rotationMatrix[2][0] = 0 - sr
                rotationMatrix[2][1] = cr * sa
                rotationMatrix[2][2] = cr * ca

                mainBody.append("rot " + str(rotationMatrix[0][0]) + " " + str(
                    rotationMatrix[0][1]) + " " + str(rotationMatrix[0][2]) + " " + str(
                    rotationMatrix[1][0]) + " " + str(rotationMatrix[1][1]) + " " + str(
                    rotationMatrix[1][2]) + " " + str(rotationMatrix[2][0]) + " " + str(
                    rotationMatrix[2][1]) + " " + str(rotationMatrix[2][2]))

                lat = 0 - float(splitLine[2])
                lon = float(splitLine[3])
                alt = float(splitLine[4])

                #temp = geodToCart(37.5, -122.7, 1000)

                convertedCoords = geodToCart(lat, lon, alt)
                if scale_factor == 1:
                    scaled_alt = alt
                else:
                    convertedCoords = [scale_factor*float(el) for el in convertedCoords]
                    scaled_alt = scale_factor*alt

                #mainBody.append(
                #    "loc " + str(convertedCoords[2]) + " " + str(convertedCoords[1]) + " " + str(
                #    alt))
                #mainBody.append(
                #    "loc " + str(convertedCoords[1]) + " " + str(convertedCoords[2]) + " " + str(
                #    alt))

                mainBody.append(
                    "loc " + str(convertedCoords[1]) + " " + str(convertedCoords[0]) + " " + str(scaled_alt))
                # mainBody.append("loc " + str(lon) + " " + str(lat) + " " + str(rad))
            else:
                splitLine2 = line2.strip().split(" ")
                if len(splitLine2) > 0:
                    if splitLine2[0] == "MATERIAL":
                        found = -1
                        for materialIndex in range(len(globalMaterials)):
                            if globalMaterials[materialIndex] == line2.strip():
                                found = 1;
                                materialsRelationship.append(materialIndex)
                                # print(materialIndex)
                                break;
                        if found == -1:
                            materialsRelationship.append(len(globalMaterials))
                            # print(len(globalMaterials))
                            globalMaterials.append(line2.strip())
                    elif splitLine2[0] == "mat":
                        if len(splitLine2) > 1:
                            mainBody.append("mat " + str(materialsRelationship[int(splitLine2[1])]))
                    elif splitLine2[0] == "texture" and len(splitLine2) > 1:
                        orig_path = splitLine2[1].strip('"')
                        base_path = Path(ACFilePath).parent
                        abs_path = (base_path / orig_path).resolve()

                        mainBody.append(f'texture "{abs_path}"')
                    else:
                        mainBody.append(line2.strip())

    return globalMaterials, mainBody, numberOfObjects

def main(STGFile_path):
    globalMaterials = []
    mainBody = []
    numberOfObjects = 0

    if FG_ROOT is not None:
        # Open a file
        STGFile = open(STGFile_path, "r")
        # print("Reading: ", STGFile.name)
        for line in STGFile:
            splitLine = line.strip().split(" ");
            if len(splitLine) > 1:
                if splitLine[0] == "OBJECT_SHARED":
                    # TODO: for 958401-test.stg, this will mean splitExtension[0] == 'Models/Airport/thangar'
                    # Is that correct, or should it just be splitExtension[0] == 'thangar' ?
                    splitExtension = splitLine[1].split(".")
                    if splitExtension[len(splitExtension) - 1] == "ac":
                        # print(splitLine[1]) #ac file name
                        lockedAndLoaded=0

                        try:
                            ACFilePath = FG_ROOT + splitLine[1]
                            globalMaterials, mainBody, numberOfObjects = processACFile(
                                ACFilePath, splitExtension, splitLine, globalMaterials, mainBody, numberOfObjects)
                            lockedAndLoaded = 1
                        except IOError:
                            lockedAndLoaded = 0

                        if lockedAndLoaded == 0:
                            try:
                                ACFilePath = FG_SCENERY + splitLine[1]
                                globalMaterials, mainBody, numberOfObjects = processACFile(
                                    ACFilePath, splitExtension, splitLine, globalMaterials, mainBody, numberOfObjects)
                                lockedAndLoaded = 1
                            except IOError:
                                lockedAndLoaded = 0

                        if lockedAndLoaded == 0:
                            try:
                                ACFilePath = os.path.dirname(sys.argv[1]) + "/" + splitLine[1]
                                globalMaterials, mainBody, numberOfObjects = processACFile(
                                    ACFilePath, splitExtension, splitLine, globalMaterials, mainBody, numberOfObjects)
                                lockedAndLoaded = 1
                            except IOError:
                                print("Could not open " + splitLine[1])
                                exit

    # Close opened file
    STGFile.close()

    print("AC3Db")
    for materialIndex in range(len(globalMaterials)):
        print(globalMaterials[materialIndex])
    print("OBJECT world")
    print("kids " + str(numberOfObjects))
    for outputLine in mainBody:
        print(outputLine)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        usage()
        sys.exit()

    STGFile_path = sys.argv[1]
    main(STGFile_path)
