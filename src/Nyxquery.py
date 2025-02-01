# Worker thread for fetching data
import time

from PyQt5.QtCore import QThread, pyqtSignal
from utils import getSiteIps, getSites, getRoles


class Nyxquery(QThread):
    # Signal to indicate that data fetching is complete
    site_ips_fetched = pyqtSignal(list)
    sites_fetched = pyqtSignal(list)
    roles_fetched = pyqtSignal(list)

    GET_SITES = 1
    GET_IPS = 2
    GET_ROLES = 3

    site = ""
    action = GET_SITES
    def run(self):
        if self.action == self.GET_IPS and self.site != "":
            ips = getSiteIps(self.site)
            print("Ips fetched successfully!")
            self.site_ips_fetched.emit(ips)
        elif self.action == self.GET_SITES:
            sites = getSites()
            print("Sites fetched successfully!")
            self.sites_fetched.emit(sites)
        elif self.action == self.GET_ROLES:
            roles = getRoles()
            print("Roles fetched successfully!")
            self.roles_fetched.emit(roles)

    def getSites(self):
        self.action = self.GET_SITES
        self.start()
    def getSiteIps(self, site):
       self.site = site
       self.action = self.GET_IPS
       self.start()
    def getRoles(self):
        self.action = self.GET_ROLES
        if self.isRunning():
            self.quit()  # Stop the thread first
            self.wait()
        self.start()
