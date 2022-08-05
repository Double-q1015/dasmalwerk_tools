import os
import shutil
from urllib import response
import tqdm
import requests
import datetime
import logging
from bs4 import BeautifulSoup
from multiprocessing.pool import Pool

logging.basicConfig(format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s',
                    level=logging.DEBUG,
                    filename='dasmalwerk.log',
                    filemode='a')
log = logging.getLogger("das_malwerk")

class DasMalwerk():
    def __init__(self) -> None:
        self.date_str = str(datetime.date.today())
        self.base_path = os.path.join(os.getcwd(), self.date_str)
        if not os.path.exists(self.base_path):
            os.makedirs(self.base_path)

    def download_file(self, url:str) ->bool:
        """
        Download file with urls
        Args:
            url:(str) The url of file.
        
        Return:
            (bool) download success or not
        """
        try:
            response = requests.get(url)
            if response.status_code != 200:
                log.error("Download {} failed".format(url))
                return False

            file_name = url.split("/")[-1]
            with open(os.path.join(self.base_path, file_name), "wb") as fp:
                fp.write(response.content)
        except Exception as e:
            logging.error(e)
        return True

    def get_file_links(self) ->list:
        """
        Return:(list) The urls of files
        """
        url = "https://das-malwerk.herokuapp.com/"
        response = requests.get(url)
        if response.status_code != 200:
            return

        soup = BeautifulSoup(response.text, 'lxml')
        href_list = []
        data = soup.find_all("tr")[1:]

        for i in data:
            temp_attr = i.find("a").attrs
            if temp_attr:
                href_list.append(temp_attr.get("href", ""))

        with open("{}_file_link.txt".format(self.date_str), "w") as f:
            for i in href_list:
                f.write(i + "\n")
        return href_list


def main():
    """
    Download files using thread pools
    """
    malwerk = DasMalwerk()
    file_links = malwerk.get_file_links()
    if file_links:
        # for link in tqdm.tqdm(file_links):
        #     download_file(link)

        pool = Pool(os.cpu_count())
        for _ in tqdm.tqdm(pool.imap_unordered(malwerk.download_file, file_links), total = len(file_links)):
            print(_)
        pool.close()
        pool.join()


if __name__ == "__main__":
    main()