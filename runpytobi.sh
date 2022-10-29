#!/bin/bash

# Write the path to PyToBI here. NOTE: a copy of Praat should be inside this folder
path2pytobi=/media/we/Media/PyToBI

# Comment/uncomment the following lines depending on your system (Mac, Linus/Windows)
# Mac Users must uncomment the following line and comment the Linux/Windows line 10
#praat=Praat.app/Contents/MacOS/Praat

#Linux/Windows users must uncomment the following line and comment the Mac line 7
praat=praat

org_directory=$1
aligned_directory=$2
subdir=praatScripts/

cd $org_directory
echo "Entering org_directory"
find . -name '*.wav' | while read file; do
	echo "····························································"
	echo "Processing file " $file
	# basename="${file%.*}"
	# basename="${basename:2}"

	basename="$(basename $file)"
	basename="${basename%.*}"

	dirname="$(dirname ${file})"
	dirname="${dirname:1}"
	# echo $basename
	# echo $dirname
	# echo "$org_directory$dirname"

	cd $path2pytobi
	cd $subdir

	praat --run module01.praat "$org_directory$dirname/" $basename
	praat --run module02.praat "$org_directory$dirname/" $basename
	praat --run module03.praat "$org_directory$dirname/" $basename
	praat --run module04.praat "$org_directory$dirname/" "$aligned_directory$dirname/" $basename

	cd $path2pytobi

	python3 tobi.py "$org_directory$dirname/" $basename
	# echo "PyToBI has been completed"
done
