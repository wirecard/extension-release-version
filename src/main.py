from lastversion import lastversion
from collections import namedtuple
from os import path
import json
import subprocess
import sys
import git
import re


class Definition:
    CONFIG_FILE_PATH = '/usr/bin/shop-extensions.json'
    SHOP_EXTENSION_PARTNER = 'wirecard'

    EXTENSION_NAMING_CONVENTION = {
        "paymentSDK-php": "paymentsdk",
        "prestashop-ee": "prestashop",
        "woocommerce-ee": "woocommerce",
        "opencart-ee": "opencart",
        "magento2-ee": "magento2",
        "shopware-ee": "shopware",
        "oxid-ee": "oxid",
        "magento-ee": "magento"
    }


class JsonFile:
    def __init__(self, json_file_name):
        self.json_file_name = json_file_name

    def json_file(self) -> dict:
        with open(path.abspath(self.json_file_name)) as file_name:
            return json.load(file_name)

    @staticmethod
    def json_decoder(extensions_parameters) -> tuple:
        return namedtuple('X', extensions_parameters.keys())(*extensions_parameters.values())

    def json_content(self) -> str:
        json_string = json.dumps(self.json_file(), indent=4)
        return json.loads(json_string, object_hook=JsonFile.json_decoder)


class ReleaseVersion:
    def __init__(self, file_name, file_content, version):
        self.file_name = file_name
        self.file_content = file_content
        self.version = version

    @staticmethod
    def last_released_version() -> str:
        """
        Returns last released version from GitHub tag
        :return: str
        """
        repository_name = sys.argv[1]
        repository_to_clone = Definition.SHOP_EXTENSION_PARTNER + "/" + repository_name
        return lastversion.latest(repository_to_clone, output_format='version', pre_ok=True)

    @staticmethod
    def current_release_version() -> str:
        """
        Returns current release version from branch name
        :return: str
        """
        repo = git.Repo(search_parent_directories=True)
        branch = repo.active_branch
        return re.sub('[^\d\.]', '', branch.name)

    def version_differences(self) -> list:
        """
        Returns list of version differences
        :return: list
        """
        self.file_name = open(path.abspath(subprocess.check_output("find . -name " + str(self.file_name), shell=True, text=True)).rstrip(), 'r')
        for file_line in self.file_name.readlines():
            if self.version in file_line and str(ReleaseVersion.last_released_version()) in file_line:
                self.file_content.append(file_line.replace(str(ReleaseVersion.last_released_version()), ReleaseVersion.current_release_version()))
            else:
                self.file_content.append(file_line)
        return self.file_content


class ExtensionVersionUpdater:
    def __init__(self, extension_name):
        self.extension_name = extension_name

    def update_release_version(self):
        naming_convention = Definition.EXTENSION_NAMING_CONVENTION
        if self.extension_name in naming_convention:
            json_content = JsonFile(Definition.CONFIG_FILE_PATH)
            for extension_parameters in getattr(json_content.json_content().extensions, naming_convention[self.extension_name]):
                content = []
                release_version = ReleaseVersion(extension_parameters.filename, content, extension_parameters.version)
                release_version.version_differences()
                file_name = open(path.abspath(subprocess.check_output("find . -name " + extension_parameters.filename, shell=True, text=True)).rstrip(), 'w')
                for file_line in content:
                    file_name.write(file_line)
                file_name.close()


if __name__ == "__main__":
    extension_name = sys.argv[1]
    extension_updater = ExtensionVersionUpdater(extension_name)
    extension_updater.update_release_version()
