# Container Action Template

Changes the versions according to the configuration file (shop-extension.json) in the calling repository.  
This can be used in an automated release workflow to change release version, as seen [here](https://github.com/wirecard/woocommerce-ee/blob/master/.github/workflows/change-release-version.yml)

## How to setup

Simply add the action to your workflow
````
- name: Change release version
  uses: wirecard/extension-version-check-action@master
  with:
    repository: <repository-name>
````
And adapt ````shop-extension.json```` to your repositories.  
Below you can find an [example configuration](#example-shop-extensionjson). 

## How to configure

The script takes the full configuration out of the ````shop-extension.json```` since it was created with the purpose 
to be used in several extension projects.

## Example shop-extension.json

### Mandatory example shop-extension.json
````json
{
  "extensions": {
    "prestashop": [
      {
        "filename": "wirecardpaymentgateway.php",
        "version": "VERSION"
      }
    ]
  }
}
````

## Short overview of the file structure

### main.py

The ```main.py``` file is the main file called through ```entrypoint.sh``` in the container.  
It calls the required objects in the correct order and executes the necessary methods.
