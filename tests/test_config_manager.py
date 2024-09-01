import pytest
import json
import xml.etree.ElementTree as ET
import csv
from src.config_manager import ConfigManager
import os


# Define constants for test filenames
TEST_JSON = 'config.json'
TEST_XML = 'config.xml'
TEST_CSV = 'config.csv'


@pytest.fixture()
def config_manager():
    return ConfigManager()


@pytest.fixture(scope='function', autouse=True)
def cleanup_files():
    # Clean up files created during tests
    yield
    for file_path in [TEST_JSON, TEST_XML, TEST_CSV]:
        if os.path.exists(file_path):
            os.remove(file_path)

    # Clean up backup files
    backup_dir = 'config-backups'
    if os.path.exists(backup_dir):
        for backup_file in os.listdir(backup_dir):
            os.remove(os.path.join(backup_dir, backup_file))
        os.rmdir(backup_dir)  # Remove the backup directory if empty


def test_can_instantiate_config_manager() -> None:
    handler = ConfigManager()
    assert handler is not None


def test_can_read_json_file(tmp_path):
    config_data = {"name": "Test", "version": 1.0} # create data set
    json_file = tmp_path / "config.json"           # create a temp json file
    with json_file.open("w") as f:
        json.dump(config_data, f)                  # write data set to json file
    manager = ConfigManager()                      # generate an object
    data = manager.read_json(json_file)            # data must be json file content
    assert data == config_data                     # check if it is so


def test_can_read_xml_file(tmp_path):
    xml_content = """<config>
                        <name>Test</name>
                        <version>1.0</version>
                     </config>"""
    xml_file = tmp_path / "config.xml"
    with xml_file.open("w") as file:
        file.write(xml_content)
    manager = ConfigManager()
    data = manager.read_xml(xml_file)
    print(data)
    assert data ==  {'name': 'Test', 'version': '1.0'}


def test_can_read_csv_file(tmp_path):
    csv_content = "name,version\nTest,1.0\n"
    csv_file = tmp_path / "config.csv"
    with csv_file.open("w") as file:
        file.write(csv_content)
    manager = ConfigManager()
    data = manager.read_csv(csv_file)
    assert data == [{"name": "Test", "version": "1.0"}]


def test_write_json(config_manager):
    data = {"name": "Test", "version": "1.0"}
    config_manager.write_json('test.json', data)

    # Verify the contents of the JSON file
    with open('test.json', 'r') as f:
        loaded_data = json.load(f)
        assert loaded_data == data


def test_write_xml(config_manager):
    data = {"name": "Test", "version": "1.0"}
    config_manager.write_xml('test.xml', data)

    # Verify the contents of the XML file
    tree = ET.parse('test.xml')
    root = tree.getroot()

    loaded_data = {child.tag: child.text for child in root}
    assert loaded_data == data


def test_write_csv(config_manager):
    data = [{"name": "Test", "version": "1.0"}, {"name": "Example", "version": "2.0"}]
    config_manager.write_csv('test.csv', data)

    # Verify the contents of the CSV file
    with open('test.csv', mode='r') as f:
        reader = csv.DictReader(f)
        loaded_data = [row for row in reader]

    assert loaded_data == data


def test_write_json_invalid_data_type(config_manager):
    with pytest.raises(TypeError):
        config_manager.write_json('test.json', "Invalid data type")


def test_write_xml_invalid_data_type(config_manager):
    with pytest.raises(TypeError):
        config_manager.write_xml('test.xml', "Invalid data type")


def test_write_csv_invalid_data_type(config_manager):
    with pytest.raises(TypeError):
        config_manager.write_csv('test.csv', "Invalid data type")


def test_write_json_empty_data(config_manager):
    config_manager.write_json('test.json', {})
    with open('test.json', 'r') as f:
        loaded_data = json.load(f)
        assert loaded_data == {}


def test_write_xml_empty_data(config_manager):
    config_manager.write_xml('test.xml', {})
    tree = ET.parse('test.xml')
    root = tree.getroot()
    assert len(root) == 0  # Should be empty


def test_write_csv_empty_data(config_manager):
    config_manager.write_csv('test.csv', [])
    with open('test.csv', mode='r') as f:
        reader = csv.DictReader(f)
        loaded_data = [row for row in reader]
        assert loaded_data == []  # Should be empty


def test_backup_management_on_write_json(config_manager):
    data1 = {"name": "Test1", "version": "1.0"}
    data2 = {"name": "Test2", "version": "2.0"}
    # Write first data to JSON
    config_manager.write_json(TEST_JSON, data1)
    # Write second data to JSON
    config_manager.write_json(TEST_JSON, data2)
    # Now check for the backup after the first write
    backup_dir = 'config-backups'
    assert os.path.exists(backup_dir)
    assert len(os.listdir(backup_dir)) == 1  # Should have one backup after first write


def test_backup_management_on_write_xml(config_manager):
    data1 = {"name": "Test1", "version": "1.0"}
    data2 = {"name": "Test2", "version": "2.0"}
    # Write first data to XML
    config_manager.write_xml(TEST_XML, data1)
    # Write second data to XML to create a backup
    config_manager.write_xml(TEST_XML, data2)
    # Now check for the backup after the first write
    backup_dir = 'config-backups'
    assert os.path.exists(backup_dir)
    assert len(os.listdir(backup_dir)) == 1  # Should have one backup after first write


def test_backup_management_on_write_csv(config_manager):
    data1 = [{"name": "Test1", "version": "1.0"}]
    data2 = [{"name": "Test2", "version": "2.0"}]
    # Write first data to CSV
    config_manager.write_csv(TEST_CSV, data1)
    # Write second data to CSV to create a backup
    config_manager.write_csv(TEST_CSV, data2)
    # Now check for the backup after the first write
    backup_dir = 'config-backups'
    assert os.path.exists(backup_dir)
    assert len(os.listdir(backup_dir)) == 1  # Should have one backup after first write
