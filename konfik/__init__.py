import pkg_resources

__version__ = pkg_resources.get_distribution("konfik").version

from .main import Konfik
