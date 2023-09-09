from icrawler.builtin import GoogleImageCrawler
from icrawler import ImageDownloader
import time
from random import randint


class PrefixNameDownloader(ImageDownloader):

    def get_filename(self, task, default_ext):
        filename = super(PrefixNameDownloader, self).get_filename(task, default_ext)
        filename = filename.split(".")[0]
        return str(int(filename)) + "." + default_ext


class GoogleDownloader:
    @staticmethod
    def download_images(items_to_find, path):
        i = -1
        for item in items_to_find:
            google_crawler = GoogleImageCrawler(
                downloader_cls=PrefixNameDownloader,
                downloader_threads=4,
                storage={'root_dir': path})
            filters = dict(
                size='large',)
            google_crawler.crawl(item, min_size=(200, 200), filters=filters, max_num=1, file_idx_offset=i,
                                 overwrite=True, offset=randint(1, 40))
            i += 1
            max(i, len(items_to_find)-1)
        time.sleep(10)
