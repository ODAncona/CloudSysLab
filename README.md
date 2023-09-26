### Backend

```
sudo apt-get install git npm -y
git clone https://github.com/ODAncona/CloudSysLab.git
cd CloudSysLab/pw1/backend
npm i
sudo node index.js
```

### Fronted

```
sudo apt-get install git nginx -y
git clone https://github.com/ODAncona/CloudSysLab.git
sudo mv CloudSysLab/frontend/front.html /var/www/html/index.html
sudo mv CloudSysLab/frontend/default /etc/nginx/sites-available/default
sudo nginx -t
```

### Bucket

Placer une image dans le bucket