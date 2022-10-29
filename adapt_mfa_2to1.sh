#!/bin/bash

org_directory=$1
echo "Searching in 2.0_directory"

find $org_directory -name '*.TextGrid' | while read file; do
	#echo "Processing file " $file
	# basename="${file%.*}"
	# basename="${basename:2}"

	basename="$(basename $file)"
	basename="${basename%.*}"

	dir_name="$(dirname $file)"
	dir_name="$(basename $dir_name)"
	#echo $basename
	#echo $dir_name
	#echo "${org_directory}${dir_name}/${basename}.TextGrid"

    path2name="${org_directory}${dir_name}/"
    #printf $"${path2name}${basename}.wav|" >> "concat_tacotron.txt"
    #cat  "${path2name}${basename}_modBreak.txt" >> "concat_tacotron.txt"
    #printf "\n" >> "concat_tacotron.txt"
    python deprecating_mfa_2_to_1.py "${org_directory}${dir_name}/" $basename
done
