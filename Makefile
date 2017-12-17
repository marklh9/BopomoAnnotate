SRC= annotate.py registrar.py
SRC+=pythonpath/myhelper.py
SRC+=Addons.xcu Jobs.xcu
SRC+=description.xml description_en-US.txt description_zh-TW.txt license.txt
SRC+=phtab.pkl
SRC+=tool.png
SRC+=META-INF/manifest.xml

VER=v$(shell expr `date +%y` - 7)$(shell date +%m.%d%H%M)

install: bopomo.oxt
	unopkg add -f bopomo.oxt

test: install
	soffice --writer --norestore sample.fodt

bopomo.oxt: $(SRC)
	cd src && zip -r ../bopomo.oxt *

src/description.xml: $(SRC)
	sed -i 's/<version value="[^"]*"/<version value="'$(VER)'"/' $@

.PHONY: install test

VPATH=src
