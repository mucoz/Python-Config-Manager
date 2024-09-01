import pytest
from src.config_manager import ConfigManager


if __name__ == "__main__":
    config_manager = ConfigManager()
    data = config_manager.read_csv("file.csv")

