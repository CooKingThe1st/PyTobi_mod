#!/bin/bash

org_directory=$1
cd $org_directory
echo "Entering org_directory"
touch "concat_tacotron.txt"
> "concat_tacotron.txt"
touch "concat_seq2seq_break.txt"
> "concat_seq2seq_break.txt"
touch "concat_seq2seq_tone.txt"
> "concat_seq2seq_tone.txt"

find . -name '*.wav' | while read file; do
	echo "Processing file " $file
	# basename="${file%.*}"
	# basename="${basename:2}"

	basename="$(basename $file)"
	basename="${basename%.*}"

	dir_name="$(dirname ${file})"
	dir_name="${dir_name:1}"
	# echo $basename
	#echo $dir_name
	# echo "$org_directory$dir_name"

    path2name="${org_directory}${dir_name}/"
    printf $"${path2name}${basename}.wav|" >> "concat_tacotron.txt"
    cat  "${path2name}${basename}_modBreak.txt" >> "concat_tacotron.txt"
    printf "\n" >> "concat_tacotron.txt"

    echo -n $(tr -d "\n" < ${path2name}${basename}.txt) > ${path2name}${basename}.txt
    
    cat  "${path2name}${basename}.txt" >> "concat_seq2seq_break.txt"
    printf "|" >> "concat_seq2seq_break.txt"
    cat  "${path2name}${basename}_orgBreak.txt" >> "concat_seq2seq_break.txt"
    printf "\n" >> "concat_seq2seq_break.txt"


    cat  "${path2name}${basename}.txt" >> "concat_seq2seq_tone.txt"
    printf "|" >> "concat_seq2seq_tone.txt"
    cat  "${path2name}${basename}_orgTone.txt" >> "concat_seq2seq_tone.txt"
    printf "\n" >> "concat_seq2seq_tone.txt"

done
