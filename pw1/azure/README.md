# Python script

program tested with python3.7.5 in virtual env

- create resource group for VM
- create virtual network
- create virtual subnet
- create public IP
- create network interface
- create VM
- list VM
- delete resource group
- create resource group for storage
- create storage account
- show primary key and connection string
- create blob container with 2 differents methods
- upload file to Azure storage as blob
- list blobs
- downloal blob
- delete resource group

## Config

install python libraries

get the id from az account with the following command :

```console
pip install -r requirement.txt

az account list --all
export AZURE_SUBSCRIPTION_ID="XXXX-XXX"
```

## Use Python API

Run the code :

```console
python azure-api-2022.py
```

## Azure storage architecture

![azure schema](storage_schema.png)

image source : https://learn.microsoft.com/en-us/azure/storage/blobs/storage-quickstart-blobs-python?tabs=environment-variable-windows#object-model
