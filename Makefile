coretests:
	cp aoctranslate.py rvgbot.py ~/git/saycbridge/src/player
	cd ~/git/saycbridge/src/player ; python3 aoctranslate.py
	cd ~/git/saycbridge/src/player ; python3 rvgbot.py --help

realtest: coretests
	cd ~/git/saycbridge/src/player ; python3 rvgbot.py --player W
