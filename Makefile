make:
	python3 setup.py build
install:
	python3 setup.py install
	@echo -e '\033[1mWelcome to Angel\033[0m\nA Reddit client for Linux'
	@sudo bash -c 'mkdir /opt/angel-reddit; mkdir /opt/angel-reddit/temp; cp -r angel/assets/* /opt/angel-reddit/'
	@sudo bash -c 'chmod 777 /opt/angel-reddit/temp'
	@sudo bash -c 'cp angel/assets/angel.desktop /usr/share/applications/angel.desktop'
	@sudo bash -c 'cp -r angel/angellib /usr/lib/python3/dist-packages/'
	@echo -e 'All Done! Enjoy Angel, and please send feedback to: \033[1mhttps://github.com/Starkiller645/angel'
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
