make:
	python3 setup.py build
install:
	python3 setup.py install
	@echo -e '\033[1mWelcome to Angel\033[0m\nA Reddit client for Linux'
	@sudo bash -c 'mkdir /opt/angel-reddit; mkdir /opt/angel-reddit/temp; cp angel/assets/loading.gif /opt/angel-reddit/loading.gif; cp angel/assets/reddit.png /opt/angel-reddit/reddit.png; cp angel/assets/upvote.png /opt/angel-reddit/upvote.png; cp angel/assets/downvote.png /opt/angel-reddit/downvote.png; cp angel/assets/angel.png /opt/angel-reddit/angel.png; cp angel/assets/angel.ico /opt/angel-reddit/angel.ico; cp angel/assets/text.png /opt/angel-reddit/text.png; cp angel/assets/imagelink.png /opt/angel-reddit/imagelink.png; cp angel/assets/link.png /opt/angel-reddit/link.png; cp angel/assets/mask.png /opt/angel-reddit/mask.png; cp angel/assets/default.png /opt/angel-reddit/default.png'
	@sudo bash -c 'chmod 777 /opt/angel-reddit/temp'
	@sudo bash -c 'cp angel/assets/angel.desktop /usr/share/applications/angel.desktop'
	@echo -e 'All Done! Enjoy Angel, and please send feedback to: \033[1mhttps://github.com/hashbangstudios/angel'
	@rm -r dist/
	@rm -r build/
	@rm -r angel.egg-info/
uninstall:
	@sudo bash -c 'rm -r /opt/angel-reddit'
	@sudo bash -c 'rm /usr/local/bin/angel'
	@sudo bash -c 'rm /usr/share/applications/angel.desktop'
	ENVHOME = ${HOME}
	@sudo rm ENVHOME/.config/praw.ini
test:
	@sudo -H pip install pytest coverage
	@pytest -s
	@coverage xml angel/__init__.py
