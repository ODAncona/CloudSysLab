# Creator: Francisco Mendonca (francisco.mendonca@hesge.ch)

import exoscale
import os
import time
from dotenv import load_dotenv

load_dotenv()


# Before using, please install exoscale-cli, and do:
#  exo c0onfig
#  Follow the instruction to create API keys.
#  And follow the instruction on how to use exoscale on python from:
#  https://www.exoscale.com/syslog/official-python-bindings-for-the-exoscale-api/


# Creates Exoscale Object
exo = exoscale.Exoscale()

# Create the zone object
zone_gva2 = exo.compute.get_zone("ch-gva-2")


# If the security group hasn't yet been created uncomment the following:

# if the security group has been crated uncomment the following:
# and comment out the previous one

try:
    security_group = exo.compute.get_security_group("tp1")
except:
    security_group = exo.compute.create_security_group("tp1")
    rules = [
        exoscale.api.compute.SecurityGroupRule.ingress(
            description="SSH",
            network_cidr="0.0.0.0/0",
            port="22",
            protocol="tcp",
        ),
        exoscale.api.compute.SecurityGroupRule.ingress(
            description="HTTP",
            network_cidr="0.0.0.0/0",
            port="80",
            protocol="tcp",
        ),
        exoscale.api.compute.SecurityGroupRule.ingress(
            description="HTTPS",
            network_cidr="0.0.0.0/0",
            port="443",
            protocol="tcp",
        ),
    ]

    for rule in rules:
        security_group.add_rule(rule)

print("Creating backend instance...", end = ' ')
backend_instance = exo.compute.create_instance(
    name = "backend",
    zone = zone_gva2,
    type = exo.compute.get_instance_type("small"),
    template = list(
        exo.compute.list_instance_templates(
            zone_gva2,
            "Linux Ubuntu 20.04 LTS 64-bit")
    )[0],
    volume_size = 50,
    security_groups = [ security_group ],
    ssh_key = exo.compute.get_ssh_key("main"),
    user_data = """#cloud-config
    package_update: true
    packages:
    - git
    - npm
    runcmd:
    - git clone https://github.com/ODAncona/CloudSysLab.git
    - cd CloudSysLab/pw1/backend
    - sudo npm i
    - sudo node index.js
    """
)
print(backend_instance.ipv4_address)

print("Creating frontend instance...", end = ' ')
frontend_instance = exo.compute.create_instance(
    name = "frontend",
    zone = zone_gva2,
    type = exo.compute.get_instance_type("small"),
    template = list(
        exo.compute.list_instance_templates(
            zone_gva2,
            "Linux Ubuntu 20.04 LTS 64-bit")
    )[0],
    volume_size = 50,
    security_groups = [ security_group ],
    ssh_key = exo.compute.get_ssh_key("main"),
    user_data = """#cloud-config
    package_update: true
    packages:
    - git
    - nginx
    runcmd:
    - git clone https://github.com/ODAncona/CloudSysLab.git
    - sudo mv CloudSysLab/frontend/front.html /var/www/html/index.html
    - sudo mv CloudSysLab/frontend/default /etc/nginx/sites-available/default
    - sudo nginx -t
    """
)
print(frontend_instance.ipv4_address)

instances = [ frontend_instance, backend_instance ]

print("Instances created.")

# Bucket
print('Creating bucket...')
images_bucket = exo.storage.create_bucket("hesso-cloud-gr7-images", zone="ch-gva-2")

# Insert file in bucket
print("Writing image to bucket...")
file_index = images_bucket.put_file("img.jpg", "imp.jpg")
file_index.set_acl('public-read')

# List files in bucket
print(images_bucket.list_files())

print('Bucket created.')
input('Infrastructure is setup! Press any key to teardown...')

# Delete all files
print("Deleting image...")
for f in images_bucket.list_files():
    print("Deleting: ", f)
    f.delete()

# Delete Bucket
print("Deleting bucket...")
images_bucket.delete()

print("Deleting instances...")
for instance in instances:
    instance.delete()
