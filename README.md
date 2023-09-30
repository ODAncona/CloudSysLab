### Backend

```
sudo apt-get update
sudo apt-get upgrade
sudo apt-get install git npm -y
git clone https://github.com/ODAncona/CloudSysLab.git
cd CloudSysLab/pw1/backend
npm ci
sudo node index.js
```

### Fronted

```
sudo apt-get update
sudo apt-get upgrade
sudo apt-get install git nginx
git clone https://github.com/ODAncona/CloudSysLab.git
sudo mv CloudSysLab/pw1/frontend/front.html /var/www/html/index.html
sudo mv CloudSysLab/pw1/frontend/default /etc/nginx/sites-available/default
sudo nginx -t
```

### Bucket

Placer une image dans le bucket