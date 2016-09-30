import pkg_resources


__version__ = pkg_resources.get_distribution("ethereum-alarm-clock-client").version


try:
    # load environment variables
    import dotenv
    dotenv.load_dotenv('.env')
except ImportError:
    pass
