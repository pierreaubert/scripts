# split books and put them in author dir
for i in *; do
    if ! test -d "$i"; then
	readarray -d- -t ar <<< "$i";
	ar0=${ar[0]};
	target=${ar0% };
	mkdir -p "$target";
	mv "$i" "${target}";
    fi
done
python3 ~/bin/scripts/sffchecker.py --calibre /data/media/books/Calibre/Pierre --sff /data/media/books/sff-updates/new

