import json
import xml.etree.ElementTree as ET
import csv
from typing import List, Dict
from logger import Logger
import os
import shutil
import datetime


class ConfigManager:
    def __init__(self):
        self._MAX_BACKUPS = 5  # Maximum number of backups to keep
        self._BACKUP_FOLDER_NAME = "config-backups"

    def _backup_file(self, file_path: str) -> None:
        """
        Create a backup of the specified file with a timestamp.

        Args:
            file_path (str): The path to the file to back up.

        Returns:
            None
        """
        if os.path.exists(file_path):
            # Create a backup directory if it doesn't exist
            backup_dir = self._BACKUP_FOLDER_NAME
            if not os.path.exists(backup_dir):
                os.makedirs(backup_dir)

            # Generate a timestamp for the backup file name
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            backup_path = os.path.join(backup_dir, f"{os.path.basename(file_path)}.{timestamp}.bak")

            # Use shutil.copy to copy the file
            try:
                shutil.copy(file_path, backup_path)
                Logger.info(f"Backup created at: '{backup_path}'")

                # Manage the number of backups
                self._manage_backups(backup_dir, os.path.basename(file_path))
            except Exception as e:
                Logger.error(f"Failed to create backup for '{file_path}': {e}")
        else:
            Logger.warn(f"File '{file_path}' does not exist. No backup created.")


    def _manage_backups(self, backup_dir: str, file_name: str) -> None:
        """
        Manage the number of backup files by deleting the oldest ones.

        Args:
            backup_dir (str): The directory where backups are stored.
            file_name (str): The name of the original file.

        Returns:
            None
        """

        # List all backups for the specific file
        backups = [f for f in os.listdir(backup_dir)
                   if f.startswith(file_name) and f.endswith('.bak')]

        # If there are more backups than allowed, delete the oldest
        while len(backups) > self._MAX_BACKUPS:
            oldest_backup = min(backups, key=lambda x: os.path.getctime(os.path.join(backup_dir, x)))
            os.remove(os.path.join(backup_dir, oldest_backup))
            Logger.info(f"Deleted old backup: '{oldest_backup}'")
            backups.remove(oldest_backup)


    def read_json(self, file_path: str) -> Dict:
        """
        Reads a JSON file and returns its contents as a dictionary.

        Args:
            file_path (str): The path to the JSON file.

        Returns:
            dict: The contents of the JSON file.
        """
        try:
            with open(file_path, "r") as file:
                data = json.load(file)
                Logger.info(f"Successfully read JSON file: '{file_path}'")
                return data
        except FileNotFoundError:
            Logger.error(f"Error: The file '{file_path}' was not found.")
            return {}
        except json.JSONDecodeError:
            Logger.error(f"Error: The file '{file_path}' is not a valid JSON file.")
            return {}


    def write_json(self, file_path: str, data: Dict) -> None:
        """
        Writes a dictionary to a JSON file.

        Args:
            file_path (str): The path to the JSON file to write to.
            data (dict): The dictionary containing data to write.

        Returns:
            None

        Raises:
            TypeError: If the provided data is not a dictionary.
        """
        if not isinstance(data, dict):
            Logger.error(f"An error occurred while writing JSON to '{file_path}': "
                         f"Excepted dictionary object but got {type(data)}")
            raise TypeError("data must be a dictionary")
        # Create a backup of the file before writing
        self._backup_file(file_path)
        try:
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=4)
                Logger.info(f"Successfully wrote JSON data to: '{file_path}'")
        except Exception as e:
            Logger.error(f"An error occurred while writing JSON to '{file_path}': {e}")


    def read_xml(self, file_path: str) -> Dict:
        """
        Reads an XML file and returns its contents as a dictionary.

        Args:
            file_path (str): The path to the XML file.

        Returns:
            dict: The contents of the XML file.
        """
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            config_data = {child.tag: child.text for child in root}
            Logger.info(f"Successfully read XML file: '{file_path}'")
            return config_data
        except FileNotFoundError:
            Logger.error(f"Error: The file '{file_path}' was not found.")
            return {}
        except ET.ParseError:
            Logger.error(f"Error: The file '{file_path}' is not a valid XML file.")
            return {}


    def write_xml(self, file_path: str, data: Dict) -> None:
        """
        Writes a dictionary to an XML file.

        Args:
            file_path (str): The path to the XML file to write to.
            data (dict): The dictionary containing data to write.

        Returns:
            None

        Raises:
            TypeError: If the provided data is not a dictionary.
        """
        if not isinstance(data, dict):
            Logger.error(f"An error occurred while writing XML to '{file_path}': "
                         f"Excepted dictionary object but got {type(data)}")
            raise TypeError("data must be a dictionary")
        # Create a backup of the file before writing
        self._backup_file(file_path)
        try:
            root = ET.Element("config")
            for key, value in data.items():
                child = ET.SubElement(root, key)
                child.text = value
            tree = ET.ElementTree(root)
            tree.write(file_path)
            Logger.info(f"Successfully wrote XML data to: '{file_path}'")
        except Exception as e:
            Logger.error(f"An error occurred while writing XML to '{file_path}': {e}")


    def read_csv(self, file_path: str) -> List[Dict]:
        """
        Reads a CSV file and returns its contents as a list of dictionaries.

        Args:
            file_path (str): The path to the CSV file.

        Returns:
            list of dict: The contents of the CSV file.
        """
        try:
            with open(file_path, "r") as file:
                reader = csv.DictReader(file)
                data = [row for row in reader]
                Logger.info(f"Successfully read CSV file: '{file_path}'")
                return data
        except FileNotFoundError:
            Logger.error(f"Error: The file '{file_path}' was not found.")
            return []
        except Exception as e:
            Logger.error(f"Error: An error occurred while reading the CSV file: {e}")
            return []


    def write_csv(self, file_path: str, data: List[Dict]) -> None:
        """
        Writes a list of dictionaries to a CSV file.

        Args:
            file_path (str): The path to the CSV file to write to.
            data (list of dict): The list of dictionaries containing data to write.

        Returns:
            None

        Raises:
            TypeError: If the provided data is not a list.
        """
        if not isinstance(data, list):
            Logger.error(f"An error occurred while writing CSV to '{file_path}': "
                         f"Excepted dictionary object but got {type(data)}")
            raise TypeError("data must be a list")
        # Create a backup of the file before writing
        self._backup_file(file_path)
        try:
            with open(file_path, mode='w', newline='') as f:
                if data:
                    writer = csv.DictWriter(f, fieldnames=data[0].keys())
                    writer.writeheader()
                    writer.writerows(data)
                    Logger.info(f"Successfully wrote CSV data to: '{file_path}'")
                else:
                    Logger.warn("No data to write to CSV.")
        except Exception as e:
            Logger.error(f"An error occurred while writing CSV to '{file_path}': {e}")
