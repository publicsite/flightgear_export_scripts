#!/bin/sh

OLD_UMASK="$(umask)"
umask 0022

#Authors: J05HYYY

thepwd="$PWD"

echo $PWD
find Terrain/BTG/ -maxdepth 2 -mindepth 2 -type d | while read tile; do
	mkdir -p "$(printf "Terrain/AC3D/%s\n" "$(printf "%s" $tile | cut -d "/" -f 3-)")"
	find "$tile" -type f | while read abtg; do
		FG_ROOT="${thepwd}/fgdata/fgdata/" FG_SCENERY="${thepwd}/fgdata/fgdata/Scenery/SceneryPack.BIKF/" python3 ../btg_to_ac3d_2.py "${abtg}" "Terrain/AC3D/$(printf "%s" "${abtg}" | cut -d "/" -f 3- | cut -d "." -f 1).ac"
	done
done

find Objects/STG/ -maxdepth 3 -mindepth 3 -type d | while read tile; do
	mkdir -p "$(printf "Objects/AC3D/%s\n" "$(printf "%s" $tile | cut -d "/" -f 3-)")"
	find "$tile" -type f -name "*.stg" | while read astg; do
		FG_ROOT="${thepwd}/fgdata/fgdata/" FG_SCENERY="${thepwd}/fgdata/fgdata/Scenery/SceneryPack.BIKF/" python3 ../concat_ac3.py "${astg}" > "Objects/AC3D/$(printf "%s" "${astg}" | cut -d "/" -f 3- | cut -d "." -f 1).ac"
	done
done

find Terrain/AC3D/ -maxdepth 2 -mindepth 2 -type d | while read tile; do
	mkdir -p "$(printf "Final/AC3D/%s\n" "$(printf "%s" $tile | cut -d "/" -f 3-)")"
	find "$tile" -type f -name "*.ac" | while read ac3d; do
		echo "OBJECT_SHARED $ac3d 0 0 0 0" >> "temp.stg"
		find Objects -name "$(basename "$ac3d")" | while read objectFile; do
		echo "OBJECT_SHARED $objectFile 0 0 0 0" >> "temp.stg"
		done
		FG_ROOT="${thepwd}/" FG_SCENERY="${thepwd}/fgdata/fgdata/Scenery/SceneryPack.BIKF/" python3 ../concat_ac3.py temp.stg > "Final/AC3D/$(printf "%s" "${ac3d}" | cut -d "/" -f 3- | cut -d "." -f 1).ac"
		rm temp.stg
	done
done

umask "${OLD_UMASK}"
