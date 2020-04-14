from lastversion import lastversion
from collections import namedtuple
import os
import json
import argparse
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

    def get_json_file(self) -> dict:
        with open(os.path.abspath(self.json_file_name)) as file_name:
            return json.load(file_name)

    @staticmethod
    def json_decoder(extensions_parameters) -> tuple:
        return namedtuple('X', extensions_parameters.keys())(*extensions_parameters.values())

    def get_json_content(self) -> str:
        json_string = json.dumps(self.get_json_file(), indent=4)
        return json.loads(json_string, object_hook=JsonFile.json_decoder)


class ReleaseVersion:
    def __init__(self, file_name, file_content, version):
        self.file_name = file_name
        self.file_content = file_content
        self.version = version

    @staticmethod
    def get_last_released_version() -> str:
        """
        Returns last released version from GitHub tag
        :return: str
        """
        repository_name = sys.argv[1]
        repository_to_clone = Definition.SHOP_EXTENSION_PARTNER + "/" + repository_name
        return lastversion.latest(repository_to_clone, output_format='version', pre_ok=True)

    @staticmethod
    def get_current_release_version() -> str:
        """
        Returns current release version from branch name
        :return: str
        """
        repo = git.Repo(search_parent_directories=True)
        branch = repo.active_branch
        return re.sub('[^\d\.]', '', branch.name)

    def get_version_differences(self) -> list:
        """
        Returns list of version differences
        :return: list
        """
        self.file_name = open(ExtensionVersionUpdater.get_filename_path(str(self.file_name)), 'r')
        for file_line in self.file_name.readlines():
            if self.version in file_line and str(ReleaseVersion.get_last_released_version()) in file_line:
                self.file_content.append(file_line.replace(str(ReleaseVersion.get_last_released_version()), ReleaseVersion.get_current_release_version()))
            else:
                self.file_content.append(file_line)
        return self.file_content


class ExtensionVersionUpdater:
    def __init__(self, extension_name):
        self.extension_name = extension_name

    @staticmethod
    def get_filename_path(file_name):
        """
        Returns filename path
        :return: string
        """
        file_path = None
        current_path = os.getcwd()
        for root, dirs, files in os.walk(current_path):
            if file_name in files:
                file_path = os.path.abspath(os.path.join(root, file_name))
        return file_path

    def update_release_version(self):
        naming_convention = Definition.EXTENSION_NAMING_CONVENTION
        if self.extension_name not in naming_convention:
            print('Unknown extension name!', file=sys.stderr)
            sys.exit(1)
        json_content = JsonFile(Definition.CONFIG_FILE_PATH)
        for extension_parameters in getattr(json_content.get_json_content().extensions, naming_convention[self.extension_name]):
            content = []
            release_version = ReleaseVersion(extension_parameters.filename, content, extension_parameters.version)
            release_version.get_version_differences()
            file_name = open(ExtensionVersionUpdater.get_filename_path(extension_parameters.filename), 'w')
            for file_line in content:
                file_name.write(file_line)
            file_name.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Provide shop extension name as an argument.')
    parser.add_argument('repository', metavar='extension name', type=str, help='shop extension name e.g. woocommerce-ee')
    args = parser.parse_args()
    extension_name = args.repository
    extension_updater = ExtensionVersionUpdater(extension_name)
    extension_updater.update_release_version()
