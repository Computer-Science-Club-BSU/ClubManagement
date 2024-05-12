#! /bin/bash

# This script does the following:
# 1. Installs Python3.12, Python3.12-venv, and MongoDB
# 2. Creates a MongoDB Account
# 3. Configures MongoDB to use Authentication
# 4. Creates a `.env` file that contains the DB authentication info
# 5. Creates a Python Venv and installs the required dependencies.

# echo "Installing 'Deadsnakes' PPA"
# sudo add-apt-repository ppa:deadsnakes/ppa -y &> /dev/null

# This function will create a random 10 character password.
create_password(){
  array=()
  for i in {a..z} {A..Z} {0..9};
    do
    array[$RANDOM]=$i
  done
  password=$(printf %s ${array[@]::10})
}


echo "Updating Apt"
sudo apt-get update &> /dev/null

echo "Installing the following packages:
    Python 3.12
    Python 3.12 Venv
    GNUPG
    curl"
sudo apt-get install python3.12 python3.12-venv gnupg curl -y &> /dev/null

apt list --installed | grep "mongodb" &> /dev/null
if [ $? -eq 1 ];
then

echo "Adding MongoDB Keyring"
curl -fsSL https://www.mongodb.org/static/pgp/server-7.0.asc | \
   sudo gpg -o /usr/share/keyrings/mongodb-server-7.0.gpg \
   --dearmor

echo "deb [ arch=amd64,arm64 signed-by=/usr/share/keyrings/mongodb-server-7.0.gpg ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/7.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-7.0.list

echo "Updating Apt"
sudo apt-get update -y &> /dev/null

echo "Installing MongoDB"
sudo apt-get install -y mongodb-org
echo "Starting MongoDB"
sudo systemctl enable mongod.service &> /dev/null


echo "Creating MongoDB User"
create_password
mongosh --eval 'use management' --eval "db.createUser(
    {
        user: \"management_user\",
        pwd: \"$password\",
        roles: [
            role: \"readWrite\", db: \"management\"
        ]
    }
)"
echo "export DB_HOST=localhost
export DB_USER=localhost
export DB_AUTH=management
export DB_PASSWORD=$password" > .env

else
echo "MongoDB Found, skipping configuration"

fi