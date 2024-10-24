#! /bin/bash

create_password(){
  array=()
  for i in {a..z} {A..Z} {0..9};
    do
    array[$RANDOM]=$i
  done
  password=$(printf %s ${array[@]::10})
}


createGunicorn(){
  echo "[Unit]
  Description=Gunicorn instance to serve Management Portal
  After=network.target

  [Service]
  User=www-data
  Group=www-data
  WorkingDirectory=$SCRIPT_DIR
  Environment=\"PATH=$SCRIPT_DIR/.venv/bin\"
  ExecStart=$SCRIPT_DIR/.venv/bin/gunicorn --workers 3 --bind unix:myproject.sock -m 007 app:app
  Restart=on-failure
  RestartSec=5s

  [Install]
  WantedBy=multi-user.target" | sudo tee /etc/systemd/system/Management.service > /dev/null

  sudo usermod -aG $USER www-data
  sudo usermod -aG www-data $USER
  sudo systemctl daemon-reload
  sudo systemctl start Management.service
  sudo systemctl enable Management.service

  echo "Management Service has been setup"
  echo "Please configure Nginx or Apache to serve the Management Portal"
  echo "File path to serve: $SCRIPT_DIR/myproject.sock"
  echo -e "Example NGINX Setup: \n"
  echo "server {
      server_name <your_domain>;

      location / {
          include proxy_params;
          proxy_pass http://unix:$SCRIPT_DIR/myproject.sock;
      }
  }
  "
}

if [ "$EUID" -eq 0 ]
  then echo "Do not run as root. This script will ask for sudo permissions when needed."
  exit
fi
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )


echo 'Checking if Python PPA is installed...'

if ! grep -q "deb .*deadsnakes/ppa" /etc/apt/sources.list /etc/apt/sources.list.d/*; then
  echo 'Adding Python PPA Repository'
  sudo add-apt-repository ppa:deadsnakes/ppa -y >> /dev/null
else
  echo "Found Python PPA"
fi


echo 'Updating Apt Repositories'
sudo apt-get update >> /dev/null

packages="python3.12-venv python3.12 python3.12-dev"

if [ -f /bin/mysql ]; then
  if [ -L /bin/mysql ]; then
    echo "MariaDB is already installed"
  else
    echo "WARNING: Mysql is currently installed. Installing MariaDB will replace mysql with symlinks to MariaDB"
    
    while true; do
      read -p "Would you still like to proceed and install MariaDB? " yn
      case $yn in
          [Yy]* ) break;;
          * ) echo "Cancelling installation"; exit 1;;
      esac
    done
    packages="$packages mariadb-server libmariadb3 libmariadb-dev"
  fi
else
  packages="$packages mariadb-server libmariadb3 libmariadb-dev"
fi

echo 'Installing Python and MariaDB Server'
sudo apt-get install $packages -y >> /dev/null


if [[ ! -d $SCRIPT_DIR/.venv ]];
then
  echo 'Creating Venv'
  python3.12 -m venv $SCRIPT_DIR/.venv >> /dev/null
  $SCRIPT_DIR/.venv/bin/pip install -r $SCRIPT_DIR/requirements.txt > /dev/null
fi

sudo mkdir -p /etc/cms/
sudo mkdir -p /var/log/cms/

sudo chown www:www-data /etc/cms
sudo chown www:www-data /var/log/cms


if [[ -z "`sudo mysql -qfsBe "SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME='management'" 2>&1`" ]];
then
	echo 'Initializing Database'
  for file in ./setup/*.sql; do
    echo "Running $file"
    sudo mysql < $file
  done

	create_password
  sudo mysql -qfsBe "GRANT SELECT,UPDATE,INSERT,DELETE on management.* to 'managementUser'@'localhost' identified by '$password';"
  echo "Creating conf.cfg file"
  echo "; This file should contain all your secret configuration information.

[GEN]
; Acceepted Values: test, prod
SMTP=test
DATA=test


[SMTP.TEST]
HOST=             ; The URI where your domain's SMTP mail server is
PORT=             ; The port that your domain's SMTP mail server is listening on
USER=             ; The username to the mailbox you want to access
PASS=             ; The password to the mailbox you want to access
SEND_AS=          ; If you're mailbox has 'alternate senders' you can fill put that name here to send mail from that address instead.

[SMTP.PROD]
HOST=
PORT=
USER=
PASS=
SEND_AS=

[DB.TEST]
HOST=localhost
PORT=3306
USER=managementUser
PASS=$password
NAME=management

[DB.PROD]
HOST=           ; The URI for the Production Database
PORT=           ; The Port for the Production Database
USER=           ; The Username for the Production Database
PASS=           ; The password for the Production Database
NAME=           ; The name of the Production Database
" | sudo tee /etc/cms/conf.cfg > /dev/null
else
	echo 'Database already found'
fi

if [[ ! -d /etc/systemd/system/Management.service ]];
then
    while true; do
        read -p "Do you wish to create a gunicorn instance to serve this program? " yn
        case $yn in
            [Yy]* ) createGunicorn break;;
            [Nn]* ) break;;
            * ) echo "Please answer yes or no.";;
        esac
    done
fi

sudo crontab -l &>/dev/null | grep "$SCRIPT_DIR/cron.sh"
if [[ $? ]];
then
  #write out current crontab
  sudo crontab -l > mycron 2> /dev/null || :
  sudo chown $USER mycron
  #echo new cron into cron file
  echo "0 0 * * * $SCRIPT_DIR/cron.sh" >> mycron
  #install new cron file
  sudo crontab mycron
  rm mycron
fi


source $SCRIPT_DIR/.venv/bin/activate