#!/bin/sh

OLD_UMASK="$(umask)"
umask 0022

#Authors: J05HYYY

#This test must be run MANUALLY

#this test requires visually checking geometories in fgviewer and osgviewer
sudo apt-get install -y flightgear openscenegraph

mkdir -p fgdata/fgdata/Scenery/SceneryPack.BIKF/Objects/w130n30/w122n37
cp -a 958401-test.stg fgdata/fgdata/Scenery/SceneryPack.BIKF/Objects/w130n30/w122n37/958401.stg

#sudo apt-get install blender flightgear openscenegraph

FG_ROOT=${FG_ROOT:-"/usr/share/games/flightgear/"}  # default if no env var
FG_ROOT="$(echo "$FG_ROOT" | sed 's~[^/]$~&/~')"  # add trailing slash if missing
export FG_ROOT

# can take input as arguments to the script (otherwise use original defaults)
stg=${1:-"${FG_ROOT}Scenery/Objects/w130n30/w122n37/958401.stg"}
btg_gz=${2:-"${FG_ROOT}Scenery/Terrain/w130n30/w122n37/958401.btg.gz"}


python3 ../btg_to_ac3d_2.py "$btg_gz" scenery1.ac

##visually check using flightgear that placement matches, or is similar enough...

#first check the hangars in flightgear and take a screenshot
#fgfs --fg-scenery=$PWD/fgdata/fgdata/Scenery/SceneryPack.BIKF --lat=37.08390597 --lon=-121.60146087 --aircraft=ufo --console --log-level=info 2>&1 | tee fgfs.log

#convert the stg file to ac3d
python3 ../concat_ac3.py "$stg" > objects1.ac

#note - you can then convert it into obj if you want (optional)
#osgconv objects1.ac out.obj

#then check the converted ac3d hangars using osgviewer, and take a screenshot
#osgviewer objects1.ac

#combine the screenshots into test-Placement-Result.png

#clean up
rm -f fgdata/fgdata/Scenery/SceneryPack.BIKF/Objects/w130n30/w122n37/958401.stg
rmdir fgdata/fgdata/Scenery/SceneryPack.BIKF/Objects/w130n30/w122n37
rmdir fgdata/fgdata/Scenery/SceneryPack.BIKF/Objects/w130n30

umask "${OLD_UMASK}"
