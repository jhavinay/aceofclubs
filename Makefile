test:
	cp aoctranslate.py rvgbot.py ~/git/saycbridge/src/player
	cd ~/git/saycbridge/src/player ; python3 rvgbot.py --help
	cd ~/git/saycbridge/src/player ; python3 rvgbot.py --player W
