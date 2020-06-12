echo -e '\033[1mWelcome to Angel\033[0m\nA Reddit client for Linux'
echo 'User home is '$HOME
echo -e 'This script will install \033[215mAngel\033[0m on your hard drive'
read -e -p 'Press [Enter] to start or [Ctrl + c] to cancel'
cp ./assets/praw.ini $HOME/.config/praw.ini
sudo bash -c 'cp ./bin/angel /usr/bin/angel; mkdir /opt/angel-reddit; mkdir /opt/angel-reddit/temp; cp ./assets/angel.png /opt/angel-reddit/angel.png; cp ./assets/angel.ico /opt/angel-reddit/angel.ico; cp ./assets/text.png /opt/angel-reddit/text.png; cp ./assets/imagelink.png /opt/angel-reddit/imagelink.png; cp ./assets/link.png /opt/angel-reddit/link.png'
sudo bash -c 'chmod 777 /opt/angel-reddit/temp'
while true; do
	read -e -p 'Would you like to create a start menu shortcut? [Y]es or [N]o' yn
	case $yn in
		[Yy]* ) sudo bash -c 'cp ./assets/angel.desktop /usr/share/applications/angel.desktop'; break;;
		[Nn]* ) break;;
		* ) echo -e 'Please enter [Y]es or [N]o\';;
	esac
done
bash -c 'kbuildsycoca5'
echo -e '\033[1mAll Done!\033[0m Enjoy Angel, and please send feedback to: \033[1mhttps://github.com/hashbangstudios/angel'
