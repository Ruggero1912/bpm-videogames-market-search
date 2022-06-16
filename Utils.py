import os
from dotenv import load_dotenv, find_dotenv


def begin():
    load_dotenv(find_dotenv())   #By default loads .env configuration variables from current directory, searching in the file ".env"
    return True

class Utils:

    BEGUN                   = begin()

    def load_config(config_key : str) -> str :
        return os.getenv(config_key)

    def split_list(a : list, n : int) -> list:
        k, m = divmod(len(a), n)
        return list(a[i*k+min(i, m):(i+1)*k+min(i+1, m)] for i in range(n))