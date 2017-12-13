SRC= BopomoAnnotateJob.py Addons.xcu Jobs.xcu description.xml \
description_en-US.txt description_zh-TW.txt license.txt phtab.pkl tool.png \
META-INF/manifest.xml

BopomoAnnotate.oxt: $(SRC)
	cd src && zip -r ../BopomoAnnotate.oxt * \
	&& unopkg add -f ../BopomoAnnotate.oxt

src/description.xml: BopomoAnnotateJob.py
	sed -i 's/<version value="[^"]*"/<version value="v'`date +%y.%m.%d.%H%S`'"/' $@

.PHONY: BopomoAnnotate.oxt

VPATH=src
