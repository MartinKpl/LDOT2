import json

from PyQt5 import QtCore, QtWidgets


class Machine:
    def __init__(self, code, ip, name):
        self.code = code
        self.ip = ip
        self.name = name

def nyxquery_site_ips_json(site: str):
    f = open("./../nyxquery-examples/ips_example.json", "r")
    return f.read()

def nyxquery_sites_json():
    f = open("./../nyxquery-examples/sitelist.json", "r")
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