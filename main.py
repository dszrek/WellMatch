#!/usr/bin/python
import os
import pandas as pd

from PyQt5.QtWidgets import QFileDialog, QDialog, QMessageBox
from PyQt5.QtCore import QDir
from PyQt5.QtXml import QDomDocument
from qgis.core import QgsProject, QgsMapLayerStyle, QgsApplication, QgsVectorLayer, QgsRasterLayer, QgsRectangle, QgsCoordinateReferenceSystem, QgsLayerTreeLayer
from qgis.utils import iface

from .import_data_dialog import ImportDataDialog

PATH_PRJ = None
STYLE_PATH = os.path.dirname(os.path.realpath(__file__)) + os.path.sep + 'styles' + os.path.sep
CRS_1992 = QgsCoordinateReferenceSystem(2180)
dlg = None
adf = None

def dlg_main(_dlg):
    """Przekazanie referencji interfejsu dockwidget'u do zmiennej globalnej."""
    global dlg
    dlg = _dlg
    init()

def init():
    dlg.btn_open_prj.pressed.connect(open_project)
    dlg.btn_adf.pressed.connect(import_adf)
    dlg.btn_bdf.pressed.connect(import_bdf)

def init_extent():
    xmin = 170000
    xmax = 870000
    ymin = 120000
    ymax = 800000
    return QgsRectangle(xmin, ymin, xmax, ymax)


class LayerManager:
    """Menedżer warstw projektu."""
    def __init__(self, dlg):
        self.root = dlg.proj.layerTreeRoot()
        self.groups_tree = [
            {'name': 'WellMatch', 'level': 1, 'layers': ['A_1', 'A_2', 'B_1', 'B_2', 'C', 'A1B1', 'A1B2', 'A2B1', 'B_INNE']}
            ]
        self.lyrs = [
            {"source": "memory", "name": "A_1", "root": False, "parent": "WellMatch", "visible": True, "uri": "Point?crs=epsg:2180&field=id:string&field=name:string&index=yes", "style": "a1.qml"},
            {"source": "memory", "name": "A_2", "root": False, "parent": "WellMatch", "visible": True, "uri": "Point?crs=epsg:2180&field=id:string&field=name:string&index=yes", "style": "a2.qml"},
            {"source": "memory", "name": "B_1", "root": False, "parent": "WellMatch", "visible": True, "uri": "Point?crs=epsg:2180&field=id:string&field=name:string&index=yes", "style": "b1.qml"},
            {"source": "memory", "name": "B_2", "root": False, "parent": "WellMatch", "visible": True, "uri": "Point?crs=epsg:2180&field=id:string&field=name:string&index=yes", "style": "b2.qml"},
            {"source": "memory", "name": "C", "root": False, "parent": "WellMatch", "visible": True, "uri": "Point?crs=epsg:2180&field=id:string&field=name:string&index=yes", "style": "c.qml"},
            {"source": "memory", "name": "A1B1", "root": False, "parent": "WellMatch", "visible": True, "uri": "LineString?crs=epsg:2180&field=id:string&field=m_dist:int", "style": "a1b1.qml"},
            {"source": "memory", "name": "A1B2", "root": False, "parent": "WellMatch", "visible": True, "uri": "LineString?crs=epsg:2180&field=id:string&field=m_dist:int", "style": "a1b2.qml"},
            {"source": "memory", "name": "A2B1", "root": False, "parent": "WellMatch", "visible": True, "uri": "LineString?crs=epsg:2180&field=id:string&field=m_dist:int", "style": "a2b1.qml"},
            {"source": "memory", "name": "B_INNE", "root": False, "parent": "WellMatch", "visible": True, "uri": "Point?crs=epsg:2180&field=id:string&field=name:string&index=yes", "style": "b_inne.qml"}
            ]
        self.lyr_vis = [["B_INNE", True]]
        self.lyr_cnt = len(self.lyrs)
        self.lyrs_names = [i for s in [[v for k, v in d.items() if k == "name"] for d in self.lyrs] for i in s]

    def project_check(self):
        """Sprawdzenie struktury warstw projektu."""
        if len(dlg.proj.mapLayers()) == 0:
            # QGIS nie ma otwartego projektu, tworzy nowy:
            self.project_create()
            return True
        else:
            # QGIS ma otwarty projekt - sprawdzanie jego struktury:
            valid = self.structure_check()
            if valid:
                # Poprawa stylów warstw, jeśli pochodzą ze starszej wersji wtyczki:
                self.style_correction("A1B1","firstChildElement('labeling').firstChildElement('settings').firstChildElement('placement')", "placement", "3", f"{STYLE_PATH}a1b1.qml")
                self.style_correction("B_INNE","firstChildElement('labeling').firstChildElement('settings').firstChildElement('rendering')", "limitNumLabels", "0", f"{STYLE_PATH}b_inne.qml")
                return True
            else:
                m_text = f"Brak wymaganych warstw lub grup warstw w otwartym projekcie. Naciśnięcie Tak spowoduje przebudowanie struktury projektu, naciśnięcie Nie przerwie proces uruchamiania wtyczki."
                reply = QMessageBox.question(dlg.app, "WellMatch", m_text, QMessageBox.Yes, QMessageBox.No)
                if reply == QMessageBox.No:
                    return False
                else:
                    lyr_missing = self.structure_check(rebuild=True)
                    if len(lyr_missing) > 0:
                        result = self.layers_create(lyr_missing)
                        return result
                    else:
                        return True

    def style_correction(self, lyr_name, element_ref, attr, bad_val, style_file):
        """Aktualizuje styl warstwy, jeśli została utworzona przez starszą wersję wtyczki."""
        layer = QgsProject.instance().mapLayersByName(lyr_name)[0]
        if not layer:
            return
        style = QgsMapLayerStyle()
        style.readFromLayer(layer)
        xml_data = style.xmlData()
        dom_document = QDomDocument()
        dom_document.setContent(xml_data)
        root_element = dom_document.documentElement()
        attr_element = eval(f"root_element.{element_ref}")
        attr_val = attr_element.attribute(attr)
        if attr_val == bad_val:
            layer.loadNamedStyle(style_file)

    def get_google_layer(self):
        """Tworzenie warstwy z podkładem Google Map."""
        google_uri = "type=xyz&url=https://mt1.google.com/vt/lyrs%3Dm%26hl%3Dpl%26x%3D%7Bx%7D%26y%3D%7By%7D%26z%3D%7Bz%7D&zmax=18&zmin=0&crs=EPSG2180"
        return QgsRasterLayer(google_uri, 'Google Map', 'wms')

    def project_create(self):
        """Utworzenie nowego projektu QGIS."""
        iface.newProject(False)
        try:
            bmap = self.get_google_layer()
            bmap.renderer().setOpacity(0.75)
        except:
            bmap = None
        if bmap:
            dlg.proj.addMapLayer(bmap)
        else:
            print("Błąd przy załadowaniu WMS!")
        QgsApplication.processEvents()
        dlg.proj.setCrs(CRS_1992)
        canvas = iface.mapCanvas()
        canvas.setExtent(init_extent())
        self.groups_create()
        self.layers_create()
        self.layer_to_group_move(lyr_name="Google Map")
        return True

    def groups_create(self):
        """Utworzenie grup warstw w projekcie."""
        for grp in self.groups_tree:
            if grp["level"] == 1:
                # Utworzenie grup głównych:
                grp_node = self.root.addGroup(grp["name"])
                grp_node.setExpanded(True)
                if "subgroups" in grp:
                    # Utworzenie podgrup:
                    for sgrp in grp["subgroups"]:
                        sgrp_node = grp_node.addGroup(sgrp)
                        sgrp_node.setExpanded(False)

    def layers_create(self, missing=None):
        """Utworzenie warstw w projekcie. Podanie atrybutu 'missing' spowoduje, że tylko wybrane warstwy będą dodane."""
        # Ustalenie ilości dodawanych warstw:
        i_max = len(missing) if missing else self.lyr_cnt
        # Utworzenie listy ze słownikami warstw do dodania:
        lyrs = []
        if missing:
            for l_dict in self.lyrs:
                if l_dict["name"] in missing:
                    lyrs.append(l_dict)
        else:
            lyrs = self.lyrs
        i = 0
        # Dodanie warstw:
        for l_dict in lyrs:
            i += 1
            raw_uri = l_dict["uri"]
            uri = eval("f'{}'".format(raw_uri))
            if l_dict["source"] == "wms" or l_dict["source"] == "gdal":
                lyr = QgsRasterLayer(uri, l_dict["name"], l_dict["source"])
                lyr_required = False
            else:
                lyr = QgsVectorLayer(uri, l_dict["name"], l_dict["source"])
                lyr_required = True
            if not lyr.isValid() and not lyr_required:
                m_text = f'Nie udało się poprawnie wczytać podkładu mapowego: {l_dict["name"]}. Naciśnięcie Tak spowoduje kontynuowanie uruchamiania wtyczki (podkład mapowy nie będzie wyświetlany), naciśnięcie Nie przerwie proces uruchamiania wtyczki. Jeśli problem będzie się powtarzał, zaleca się powiadomienie administratora systemu.'
                reply = QMessageBox.question(dlg.app, "WellMatch", m_text, QMessageBox.Yes, QMessageBox.No)
                if reply == QMessageBox.No:
                    return False
            elif not lyr.isValid() and lyr_required:
                m_text = f'Nie udało się poprawnie wczytać warstwy: {l_dict["name"]}. Jeśli problem będzie się powtarzał, proszę o powiadomienie administratora systemu (dszr@pgi.gov.pl).'
                QMessageBox.critical(dlg.app, "WellMatch", m_text)
                return False
            if l_dict["source"] == "memory":
                lyr.setCustomProperty("skipMemoryLayersCheck", 1)
            if "crs" in l_dict:
                lyr.setCrs(CRS_1992)
            dlg.proj.addMapLayer(lyr, False)
            if l_dict["root"]:
                parent_grp = self.root
                parent_grp.insertChildNode(l_dict["pos"], QgsLayerTreeLayer(lyr))
                parent_grp.findLayer(lyr).setItemVisibilityChecked(l_dict["visible"])
            else:
                if "pos" in l_dict:
                    parent_grp = self.root.findGroup(l_dict["parent"])
                    parent_grp.insertChildNode(l_dict["pos"], QgsLayerTreeLayer(lyr))
                    parent_grp.findLayer(lyr).setItemVisibilityChecked(False)
                else:
                    parent_grp = self.root.findGroup(l_dict["parent"])
                    node = parent_grp.addLayer(lyr)
                    node.setItemVisibilityChecked(l_dict["visible"])
            lyr.loadNamedStyle(f'{STYLE_PATH}{l_dict["style"]}')
        return True

    def layers_check(self):
        """Zwraca, czy wszystkie niezbędne warstwy są obecne w projekcie."""
        lyrs = []
        missing = []
        # Utworzenie listy warstw, które znajdują się w projekcie:
        for lyr in dlg.proj.mapLayers().values():
            lyrs.append(lyr.name())
        # Sprawdzenie, czy wszystkie niezbędne warstwy istnieją w projekcie:
        for lyr in self.lyrs_names:
            if lyr not in lyrs:
                print(f"Brakuje warstwy: {lyr}")
                missing.append(lyr)
        return missing

    def structure_check(self, rebuild=False):
        """Zwraca, czy wszystkie niezbędne grupy i warstwy są obecne w projekcie (rebuild=False),
        albo przebudowuje strukturę projektu (przenosi lub tworzy grupy i przenosi warstwy do odpowiednich grup)
        i zwraca listę brakujących warstw (rebuild=True)."""
        missing = []
        for grp in self.groups_tree:
            parent_node = self.root
            grp_node = parent_node.findGroup(grp["name"]) if "name" in grp else parent_node
            if grp["level"] == 2:
                parent_node = self.root.findGroup(grp["parent"])
                grp_node = parent_node.findGroup(grp["name"])
            if not grp_node and not rebuild:
                return False
            elif not grp_node and rebuild:
                moved = self.group_move(parent_node, grp["name"])
                if not moved:
                    parent_node.addGroup(grp["name"])
                grp_node = parent_node.findGroup(grp["name"])
            for lyr_name in grp["layers"]:
                if not self.layer_in_group_found(grp_node, lyr_name) and not rebuild:
                    return False
                elif not self.layer_in_group_found(grp_node, lyr_name) and rebuild:
                    moved = self.layer_to_group_move(grp_node, lyr_name)
                    if not moved:
                        missing.append(lyr_name)
                        continue
                lyr = dlg.proj.mapLayersByName(lyr_name)[0]
                if not lyr.isValid():
                    dlg.proj.removeMapLayer(lyr)
                    missing.append(lyr_name)
        if missing:
            print(f"layer/structure_check - lista brakujących warstw:")
            print(missing)
        return missing if rebuild else True

    def group_move(self, parent_node, grp_name):
        """Przenoszenie grupy (jeśli istnieje) na właściwą pozycję w projekcie."""
        grp_node = self.root.findGroup(grp_name)
        if grp_node:
            # Grupa o podanej nazwie jest w projekcie, ale w innym miejscu i należy ją przenieść:
            parent = grp_node.parent()
            new_grp = grp_node.clone()
            parent_node.insertChildNode(0, new_grp)
            parent.removeChildNode(grp_node)
            return True
        else:
            return False

    def layer_in_group_found(self, grp_node, lyr_name):
        """Zwraca, czy warstwa o podanej nazwie znajduje się w podanej grupie."""
        for child in grp_node.children():
            if child.name() == lyr_name:
                return True
        return False

    def layer_to_group_move(self, grp_node=None, lyr_name=None):
        """Przenoszenie warstwy (jeśli istnieje) do właściwej grupy."""
        try:
            lyr = self.root.findLayer(dlg.proj.mapLayersByName(lyr_name)[0].id())
        except Exception as err:
            print(f"layers/layer_to_group_move: {err}")
            return False
        # Warstwa o podanej warstwie jest w projekcie, ale w innej grupie i należy ją przenieść:
        parent = lyr.parent()
        new_lyr = lyr.clone()
        # Przeniesienie do grupy (jeśli podana), albo na koniec legendy:
        grp_node.insertChildNode(0, new_lyr) if grp_node else self.root.insertChildNode(-1, new_lyr)
        parent.removeChildNode(lyr)
        return True

def open_project():
    """Załadowanie zapisanego projektu. Uruchamia się po naciśnięciu btn_open_prj."""
    global PATH_PRJ
    if dlg.gui_mode != "init":
        dlg.project_reset(load=False)
    dlg.gui_mode = "init"
    PATH_PRJ = file_dialog(is_folder=True)
    if not os.path.isdir(PATH_PRJ):
        dlg.lab_path_content.setText(">> Brak zdefiniowanego projektu <<")
        return
    dlg.lab_path_content.setText(PATH_PRJ)
    df_load()
    dlg.adf_sel_change()

def df_load():
    """Załadowanie dataframe'ów projektu."""
    # Próba wczytania zbioru danych A:
    f_path = f"{PATH_PRJ}{os.path.sep}adf.parq"
    if os.path.isfile(f_path):
        dlg.load_adf(load_parq(f_path))
    else:
        check_files()
        return
    # Próba wczytania zbioru danych B:
    idfs = idfs_load()
    if not idfs:  # Nie ma kompletu plików
        check_files()
        return
    dlg.load_idf(idfs)
    f_path = f"{PATH_PRJ}{os.path.sep}bdf.parq"
    dlg.load_bdf(load_parq(f_path))
    dlg.calc_params_max()
    # Próba wczytania abdf:
    f_path = f"{PATH_PRJ}{os.path.sep}abdf.parq"
    if not os.path.isfile(f_path):
        dlg.abdf = pd.DataFrame(columns=['a_idx', 'b_idx', 'ab'])
        dlg.abdf['a_idx'] = dlg.abdf['a_idx'].astype('int64')
        dlg.abdf['b_idx'] = dlg.abdf['b_idx'].astype('int64')
        dlg.abdf['ab'] = dlg.abdf['ab'].astype('int64')
        try:
            dlg.abdf.to_parquet(f_path, compression='gzip')
        except Exception as err:
            print(err)
    else:
        dlg.abdf = load_parq(f_path)
    # Próba wczytania badf:
    f_path = f"{PATH_PRJ}{os.path.sep}badf.parq"
    if not os.path.isfile(f_path):
        dlg.badf = pd.DataFrame(columns=['b_idx', 'a_idx', 'ba'])
        dlg.badf['b_idx'] = dlg.badf['b_idx'].astype('int64')
        dlg.badf['a_idx'] = dlg.badf['a_idx'].astype('int64')
        dlg.badf['ba'] = dlg.badf['ba'].astype('int64')
        try:
            dlg.badf.to_parquet(f_path, compression='gzip')
        except Exception as err:
            print(err)
    else:
        dlg.badf = load_parq(f_path)
    # Próba wczytania cdf:
    f_path = f"{PATH_PRJ}{os.path.sep}cdf.parq"
    if not os.path.isfile(f_path):
        dlg.cdf = pd.DataFrame(columns=['a_idx', 'X', 'Y'])
        dlg.cdf['a_idx'] = dlg.cdf['a_idx'].astype('int64')
        dlg.cdf['X'] = dlg.cdf['X'].astype('float64')
        dlg.cdf['Y'] = dlg.cdf['Y'].astype('float64')
        dlg.cdf.to_parquet(f_path, compression='gzip')
    else:
        dlg.cdf = load_parq(f_path)
        dlg.cdf['a_idx'] = pd.to_numeric(dlg.cdf['a_idx'], downcast='integer')

def idfs_load():
    """Zwraca dataframe'y indeksów z bazy B. Pusty, jeśli nie ma kompletu plików."""
    bdfs = [['bdf', 'bdf'], ['Z', 'zdf'], ['H', 'hdf'], ['ROK', 'rdf']]
    imp_dfs = []
    for df in bdfs:
        f_path = f"{PATH_PRJ}{os.path.sep}{df[1]}.parq"
        if not os.path.isfile(f_path):
            return
        else:
            if df[0] != 'bdf':
                imp_dfs.append([df[0], load_parq(f_path)])
    return imp_dfs

def import_adf():
    """Import .csv z danymi bazy A. Uruchamia się po naciśnięciu btn_adf."""
    global dlg
    try:
        a_csv = load_csv()
    except:
        return
    if a_csv is None:
        return
    dlg.impdlg = ImportDataDialog(a_csv, 'A', dlg)
    dlg.impdlg.show()

def import_bdf():
    """Import .csv z danymi bazy B. Uruchamia się po naciśnięciu btn_bdf."""
    global bdf
    try:
        b_csv = load_csv()
    except:
        return
    if b_csv is None:
        return
    dlg.impdlg = ImportDataDialog(b_csv, 'B', dlg)
    dlg.impdlg.show()

def load_csv(df_path=None):
    """Załadowanie zawartości csv do pandas dataframe'u."""
    if not df_path:
        df_path = file_dialog(dir=PATH_PRJ, fmt='csv')
    try:
        df = pd.read_csv(df_path, error_bad_lines=False, encoding="cp1250", delimiter=";")
    except Exception as error:
        QMessageBox.critical(None, "WellMatch", f"{error}")
        return
    return df

def load_parq(df_path=None):
    """Załadowanie zawartości parq do pandas dataframe'u."""
    if not df_path:
        df_path = file_dialog(dir=PATH_PRJ, fmt='parq')
    try:
        df = pd.read_parquet(df_path)
    except Exception as error:
        print(error)
        return
    return df

def file_dialog(dir='', for_open=True, fmt='', is_folder=False):
    """Dialog z eksploratorem Windows. Otwieranie/tworzenie folderów i plików."""
    options = QFileDialog.Options()
    options |= QFileDialog.DontUseNativeDialog
    options |= QFileDialog.DontUseCustomDirectoryIcons
    dialog = QFileDialog()
    dialog.setOptions(options)
    dialog.setFilter(dialog.filter() | QDir.Hidden)
    if is_folder:  # Otwieranie folderu
        dialog.setFileMode(QFileDialog.DirectoryOnly)
    else:  # Otwieranie pliku
        dialog.setFileMode(QFileDialog.AnyFile)
    # Otwieranie / zapisywanie:
    dialog.setAcceptMode(QFileDialog.AcceptOpen) if for_open else dialog.setAcceptMode(QFileDialog.AcceptSave)
    # Ustawienie filtrowania rozszerzeń plików:
    if fmt != '' and not is_folder:
        dialog.setDefaultSuffix(fmt)
        dialog.setNameFilters([f'{fmt} (*.{fmt})'])
    # Ścieżka startowa:
    if dir != '':
        dialog.setDirectory(str(dir))
    else:
        dialog.setDirectory(str(os.environ["HOMEPATH"]))
    # Przekazanie ścieżki folderu/pliku:
    if dialog.exec_() == QDialog.Accepted:
        path = dialog.selectedFiles()[0]
        return path
    else:
        return ''

def check_files():
    """Ustala wartość 'gui_mode' na podstawie zawartości folderu projektu."""
    base_files = ["adf.parq", "bdf.parq", "hdf.parq", "rdf.parq", "zdf.parq"]
    work_files = ["abdf.parq", "badf.parq"]
    # Sprawdzenie folderu 'data':
    has_data = True if os.path.isdir(f"{PATH_PRJ}{os.path.sep}data") else False
    # Sprawdzenie plików bazowych:
    has_base = True
    dlg.btn_adf.setText("Import bazy A")
    dlg.btn_adf.setEnabled(True)
    dlg.btn_bdf.setText("Import bazy B")
    dlg.btn_bdf.setEnabled(True)
    for file_name in base_files:
        if not os.path.isfile(f"{PATH_PRJ}{os.path.sep}{file_name}"):
            has_base = False
        else:
            if file_name == "adf.parq":
                dlg.btn_adf.setText("Baza A wczytana")
                dlg.btn_adf.setEnabled(False)
            if file_name == "bdf.parq":
                dlg.btn_bdf.setText("Baza B wczytana")
                dlg.btn_bdf.setEnabled(False)
    # Sprawdzenie plików roboczych:
    has_work = True
    for file_name in work_files:
        if not os.path.isfile(f"{PATH_PRJ}{os.path.sep}{file_name}"):
            has_work = False
            break
    # Utworzenie subfolderu 'data', jeśli nie istnieje i nie ma również work_files:
    if not has_data and not has_work:
        os.makedirs(f"{PATH_PRJ}{os.path.sep}data")
        has_data = True
    # Ustalenie wartości 'gui_mode':
    print(f"has_data: {has_data}, has_base: {has_base}, has_work: {has_work}")
    if has_data and not has_base and not has_work:
        dlg.gui_mode = "new"
    elif has_data and has_base:
        dlg.gui_mode = "automatic"
    elif not has_data and has_base and has_work:
        dlg.gui_mode = "manual"
