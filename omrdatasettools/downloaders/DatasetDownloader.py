import os
import shutil
import urllib.parse as urlparse
import urllib.request as urllib2
from zipfile import ZipFile
from abc import ABC, abstractmethod


class DatasetDownloader(ABC):
    """ The abstract base class for classes that download a specific dataset """

    @abstractmethod
    def download_and_extract_dataset(self,
                                     destination_directory: str):
        """ Starts the download of the dataset and extracts it into the directory specified in the constructor
            :param destination_directory: The root directory, into which the data will be placed.
        """
        pass

    @abstractmethod
    def get_dataset_download_url(self) -> str:
        """ Returns the URL, where this dataset can be downloaded from directy """
        pass

    @abstractmethod
    def get_dataset_filename(self) -> str:
        """ Returns the filename for the ZIP-file that will be downloaded for this dataset """
        pass

    def extract_dataset(self, absolute_path_to_temp_folder: str):
        archive = ZipFile(self.get_dataset_filename(), "r")
        archive.extractall(absolute_path_to_temp_folder)
        archive.close()

    def clean_up_temp_directory(self, temp_directory):
        print("Deleting temporary directory {0}".format(temp_directory))
        shutil.rmtree(temp_directory)

    def download_file(self, url, destination_filename=None) -> str:
        u = urllib2.urlopen(url)
        scheme, netloc, path, query, fragment = urlparse.urlsplit(url)
        filename = os.path.basename(path)
        if not filename:
            filename = 'downloaded.file'
        if destination_filename:
            filename = destination_filename

        filename = os.path.abspath(filename)

        with open(filename, 'wb') as f:
            meta = u.info()
            meta_func = meta.getheaders if hasattr(meta, 'getheaders') else meta.get_all
            meta_length = meta_func("Content-Length")
            file_size = None
            if meta_length:
                file_size = int(meta_length[0])
            print("Downloading: {0} Bytes: {1} into {2}".format(url, file_size, filename))

            file_size_dl = 0
            block_sz = 8192
            status_counter = 0
            status_output_interval = 100
            while True:
                buffer = u.read(block_sz)
                if not buffer:
                    break

                file_size_dl += len(buffer)
                f.write(buffer)
                status = "{0:16}".format(file_size_dl)
                if file_size:
                    status += "   [{0:6.2f}%]".format(file_size_dl * 100 / file_size)
                status += chr(13)
                status_counter += 1
                if status_counter == status_output_interval:
                    status_counter = 0
                    print(status)
                    # print(status, end="", flush=True) Does not work unfortunately
            print()

        return filename
