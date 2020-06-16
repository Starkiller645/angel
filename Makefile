build:
	@echo 'Building with PyInstaller'
	@pyinstaller --onefile --noconsole angel/angel.py
	@cp ./dist/angel ./bin/angel
	@cp ./dist/angel ./bin/angel-32
install:
	@bash -c 'cp ./assets/praw.ini /home/jacob/.config/praw.ini'\
arch = $(shell getconf LONG_BIT)\
	@echo arch
	@echo 'Welcome to Angel - A Reddit client for Linux'
ifeq '$(arch)' '32'
	@sudo bash -c 'cp ./bin/angel-32 /usr/bin/angel'
	@echo 'Copied Angel binary to /usr/bin/'
else
	@sudo bash -c 'cp ./bin/angel /usr/bin/angel'
	@echo 'Copied Angel binary to /usr/bin/'
endif
	@sudo bash -c 'mkdir /opt/angel-reddit; mkdir /opt/angel-reddit/temp; cp ./assets/upvote.png /opt/angel-reddit/upvote.png; cp ./assets/downvote.png /opt/angel-reddit/downvote.png; cp ./assets/angel.png /opt/angel-reddit/angel.png; cp ./assets/angel.ico /opt/angel-reddit/angel.ico; cp ./assets/text.png /opt/angel-reddit/text.png; cp ./assets/imagelink.png /opt/angel-reddit/imagelink.png; cp ./assets/link.png /opt/angel-reddit/link.png'
	@echo 'Copied asset files'
	@sudo chmod 775 /opt/angel-reddit/temp
	@echo 'Creating start menu shortcut...'
	@sudo bash -c 'cp ./assets/angel.desktop /usr/share/applications/angel.desktop; kbuildsycoca5;'
	@echo 'Done! Enjoy Angel, and please send feedback and bug reports to: https://github.com/hashbangstudios/angel'
