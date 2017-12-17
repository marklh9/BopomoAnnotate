SRC= bopomo.py Addons.xcu Jobs.xcu description.xml \
description_en-US.txt description_zh-TW.txt license.txt phtab.pkl tool.png \
META-INF/manifest.xml

bopomo.oxt: $(SRC)
	cd src && zip -r ../bopomo.oxt * \
	&& unopkg add -f ../bopomo.oxt

src/description.xml: bopomo.py
	sed -i 's/<version value="[^"]*"/<version value="v'`date +%y.%m.%d.%H%S`'"/' $@

.PHONY: bopomo.oxt

VPATH=src
