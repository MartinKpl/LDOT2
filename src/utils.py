import json, os, sys

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

def getSiteIps(site: str, filter: str = ""):
    rawIps = json.loads(nyxquery_site_ips_json(site))
    ips = []
    for name in rawIps:
        cleanName = name.split(".")[0]
        if filter != "":
            if filter in cleanName or filter in "0000":
                ips.append(["0000", rawIps[name]["ip"], cleanName])
        else:
            ips.append(["0000", rawIps[name]["ip"], cleanName])

    return ips

def getSites():
    rawSites = json.loads(nyxquery_sites_json())

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