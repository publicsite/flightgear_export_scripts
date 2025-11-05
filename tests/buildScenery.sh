#!/bin/sh

OLD_UMASK="$(umask)"
umask 0022

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
    fname="$(basename "${abtg}")"
    fn_no_ext="${fname%%.*}"
    # Check that fn_no_ext is a positive integer
    case $fn_no_ext in
      ''|*[!0-9]*) echo "Can't get lonlat from $fname, skipping..." ; continue ;;
    esac

    fn_subdir_subdir="$(printf "%s" "${abtg}" | rev | cut -d "/" -f 1-3 | rev | cut -d "." -f 1)"


		mkdir -p "$(printf "%sScenery/${scenery_a}/Master/%s\n" "${FG_ROOT}" "$(printf "%s" $tile | rev | cut -d "/" -f 1-2 | rev)")"

		SCALE_FACTOR="1" FG_ROOT="${FG_ROOT}" FG_SCENERY="${FG_ROOT}Scenery/${scenery_a}/" \
		python3 ${thepwd}/../btg_to_ac3d_2.py "${abtg}" "${FG_ROOT}Scenery/${scenery_a}/Master/${fn_subdir_subdir}-objects.ac"

		masterstg="${FG_ROOT}Scenery/${scenery_a}/Master/${fn_subdir_subdir}.stg"

		lonlat="$(python3 ${thepwd}/../tile_calculator.py -c "$fn_no_ext")"

		elevation="$(echo woo $lonlat | FG_ROOT="${FG_ROOT}" FG_SCENERY="${FG_ROOT}Scenery/${scenery_a}/" fgelev | grep woo | cut -d ' ' -f 2)"

		printf "OBJECT_SHARED /Master/%s %s %s 0\n" "${fn_subdir_subdir}-objects.ac" "$lonlat" "$elevation" >> "$masterstg"

		astg="${FG_ROOT}Scenery/${scenery_b}/Objects/${fn_subdir_subdir}.stg"
		if [ -d "$(dirname "$astg")" ]; then
			if [ -f "$astg" ]; then
				cat "$astg" >> "$masterstg"
			fi
		fi

		astg="${FG_ROOT}Scenery/${scenery_b}/Pylons/${fn_subdir_subdir}.stg"
		if [ -d "$(dirname "$astg")" ]; then
			if [ -f "$astg" ]; then
				cat "$astg" >> "$masterstg"
			fi
		fi

		astg="${FG_ROOT}Scenery/${scenery_b}/Roads/${fn_subdir_subdir}.stg"
		if [ -d "$(dirname "$astg")" ]; then
			if [ -f "$astg" ]; then
				cat "$astg" >> "$masterstg"
			fi
		fi

		astg="${FG_ROOT}Scenery/${scenery_b}/Buildings/${fn_subdir_subdir}.stg"
		if [ -d "$(dirname "$astg")" ]; then

			if [ -f "$astg" ]; then
				cat "$astg" >> "$masterstg"
			fi
		fi

		astg="${FG_ROOT}Scenery/${scenery_b}/Details/${fn_subdir_subdir}.stg"
		if [ -d "$(dirname "$astg")" ]; then
			if [ -f "$astg" ]; then
				cat "$astg" >> "$masterstg"
			fi
		fi

		mkdir -p "$(printf "%s/Final/AC3D/%s\n" "${thepwd}" "$(printf "%s" $tile | rev | cut -d "/" -f 1-2 | rev)")"
		astg_subdir_subdir="$(printf "%s" "${astg}" | rev | cut -d "/" -f 1-3 | rev | cut -d "." -f 1)"

		SCALE_FACTOR="0.001" FG_ROOT="${FG_ROOT}" FG_SCENERY="${FG_ROOT}Scenery/${scenery_a}/" \
		python3 ${thepwd}/../concat_ac3.py "$masterstg" >> "${thepwd}/Final/AC3D/${astg_subdir_subdir}.ac"
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

umask "${OLD_UMASK}"
