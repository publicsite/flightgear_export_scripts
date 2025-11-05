#!/bin/sh

OLD_UMASK="$(umask)"
umask 0022

# 1) cd to tests directory, run this script

rm 383925-scenery.ac out.ac atemp.stg #dont worry if this fails, its just to clean up

SCALE_FACTOR="1" FG_ROOT="${PWD}/fgdata/fgdata/" FG_SCENERY="${PWD}/fgdata/fgdata/Scenery/SceneryPack.BIKF/" \
python3 ${PWD}/../btg_to_ac3d_2.py "fgdata/fgdata/Scenery/SceneryPack.BIKF/Terrain/w160n20/w157n20/383925.btg.gz" "383925-scenery.ac"

# Note that with the -c flag added, the below test instructions are unnecessary because the flag fixes the issue
lonlat="$(python3 ${PWD}/../tile_calculator.py -c 383925)"

elevation="$(echo woo $lonlat | \
FG_ROOT="${PWD}/fgdata/fgdata/" FG_SCENERY="${PWD}/fgdata/fgdata/Scenery/SceneryPack.BIKF/" fgelev \
| grep woo | \
cut -d ' ' -f 2)"

printf "OBJECT_SHARED %s/%s %s %s 142 142 142\n" "${PWD}" "383925-scenery.ac" "$lonlat" "$elevation" > atemp.stg

grep "ac " fgdata/fgdata/Scenery/SceneryPack.BIKF/Objects/w160n20/w157n20/383925.stg >> atemp.stg

SCALE_FACTOR="0.001" FG_ROOT="${PWD}/fgdata/fgdata/" FG_SCENERY="${PWD}/fgdata/fgdata/Scenery/SceneryPack.BIKF/" \
python3 ${PWD}/../concat_ac3.py "atemp.stg" >> "out.ac"

# OLD INSTRUCTIONS TO DEMONSTRATE WHEN THIS TEST USED TO FAIL:

# 2) run
# 	$ osgviewer out.ac
# observe that there are no pylons displayed

# 3) run
#	$ nano out.ac
# change the first loc param to 
#	loc -2076.327387217802 -5463.314448130804 0.77766

# 4) run
#	$osgviewer out.ac
# observe that pylons are displayed, but at the wrong angle to the scenery





# ==what did we do?==
# We changed the loc param of the scenery to match that of one of the pylons,
# because pylons were close enough to the scenery after editing the loc param, the pylons were displayed after modification

# ==what this tells us==
# The scenery loc param and the object loc params are 'too different' for some reason, and this needs correcting.
#

umask "${OLD_UMASK}"
