SRC= bopomo.py Addons.xcu Jobs.xcu description.xml \
description_en-US.txt description_zh-TW.txt license.txt phtab.pkl tool.png \
META-INF/manifest.xml
VER=v$(shell expr `date +%y` - 7)$(shell date +%m.%d%H%M)

install: bopomo.oxt
	unopkg add -f bopomo.oxt

test: install
	soffice --writer --norestore

bopomo.oxt: $(SRC)
	cd src && zip -r ../bopomo.oxt *

src/description.xml: bopomo.py
	sed -i 's/<version value="[^"]*"/<version value="'$(VER)'"/' $@

.PHONY: install test

VPATH=src
