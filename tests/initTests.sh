#!/bin/sh
#Authors J05HYYY

OLD_UMASK="$(umask)"
umask 0022

thepwd="${PWD}"

#get flightgear data

mkdir fgdata
cd fgdata

wget https://sourceforge.net/projects/flightgear/files/release-2020.3/FlightGear-2020.3.8-data.txz/download -O FlightGear-2020.3.8-data.txz
wget http://mirrors.ibiblio.org/flightgear/ftp/Scenery-v2.12/e000n50.tgz
wget http://mirrors.ibiblio.org/flightgear/ftp/Scenery-v2.12/w010n50.tgz
wget https://github.com/legoboyvdlp/London-OSM-fg-CustomScenery/archive/refs/heads/master.tar.gz -O London-OSM-fg-CustomScenery-master.tar.gz

tar -xf FlightGear-2020.3.8-data.txz

cd ..

ln -s fgdata/fgdata/Models FG_ROOT

#process BTG files

mkdir -p fgdata/fgdata/Scenery/London
cd fgdata/fgdata/Scenery/London

#mkdir -p BTG/e000n50/e000n51
#cp -a Terrain/e000n50/e000n51/*.btg.gz BTG/e000n50/e000n51/
#rm -rf Terrain Objects

tar -xf $thepwd/fgdata/w010n50.tgz
#mkdir -p BTG/w010n50/w001n51
#cp -a Terrain/w010n50/w001n51/*.btg.gz BTG/w010n50/w001n51/
#rm -rf Terrain Objects

tar -xf $thepwd/fgdata/e000n50.tgz

cd ../../

#get Objects
mkdir -p Objects
cd Objects
tar -xf $thepwd/fgdata/London-OSM-fg-CustomScenery-master.tar.gz

cd $thepwd

#get conversion scripts #TODO:FIX BTG TO AC3D SCRIPT
#git clone https://github.com/publicsite/flightgear_export_scripts
#sed -i "s#FG_ROOT = \"/usr/share/games/flightgear/\"#FG_ROOT = \"${thepwd}/fgdata/fgdata/\"#g" flightgear_export_scripts/btg_to_ac3d_2.py
#sed -i "s#FG_ROOT = \"/usr/share/games/flightgear/\"#FG_ROOT = \"${thepwd}/fgdata/fgdata/\"#g" flightgear_export_scripts/concat_ac3.py

umask "${OLD_UMASK}"
