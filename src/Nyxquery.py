# Worker thread for fetching data
import time

from PyQt5.QtCore import QThread, pyqtSignal
from utils import getSiteIps, getSites


class Nyxquery(QThread):
    # Signal to indicate that data fetching is complete
    site_ips_fetched = pyqtSignal(list)
    sites_fetched = pyqtSignal(list)

    site = ""
    isGetIps = False
    def run(self):
        if self.isGetIps:
            ips = getSiteIps(self.site)
            print("Ips fetched successfully!")
            self.site_ips_fetched.emit(ips)
        else:
            sites = getSites()
            print("Ips fetched successfully!")
            self.sites_fetched.emit(sites)

    def getSites(self):
        self.sites_fetched.emit("Data has been fetched successfully!")
        self.isGetIps = False
    def getSiteIps(self, site):
       self.site = site
       self.start()
       self.isGetIps = True
