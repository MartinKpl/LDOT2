import json, os, sys
import subprocess
from typing import List

from PyQt5 import QtCore, QtWidgets

class Machine:
    def __init__(self, code, ip, name):
        self.code = code
        self.ip = ip
        self.name = name


def resource_path(relative_path):
    """ Get the absolute path to the resource, works for dev and for PyInstaller """
    # Determine if we are running in a PyInstaller bundle
    if getattr(sys, 'frozen', False):
        # Running in PyInstaller bundle
        base_path = sys._MEIPASS
    else:
        # Running in development mode
        base_path = os.path.dirname(os.path.abspath(__file__))
        # Adjust the path to point to the project root
        base_path = os.path.abspath(os.path.join(base_path, '..'))
    return os.path.join(base_path, relative_path)


def nyxquery_site_ips_json(site: str):
    json_file_path = resource_path("nyxquery-examples/ips_example.json")
    with open(json_file_path, "r") as f:
        return f.read()


def nyxquery_sites_json():
    json_file_path = resource_path("nyxquery-examples/sitelist.json")
    with open(json_file_path, "r") as f:
        return f.read()


def getSiteIps(site: str, filter: str = "") -> list:
    use_mock = os.getenv('USE_MOCK', 'false').lower() == 'true'
    ips = []

    if use_mock:
        print("Using mock for nyxquery")
        rawIps = json.loads(nyxquery_site_ips_json(site))
    else:
        result = subprocess.run(f"nyxquey --site {site} --json", shell=True, capture_output=True, text=True)
        rawIps = json.loads(result.stdout)

    for name in rawIps:
        cleanName = name.split(".")[0]
        if filter != "":
            if filter in cleanName:
                ips.append([rawIps[name]["ip"], cleanName])
        else:
            ips.append([rawIps[name]["ip"], cleanName])

    return ips


def getSites():
    use_mock = os.getenv('USE_MOCK', 'false').lower() == 'true'
    rawSites = []

    if use_mock:
        rawSites = json.loads(nyxquery_sites_json())
    else:
        result = subprocess.run(f"nyxquey --site-list --json", shell=True, capture_output=True, text=True)
        rawSites = json.loads(result.stdout)

    return list(rawSites.keys())


def make_combo_box_searchable(combo_box):
    combo_box.setFocusPolicy(QtCore.Qt.StrongFocus)
    combo_box.setEditable(True)
    combo_box.setInsertPolicy(QtWidgets.QComboBox.NoInsert)

    filter_model = QtCore.QSortFilterProxyModel(combo_box)
    filter_model.setFilterCaseSensitivity(QtCore.Qt.CaseInsensitive)
    filter_model.setSourceModel(combo_box.model())

    completer = QtWidgets.QCompleter(filter_model, combo_box)
    completer.setCompletionMode(QtWidgets.QCompleter.UnfilteredPopupCompletion)

    combo_box.setCompleter(completer)
    combo_box.lineEdit().textEdited.connect(filter_model.setFilterFixedString)


def openSSH(ip: str):
    if sys.platform == 'win32':
        os.system(f"start cmd /k ssh {ip}")
    else:
        os.system(f"gnome-terminal -- bash -c 'ssh {ip}; exec bash'")
#gnome-terminal -- bash -c "ssh {ip}; exec bash"


def openCSSH(ips: List[str]):
    print(ips)
    if sys.platform == 'linux':
        os.system(f"gnome-terminal -- bash -c 'cssh {' '.join(ips)}; exec bash'")
