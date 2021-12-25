following this tutorial: https://www.youtube.com/watch?v=goToXTC96Co
1. Logging in via PuTTY
2. updating and upgrading the Ubuntu distro.
```bash
apt update && apt upgrade
```
3. Set hostname to something you like
 ```bash
hostnamectl set-hostname vraagslaaf-server
#ook aanpasen in host file
mkdir etc
nano etc/hosts
#add a line with <server ip> <tab> hostname
```
4. Een limited user aan onze server toevoegen
```bash
adduser anton
```

Kies een wachtwoord.
Je kan je volledige naam ingeven, de andere info kan je blank laten
5. Add user to sudogroep
```bash
adduser anton sudo
```
6. exit en log in met je nieuwe ww
   
7. Evenuteel SSH key based authentication gebruiken:

https://www.linode.com/docs/guides/use-public-key-authentication-with-ssh/#windows
Remove the capability to login via root (as we have SSH keys)

8. Firewall
```bash
sudo apt install ufw
sudo ufw default allow outgoing
sudo ufw defualt deny incoming
sudo ufw allow ssh
#flask dev server
sudo ufw allow 5000

sudo ufw enable
```

9. install git and python
```bash
sudo apt install git
sudo apt install python3
sudo apt install python3-pip
```
10. Test app Nu zou je moeten kunnen je flask app runnen en het zou moeten werken

11. nginx
```bash
sudo apt install nginx
pip install gunicorn
#verwijder de default config file voor nginx
sudo rm /etc/nginx/sites-enabled/default
sudo nano /etc/nginx/sites-enabled/vraagslaaf
```
in die file maak iets dat hierop lijkt
https://github.com/CoreyMSchafer/code_snippets/blob/master/Python/Flask_Blog/snippets/nginx.conf

12. Allow http traffic and disallow testing traffic
```bash
sudo ufw allow http/tcp
sudo ufw delete allow 5000
sudo ufw enable
sudo systemctl restart nginx
```
je gaat een bad gateway krijgen als je probeert te connecteren
13. gunicorn
```bash
gunicorn -w (n+2) run:app
```
see number of cores with
```bash
nproc --all
```
Problem dak moest oplossen waren zombrie processen op port 8000, kan ik oplossen met https://amalgjose.com/2020/02/27/gunicorn-connection-in-use-0-0-0-0-8000/
```bash
sudo fuser -k 8000/tcp
```

14. supervisor
```bash
sudo apt install supervisor
#config file
sudo nano /etc/supervisor/conf.d/sample-flask.conf
```
make a config like this one
https://github.com/CoreyMSchafer/code_snippets/blob/master/Python/Flask_Blog/snippets/supervisor.conf
```bash
sudo mkdir -p /var/log/sample-flask
sudo touch /var/log/sample-flask/out.log
sudo touch /var/log/sample-flask/err.log
sudo supervisorctl reload
```









