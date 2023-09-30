# Import the needed credential and management objects from the libraries.
from azure.identity import AzureCliCredential
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.compute import ComputeManagementClient
import os

# storage
# https://learn.microsoft.com/en-us/azure/developer/python/sdk/examples/azure-sdk-example-storage?tabs=bash
import os, random
# Import the needed management objects from the libraries. The azure.common library
# is installed automatically with the other libraries.
from azure.identity import AzureCliCredential
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.storage import StorageManagementClient
# Import the client object from the SDK library
from azure.storage.blob import BlobClient
import os, uuid
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient, __version__


print(f"Provisioning a virtual machine...some operations might take a minute or two.")

# Acquire a credential object using CLI-based authentication.
credential = AzureCliCredential()

# Retrieve subscription ID from environment variable.
subscription_id = os.environ["AZURE_SUBSCRIPTION_ID"]


# Step 1: Provision a resource group

# Obtain the management object for resources, using the credentials from the CLI login.
resource_client = ResourceManagementClient(credential, subscription_id)

# Constants we need in multiple places: the resource group name and the region
# in which we provision resources. You can change these values however you want.
RESOURCE_GROUP_NAME = "PythonAzureExample-VM-rg"
#LOCATION = "westus2"
LOCATION = "westeurope"

# Provision the resource group.
rg_result = resource_client.resource_groups.create_or_update(RESOURCE_GROUP_NAME,
    {
        "location": LOCATION
    }
)


print(f"Provisioned resource group {rg_result.name} in the {rg_result.location} region")

# For details on the previous code, see Example: Provision a resource group
# at https://docs.microsoft.com/azure/developer/python/azure-sdk-example-resource-group


# Step 2: provision a virtual network

# A virtual machine requires a network interface client (NIC). A NIC requires
# a virtual network and subnet along with an IP address. Therefore we must provision
# these downstream components first, then provision the NIC, after which we
# can provision the VM.

# Network and IP address names
VNET_NAME = "python-example-vnet"
SUBNET_NAME = "python-example-subnet"
IP_NAME = "python-example-ip"
IP_CONFIG_NAME = "python-example-ip-config"
NIC_NAME = "python-example-nic"

# Obtain the management object for networks
network_client = NetworkManagementClient(credential, subscription_id)

# Provision the virtual network and wait for completion
poller = network_client.virtual_networks.begin_create_or_update(RESOURCE_GROUP_NAME,
    VNET_NAME,
    {
        "location": LOCATION,
        "address_space": {
            "address_prefixes": ["10.0.0.0/16"]
        }
    }
)

vnet_result = poller.result()

print(f"Provisioned virtual network {vnet_result.name} with address prefixes {vnet_result.address_space.address_prefixes}")

# Step 3: Provision the subnet and wait for completion
poller = network_client.subnets.begin_create_or_update(RESOURCE_GROUP_NAME, 
    VNET_NAME, SUBNET_NAME,
    { "address_prefix": "10.0.0.0/24" }
)
subnet_result = poller.result()

print(f"Provisioned virtual subnet {subnet_result.name} with address prefix {subnet_result.address_prefix}")

# Step 4: Provision an IP address and wait for completion
poller = network_client.public_ip_addresses.begin_create_or_update(RESOURCE_GROUP_NAME,
    IP_NAME,
    {
        "location": LOCATION,
        "sku": { "name": "Standard" },
        "public_ip_allocation_method": "Static",
        "public_ip_address_version" : "IPV4"
    }
)

ip_address_result = poller.result()

print(f"Provisioned public IP address {ip_address_result.name} with address {ip_address_result.ip_address}")

# Step 5: Provision the network interface client
poller = network_client.network_interfaces.begin_create_or_update(RESOURCE_GROUP_NAME,
    NIC_NAME, 
    {
        "location": LOCATION,
        "ip_configurations": [ {
            "name": IP_CONFIG_NAME,
            "subnet": { "id": subnet_result.id },
            "public_ip_address": {"id": ip_address_result.id }
        }]
    }
)

nic_result = poller.result()

print(f"Provisioned network interface client {nic_result.name}")

# Step 6: Provision the virtual machine

# Obtain the management object for virtual machines
compute_client = ComputeManagementClient(credential, subscription_id)
network_client = NetworkManagementClient(credential, subscription_id)

VM_NAME = "AzureInstance"
USERNAME = "azureuser"
PASSWORD = "ChangePa$$w0rd24"

print(f"Provisioning virtual machine {VM_NAME}; this operation might take a few minutes.")

# Provision the VM specifying only minimal arguments, which defaults to an Ubuntu 18.04 VM
# on a Standard DS1 v2 plan with a public IP address and a default virtual network/subnet.

poller = compute_client.virtual_machines.begin_create_or_update(RESOURCE_GROUP_NAME, VM_NAME,
    {
        "location": LOCATION,
        "storage_profile": {
            "image_reference": {
                "publisher": 'Canonical',
                "offer": "UbuntuServer",
                "sku": "16.04.0-LTS",
                "version": "latest"
            }
        },
        "hardware_profile": {
            "vm_size": "Standard_DS1_v2"
        },
        "os_profile": {
            "computer_name": VM_NAME,
            "admin_username": USERNAME,
            "admin_password": PASSWORD
        },
        "network_profile": {
            "network_interfaces": [{
                "id": nic_result.id,
            }]
        }        
    }
)

vm_result = poller.result()

print(f"Provisioned virtual machine {vm_result.name}")

# https://stackoverflow.com/questions/58925397/how-could-i-list-azure-virtual-machines-using-python
# https://stackoverflow.com/questions/40728871/get-ip-from-vm-object-using-azure-sdk-in-python

# vm_list = compute_client.virtual_machines.list_all()
vm_list = compute_client.virtual_machines.list(RESOURCE_GROUP_NAME)

for vm in vm_list:
    general_view = vm.id.split("/")
    resource_group = general_view[4]
    vm_name = general_view[-1]
    vm = compute_client.virtual_machines.get(resource_group, vm_name, expand='instanceView')

    print("  name: ", vm.name)
    print("  type: ", vm.type)
    print("  location: ", vm.location)
    for stat in vm.instance_view.statuses:
        print("  code: ", stat.code)
    print("  osType: ", vm.storage_profile.os_disk.os_type)
    for interface in vm.network_profile.network_interfaces:
        name=" ".join(interface.id.split('/')[-1:])
        sub="".join(interface.id.split('/')[4])
        try:
            thing=network_client.network_interfaces.get(sub, name).ip_configurations
            for x in thing:
                print("  Private IP: ", x.private_ip_address)
                #print("  Public  IP: ", x.public_ip_address)
        except:
            print("nope")
    print('-----------------------------')    

input("press enter to delete resources\n")

# delete the resource group. begin_delete is asynchronous.
poller = resource_client.resource_groups.begin_delete(rg_result.name)
result = poller.result()

print(f"Ressource groups deleted")

## ---------- storage ----------##

# Acquire a credential object using CLI-based authentication.
credential = AzureCliCredential()

# Retrieve subscription ID from environment variable.
subscription_id = os.environ["AZURE_SUBSCRIPTION_ID"]

# Obtain the management object for resources.
resource_client = ResourceManagementClient(credential, subscription_id)

# Constants we need in multiple places: the resource group name and the region
# in which we provision resources. You can change these values however you want.
RESOURCE_GROUP_NAME = "PythonAzureExample-Storage-rg"
LOCATION = "westeurope"

# Step 1: Provision the resource group.

rg_result = resource_client.resource_groups.create_or_update(RESOURCE_GROUP_NAME,
    { "location": LOCATION })

print(f"Provisioned resource group {rg_result.name}")

# For details on the previous code, see Example: Provision a resource group
# at https://docs.microsoft.com/azure/developer/python/azure-sdk-example-resource-group


# Step 2: Provision the storage account, starting with a management object.

storage_client = StorageManagementClient(credential, subscription_id)

# This example uses the CLI profile credentials because we assume the script
# is being used to provision the resource in the same way the Azure CLI would be used.

STORAGE_ACCOUNT_NAME = f"pythonazurestorage{random.randint(1,100000):05}"

# You can replace the storage account here with any unique name. A random number is used
# by default, but note that the name changes every time you run this script.
# The name must be 3-24 lower case letters and numbers only.


# Check if the account name is available. Storage account names must be unique across
# Azure because they're used in URLs.
availability_result = storage_client.storage_accounts.check_name_availability(
    { "name": STORAGE_ACCOUNT_NAME }
)
# exit()
if not availability_result.name_available:
    print(f"Storage name {STORAGE_ACCOUNT_NAME} is already in use. Try another name.")
    
    input("press enter to delete resources\n")
    poller = resource_client.resource_groups.begin_delete(rg_result.name)
    result = poller.result()
    print(f"Ressource groups deleted")
    exit()

# The name is available, so provision the account
poller = storage_client.storage_accounts.begin_create(RESOURCE_GROUP_NAME, STORAGE_ACCOUNT_NAME,
    {
        "location" : LOCATION,
        "kind": "StorageV2",
        "sku": {"name": "Standard_LRS"}
    }
)

# Long-running operations return a poller object; calling poller.result()
# waits for completion.
account_result = poller.result()
print(f"Provisioned storage account {account_result.name}")


# Step 3: Retrieve the account's primary access key and generate a connection string.
keys = storage_client.storage_accounts.list_keys(RESOURCE_GROUP_NAME, STORAGE_ACCOUNT_NAME)

print(f"Primary key for storage account: {keys.keys[0].value}")

# Retrieve the connection string. Note that a connection
# string grants all permissions to the caller, making it less secure than obtaining a
# BlobClient object using credentials.
conn_string = f"DefaultEndpointsProtocol=https;EndpointSuffix=core.windows.net;AccountName={STORAGE_ACCOUNT_NAME};AccountKey={keys.keys[0].value}"

print(f"Connection string: {conn_string}")

# Step 4: Provision the blob container in the account (this call is synchronous)
CONTAINER_NAME = "blob-container-01"
container = storage_client.blob_containers.create(RESOURCE_GROUP_NAME, STORAGE_ACCOUNT_NAME, CONTAINER_NAME, {})

# The fourth argument is a required BlobContainer object, but because we don't need any
# special values there, so we just pass empty JSON.

print(f"Provisioned blob container {container.name} with first method")


# https://learn.microsoft.com/en-us/azure/storage/blobs/storage-quickstart-blobs-python?tabs=environment-variable-windows#download-blobs
try:
    #print("Azure Blob Storage v" + __version__ + " - Python quickstart sample")

    # Create the BlobServiceClient object which will be used to create a container client
    blob_service_client = BlobServiceClient.from_connection_string(conn_string)
    # Create a unique name for the container
    #container_name = str(uuid.uuid4())
    container_name = "azure-bucket"
    # Create the container
    container_client = blob_service_client.create_container(container_name)
    print(f"Provisioned blob container {container_name} with second method")

    # # # first create an empty file, if a file with the same name doens't exist.
    filename = "file-to-upload.txt"
    if not os.path.isfile(filename):
        f = open(filename, "a")
        f.write("Hello there, Azure Storage. I'm a friendly file ready to be stored in a blob.")
        f.close()
    # Create a blob client using the local file name as the name for the blob
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=filename)

    print("\nUploading to Azure Storage as blob:\n\t" + filename)

    # Upload the created file
    with open(filename, "rb") as data:
        blob_client.upload_blob(data)

    input("\nListing blobs... press enter")

    # List the blobs in the container
    blob_list = container_client.list_blobs()
    for blob in blob_list:
        print("\t" + blob.name)
        #print(blob)

    filename_downloaded = "file-downloaded.txt"
    print("\nDownloading blob:\n\t" + filename + " --> " + filename_downloaded + "\n")
    
    with open(filename_downloaded, "wb") as download_file:
        download_file.write(container_client.download_blob(filename).readall())


except Exception as ex:
    print('Exception:')
    print(ex)


input("press enter to delete resources\n")

# delete the resource group. begin_delete is asynchronous.
poller = resource_client.resource_groups.begin_delete(rg_result.name)
result = poller.result()

print(f"Ressource groups deleted")
