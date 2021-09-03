#!/bin/bash
#
# admin@kamenka.su
#
# find all fortunes with the keyword, save into tmp, get one random, flush temp dir
#
# input: uid and keyword
#
##################################################################################################

dirid="id$1"

if [ ! -d 'tmp' ]; then mkdir 'tmp'
fi

cd tmp

### uid dir test
if [ ! -d $dirid ]; then mkdir $dirid
fi

cd $dirid
rm xx* > /dev/null 2>&1

/usr/games/fortune -i -m "\(^\| \)\($2\)" > /dev/stdout 2>/dev/null | csplit - -sz --suppress-matched /%/ {*}
/usr/games/fortune -i -m "\(^\| \)\($2\)" ru > /dev/stdout 2>/dev/null | csplit - -sz --suppress-matched /%/ {*}

### OK, now tmp/uid is full (or empty if none is found) of files
### next let  the python script done the things over with only one choosen from all the bunch

citates=(*)
if ((${#citates[*]} > 1)); then
	num=$((RANDOM % ${#citates[*]}))
	if (($num < 10)); then
	cat xx0$num
	else
	cat xx$num
	fi
	cd ..
	rm -rf $dirid
else
	exit -1
fi
