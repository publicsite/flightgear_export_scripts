#!/bin/sh

#Authors: J05HYYY

thepwd="$PWD"

FG_ROOT="${thepwd}/fgdata/fgdata/"

scenery_a="SceneryPack.BIKF"
scenery_b="London"

cd "${FG_ROOT}Scenery/${scenery_a}"

if [ -d "${FG_ROOT}Scenery/${scenery_a}/Master" ]; then
	rm -rf "${FG_ROOT}Scenery/${scenery_a}/Master"
fi

if [ -d "${FG_ROOT}Scenery/${scenery_b}/Master" ]; then
	rm -rf "${FG_ROOT}Scenery/${scenery_b}/Master"
fi

echo $PWD
find "${FG_ROOT}Scenery/${scenery_b}/Terrain" -maxdepth 2 -mindepth 2 -type d | while read tile; do
	mkdir -p "$(printf "Final/AC3D/%s\n" "$(printf "%s" $tile | rev | cut -d "/" -f 1-2 | rev)")"
	find "$tile" -type f -name "*.btg.gz" | while read abtg; do


		mkdir -p "$(printf "%sScenery/${scenery_a}/Master/%s\n" "${FG_ROOT}" "$(printf "%s" $tile | rev | cut -d "/" -f 1-2 | rev)")"
		SCALE_FACTOR="1" FG_ROOT="${FG_ROOT}" FG_SCENERY="${FG_ROOT}Scenery/${scenery_a}/" python3 ${thepwd}/../btg_to_ac3d_2.py "${abtg}" "${FG_ROOT}Scenery/${scenery_a}/Master/$(printf "%s" "${abtg}" | rev | cut -d "/" -f 1-3 | rev | cut -d "." -f 1)-objects.ac"

		masterstg="${FG_ROOT}Scenery/${scenery_a}/Master/$(printf "%s" "${abtg}" | rev | cut -d "/" -f 1-3 | rev | cut -d "." -f 1).stg"

		lonlat="$(python3 ${thepwd}/../tile_calculator.py $(printf "%s" "${abtg}" | rev | cut -d "/" -f 1 | rev | cut -d "." -f 1))"

		elevation="$(echo woo $lonlat | FG_ROOT="${FG_ROOT}" FG_SCENERY="${FG_ROOT}Scenery/${scenery_a}/" fgelev | grep woo | cut -d ' ' -f 2)"

		printf "OBJECT_SHARED /Master/%s %s %s 0\n" "$(printf "%s" "${abtg}" | rev | cut -d "/" -f 1-3 | rev | cut -d "." -f 1)-objects.ac" "$lonlat" "$elevation" >> "$masterstg"

		astg="${FG_ROOT}Scenery/${scenery_b}/Objects/$(printf "%s" "${abtg}" | rev | cut -d "/" -f 1-3 | rev | cut -d "." -f 1).stg"
		if [ -d "$(dirname "$astg")" ]; then
			if [ -f "$astg" ]; then
				cat "$astg" >> "$masterstg"
			fi
		fi

		astg="${FG_ROOT}Scenery/${scenery_b}/Pylons/$(printf "%s" "${abtg}" | rev | cut -d "/" -f 1-3 | rev | cut -d "." -f 1).stg"
		if [ -d "$(dirname "$astg")" ]; then
			if [ -f "$astg" ]; then
				cat "$astg" >> "$masterstg"
			fi
		fi

		astg="${FG_ROOT}Scenery/${scenery_b}/Roads/$(printf "%s" "${abtg}" | rev | cut -d "/" -f 1-3 | rev | cut -d "." -f 1).stg"
		if [ -d "$(dirname "$astg")" ]; then
			if [ -f "$astg" ]; then
				cat "$astg" >> "$masterstg"
			fi
		fi

		astg="${FG_ROOT}Scenery/${scenery_b}/Buildings/$(printf "%s" "${abtg}" | rev | cut -d "/" -f 1-3 | rev | cut -d "." -f 1).stg"
		if [ -d "$(dirname "$astg")" ]; then

			if [ -f "$astg" ]; then
				cat "$astg" >> "$masterstg"
			fi
		fi

		astg="${FG_ROOT}Scenery/${scenery_b}/Details/$(printf "%s" "${abtg}" | rev | cut -d "/" -f 1-3 | rev | cut -d "." -f 1).stg"
		if [ -d "$(dirname "$astg")" ]; then
			if [ -f "$astg" ]; then
				cat "$astg" >> "$masterstg"
			fi
		fi

		mkdir -p "$(printf "%s/Final/AC3D/%s\n" "${thepwd}" "$(printf "%s" $tile | rev | cut -d "/" -f 1-2 | rev)")"
		SCALE_FACTOR="0.001" FG_ROOT="${FG_ROOT}" FG_SCENERY="${FG_ROOT}Scenery/${scenery_a}/" python3 ${thepwd}/../concat_ac3.py "$masterstg" >> "${thepwd}/Final/AC3D/$(printf "%s" "${astg}" | rev | cut -d "/" -f 1-3 | rev | cut -d "." -f 1).ac"
	done
done

#find "${FG_ROOT}Scenery/${scenery_a}/Objects" -maxdepth 2 -mindepth 2 -type d | while read tile; do
#	mkdir -p "$(printf "Final/AC3D/%s\n" "$(printf "%s" $tile | rev | cut -d "/" -f 1-2 | rev)")"
#	find "$tile" -type f -name "*.stg" | while read astg; do
#		echo "OBJECT_SHARED $ac3d 0 0 0 0" >> "temp.stg"
#
#	done
#done

#find Terrain/AC3D/ -maxdepth 2 -mindepth 2 -type d | while read tile; do
#	mkdir -p "$(printf "Final/AC3D/%s\n" "$(printf "%s" $tile | rev | cut -d "/" -f 1-2 | rev)")"
#	find "$tile" -type f -name "*.ac" | while read ac3d; do
#		echo "OBJECT_SHARED $ac3d 0 0 0 0" >> "temp.stg"
#		find Objects -name "$(basename "$ac3d")" | while read objectFile; do
#		echo "OBJECT_SHARED $objectFile 0 0 0 0" >> "temp.stg"
#		dones
#		FG_ROOT="${thepwd}/" FG_SCENERY="${FG_ROOT}Scenery/${scenery_a}/Scenery" python3 ${thepwd}/../concat_ac3.py temp.stg > "Final/AC3D/$(printf "%s" "${ac3d}" | rev | cut -d "/" -f 1-3 | rev | cut -d "." -f 1).ac"
#		temp.stg
#	done
#done
