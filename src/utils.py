import json, os, sys
import subprocess
import time
from typing import List

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QApplication
from pynput import keyboard
from pynput.keyboard import Controller

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
    json_file_path = "nyxquery-examples/ips_example.json" #resource_path("nyxquery-examples/ips_example.json")
    with open(json_file_path, "r") as f:
        return f.read()


def nyxquery_sites_json():
    json_file_path = "nyxquery-examples/sitelist.json" #resource_path("nyxquery-examples/sitelist.json")
    with open(json_file_path, "r") as f:
        return f.read()

lastRawIps = {}
def getSiteIps(site: str) -> list:
    use_mock = os.getenv('USE_MOCK', 'false').lower() == 'true'
    ips = []

    if use_mock:
        time.sleep(2)
        print("Using mock for nyxquery")
        rawIps = json.loads(nyxquery_site_ips_json(site))
    else:
        result = subprocess.run(f"nyxquery --site {site} --json", shell=True, capture_output=True, text=True)
        rawIps = json.loads(result.stdout)

    lastRawIps[site] = rawIps

    for name in rawIps:
        cleanName = name.split(".")[0]

        if "ums-privil-server" in cleanName:
            cleanName = f"nova{cleanName[-2:]}/{cleanName}"

        ips.append([rawIps[name]["ip"], cleanName, rawIps[name]["roles"]])

    return ips


def filterIps(rawIps: list, filter: str = "") -> list:
    #print(f"Filtering {filter}")
    ips = []
    for machine in rawIps:
        ip = machine[0]
        name = machine[1]
        if filter != "":
            if filter in name:
                ips.append([ip, name])
        else:
            ips.append([ip, name])

    return ips

def filterIpsByRole(rawIps: list, role: str = "") -> list:
    if role == "" or role == "All":
        return rawIps

    filteredIps = []
    for machine in rawIps:
        if role in machine[2]:
            filteredIps.append(machine)

    return filteredIps

def getSites():
    use_mock = os.getenv('USE_MOCK', 'false').lower() == 'true'
    rawSites = []

    if use_mock:
        time.sleep(2)
        rawSites = json.loads(nyxquery_sites_json())
    else:
        result = subprocess.run(f"nyxquery --site-list --json", shell=True, capture_output=True, text=True)
        rawSites = json.loads(result.stdout)

    sites = list(rawSites.keys())
    sites.sort()

    return sites


def getRoles():
    result = subprocess.run(f"nyxquery --role-list", shell=True, capture_output=True, text=True)
    rawRoles = result.stdout

    roles = rawRoles.split("\n")

    roles = ["All"] + sorted(roles, key=lambda x: (not "ims" in x, x))

    return roles


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
    print(f"Will ssh ip {ip}")
    if sys.platform == 'win32':
        os.system(f"start cmd /k ssh {ip}")
    else:
        os.system(f"gnome-terminal -- bash -c 'ssh {ip}'")
#gnome-terminal -- bash -c "ssh {ip}; exec bash"


def openCSSH(ips: List[str]):
    print(ips)
    if sys.platform == 'linux':
        os.system(f"gnome-terminal -- bash -c 'cssh {' '.join(ips)}'")


def get_json_file_path():
    home_dir = os.path.expanduser('~')
    json_file = os.path.join(home_dir, 'ldot2data.json')
    return json_file


initializedData = []


def read_json():
    """
    {
        "hotkeys": [
            [
                "test", #text to paste
                true, #active?
                "F2" #hotkey
            ],
            ...
        ],
        "scpConf": {
            "rsaPath": "",
            "username": "m.kaplan",
            "downloadPath": "/home/mkaplan/linprj/LDOT2/nyxquery-examples",
            "hotkey": "F12"
        },
        "quickFilters: ["filter1", "filter2", "filter3"]
    }
    """
    # Ensure the directory exists
    file_path = get_json_file_path()
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    # Check if the file exists, and create it with default content if not
    if not os.path.exists(file_path) and not initializedData:
        with open(file_path, 'w') as file:
            default_data = {'hotkeys': []}  # Define your default data here
            json.dump(default_data, file, indent=4)

    # Read the JSON data
    try:
        if not initializedData:
            with open(file_path, 'r') as file:
                data = json.load(file)
                return data
        else:
            return initializedData

    except IOError as e:
        print(f"Error reading file {file_path}: {e}")
        return {}


def write_json(data):
    file_path = get_json_file_path()
    try:
        with open(file_path, 'w') as file:
            json.dump(data, file, indent=4)
    except IOError as e:
        print(f"Error writing to file {file_path}: {e}")


def doSCP(data: list | dict, controller: Controller, site: str):
    '''
            "rsaPath": self.rsaInput.text(),
            "username": self.usernameInput.text(),
            "downloadPath": self.downloadInput.text(),
            "hotkey": self.combo_box.currentText()
            scp -i /home/m.kaplan/m.kaplan_PROD.rsa m.kaplan@extstg3-ums-privil-ase-01.ptstaging.ptec:/opt/local/tmp/server.log.359.20240513-115841-125.zst /home/m.kaplan/
    '''
    cb = QApplication.clipboard()
    filename = cb.text(mode=cb.Selection)
    if filename == "":
        filename = cb.text(mode=cb.Clipboard)
        if filename == "":
            print("Select the file to do the SCP to")
            return
    filename = filename.strip()

    fqdn = getFQDN(site)
    print("FQDN: ", fqdn)

    controller.press(keyboard.Key.backspace) # to remove the '~' that may be generated when pressing certain fn key
    controller.release(keyboard.Key.backspace)
    controller.press('q') #get out of less
    controller.release('q')
    controller.press(keyboard.Key.backspace)
    controller.release(keyboard.Key.backspace)

    controller.type(f"cp {filename} /opt/local/tmp/")
    controller.press(keyboard.Key.enter)
    time.sleep(0.1)
    controller.release(keyboard.Key.enter)
    time.sleep(0.2)
    controller.type(f"chmod 755 /opt/local/tmp/{filename}")
    controller.press(keyboard.Key.enter)
    time.sleep(0.1)
    controller.release(keyboard.Key.enter)

    command = f"scp -i {data.get('rsaPath','')} {data.get('username','')}@{fqdn}:/opt/local/tmp/{filename} {data.get('downloadPath','')}"
    os.system(f"gnome-terminal -- bash -c '{command}'")

def getFQDN(site: str)->str:
    '''
    WM_NAME(STRING) = "CSSH: 10.207.193.68"

    WM_NAME(STRING) = "m.kaplan@mitmega-ums-privil-peko-01:~"
    '''
    result = subprocess.run(f"xprop -id $(xprop -root 32x '\t$0' _NET_ACTIVE_WINDOW | cut -f 2) WM_NAME", shell=True, capture_output=True, text=True)
    windowName = result.stdout

    if "CSS" in windowName:
        windowName = windowName[windowName.index("CSSH: ")+len("CSSH: "):-2]

        for name in lastRawIps[site]:
            if lastRawIps[site][name]["ip"] == windowName:
                return lastRawIps[site][name]["fqdn"]
    else: #from ssh
        start = windowName.index('@') + 1
        end = windowName.index(':', start)
        windowName = windowName[start:end]

        for name in lastRawIps[site]:
            if windowName in name:
                return lastRawIps[site][name]["fqdn"]

    return ""
