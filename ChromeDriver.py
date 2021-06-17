from pathlib import Path
import requests
from tqdm import tqdm
from zipfile import ZipFile
from sys import platform

class ChromeDriver:

    def __init__(self, version=None, os=None):
        self.os_choices = {
            ("mac", "macintosh","mac64" "os x", "x") : "mac64",
            ("win", "windows", "win64", "win32") : "win32",
            ("linux", "linux64") : "linux64"
            }
        self.driver_name = "chromedriver"
        self.dl_base_url = "https://chromedriver.storage.googleapis.com"
        self.version_base_url = "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_"
        self.os = self.__resolve_os(os)
        self.version = self.__resolve_version(version)
        self.path = None

    def __resolve_os(self, __os):
        temp_os = None
        if  __os == None:
            temp_os = platform
        else:
            temp_os = __os
        for os_aliases in self.os_choices.keys():
            if temp_os.lower() in os_aliases:
                return self.os_choices[os_aliases]
        raise ValueError("# Could not resolve OS")

    def __resolve_version(self, __version):
        if __version == None:
            return "91.0.4472.77"
        else:
            return __version

    def __make_path(self, path):
        path.mkdir(parents=True, exist_ok=True)
        print("# Using Path: {}".format(path))
        return path

    def __resolve_path(self, __path):
        default_path = Path().absolute().joinpath("ChromeDriver_{}_{}".format(self.os, self.version))
        if not __path == None:
            path = Path(__path).absolute().joinpath("ChromeDriver_{}_{}".format(self.os, self.version))
            try:
                if not path.exists():
                    return self.__make_path(path)
                else:
                    if path.is_dir():
                        return self.__make_path(path)
                    else:
                        raise NotADirectoryError(path)
            except NotADirectoryError as err_dirPath:
                print("# Error: This is not a Directory Path : {}".format(err_dirPath))
                return self.__make_path(default_path)
            except (WindowsError, OSError) as err:
                print(err)
                return self.__make_path(default_path)
        else:
            return self.__make_path(default_path)


    def __check_for_driver(self, __overwrite=None, __path=None):
        self.path = self.__resolve_path(__path)
        toBeDownloaded = None
        if self.os == "win32":
            extension = ".exe"
        else:
            extension = ""
        driver_path = self.path.joinpath(self.driver_name + extension)
        try:
            if driver_path.exists():
                raise FileExistsError(driver_path)
        except FileExistsError as err:
            print("# Note: Driver already exists at : {}".format(err))
            if __overwrite == None:
                choice = input("# Over-write existing Driver ? [y/n] : ")
                if choice=='y' or choice=="Y":
                    __overwrite = True
                elif choice=="n" or choice=="N":
                    __overwrite = False
            if __overwrite:
                print("# Over-writing the existing Driver")
            toBeDownloaded = __overwrite
        else:
            toBeDownloaded = True
        finally:
            return toBeDownloaded

    def __get_driver_id(self):
        major_version = ".".join(self.version.split(".")[:-1])
        major_version_url = self.version_base_url+major_version
        response = requests.get(major_version_url)
        return response.text

    def __download_driver(self, __url):
        dl_file_path = self.path.joinpath(self.driver_name+".zip")
        print("# Fetching from : {}".format(__url))
        with requests.get(__url, stream=True) as response:
            total_size = int(response.headers.get('content-length', 0))
            block_size = 1024
            progress=tqdm(total=total_size, unit='iB', unit_scale=True, desc="# Downloading ")
            with open(dl_file_path, 'wb') as file:
                for data in response.iter_content(block_size):
                    if data:
                        progress.update(len(data))
                        file.write(data)
            progress.close()    

    def __extract_and_cleanup(self):
        target_dir_path = self.path
        file_path = self.path.joinpath(self.driver_name+".zip")
        print("# Extracting to : {}".format(target_dir_path))
        with ZipFile(file_path, 'r') as zip_ref:
            zip_ref.extractall(target_dir_path)
        print("# Deleting redundant files ...")
        file_path.unlink()

    def get_driver(self, path=None, overwrite=None):
        print("\n### Chrome Driver Downloader ###")
        if self.__check_for_driver(overwrite, path):
            print("# Downloading Driver ...")
            driver_dl_url = self.dl_base_url+"/"+self.__get_driver_id()+"/"+self.driver_name+"_"+self.os+".zip"
            self.__download_driver(driver_dl_url)
            self.__extract_and_cleanup()
        else:
            print("# Download skipped")
        print("# Done\n")
        return self.path.joinpath(self.driver_name+".exe")

if __name__ == "__main__":
    print("[1] Windows")
    print("[2] Linux")
    print("[3] Macintosh")
    os = input("Operating System [Press 'c' for current OS] : ")
    if os == 'c':
        os = None
    else:
        os_choices = {"1":"win32", "2":"linux64", "3":"mac64"}
        os = os_choices.get(os)

    version = input("Chrome Version Number [Press 'c' for current version] : ")
    if version == 'c':
        version = None

    target_dir = input("Folder Name [Press 'c' for current directory]: ")
    if target_dir == 'c':
        target_dir = None
        
    cd = ChromeDriver(version, os)
    cd.get_driver(target_dir)