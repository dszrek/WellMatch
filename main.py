#!/usr/bin/python
import os
import pandas as pd
import numpy as np

from PyQt5.QtWidgets import QFileDialog, QDialog, QMessageBox
from PyQt5.QtCore import QDir, QVariant
from qgis.core import QgsProject, QgsApplication, QgsVectorLayer, QgsRasterLayer, QgsRectangle, QgsGeometry, QgsWkbTypes, QgsCoordinateReferenceSystem, QgsCoordinateTransform, QgsPointXY, QgsField
from qgis.utils import iface

from .import_data_dialog import ImportDataDialog
from .classes import DataFrameModel

PATH_PRJ = None
STYLE_PATH = os.path.dirname(os.path.realpath(__file__)) + os.path.sep + 'styles' + os.path.sep
dlg = None
adf = None

def dlg_main(_dlg):
    """Przekazanie referencji interfejsu dockwidget'u do zmiennej globalnej."""
    global dlg
    dlg = _dlg
    init()
    create_qgis_project()
    create_layers()

def init():
    dlg.btn_new_prj.pressed.connect(new_project)
    dlg.btn_open_prj.pressed.connect(open_project)
    dlg.btn_adf.pressed.connect(import_adf)
    dlg.btn_bdf.pressed.connect(import_bdf)


def create_qgis_project():
    """Utworzenie nowego projektu QGIS."""
    iface.newProject(False)
    crs_1992 = QgsCoordinateReferenceSystem(2180)
    qprj = QgsProject.instance()
    # qprj.setCrs(crs_1992)
    # canvas.setExtent(init_extent())
    try:
        bmap = get_google_layer()
        bmap.renderer().setOpacity(0.75)
    except:
        bmap = None
    if bmap:
        qprj.addMapLayer(bmap)
    else:
        print("Błąd przy załadowaniu WMS!")
    QgsApplication.processEvents()
    qprj.setCrs(crs_1992)
    canvas = iface.mapCanvas()
    canvas.setExtent(init_extent())

def init_extent():
    xmin = 170000
    xmax = 870000
    ymin = 120000
    ymax = 800000
    return QgsRectangle(xmin, ymin, xmax, ymax)

def get_google_layer():
    google_uri = "type=xyz&url=https://mt1.google.com/vt/lyrs%3Dm%26hl%3Dpl%26x%3D%7Bx%7D%26y%3D%7By%7D%26z%3D%7Bz%7D&zmax=18&zmin=0&crs=EPSG2180"
    return QgsRasterLayer(google_uri, 'Google', 'wms')

def get_osm_layer():
    google_uri = 'type=xyz&url=https://a.tile.openstreetmap.org/%7Bz%7D/%7Bx%7D/%7By%7D.png&zmax=19&zmin=0&crs=EPSG2180'
    return QgsRasterLayer(google_uri, 'OSM', 'wms')

def create_layers():
    """Utworzenie warstw projektu."""
    uri_p = "Point?crs=epsg:2180&field=id:integer"
    uri_l = "LineString?crs=epsg:2180&field=id:integer"
    # B_INNE:
    b_inne = QgsVectorLayer(uri_p, "B_INNE", "memory")
    b_inne.setCustomProperty("skipMemoryLayersCheck", 1)
    pr = b_inne.dataProvider()
    pr.addAttributes([
                    QgsField('id', QVariant.String),
                    QgsField('name', QVariant.String)
                    ])
    b_inne.updateFields()
    QgsProject.instance().addMapLayer(b_inne)
    b_inne.loadNamedStyle(f"{STYLE_PATH}b_inne.qml")
    # A2B1:
    a2b1 = QgsVectorLayer(uri_l, "A2B1", "memory")
    a2b1.setCustomProperty("skipMemoryLayersCheck", 1)
    pr = a2b1.dataProvider()
    pr.addAttributes([
                    QgsField('m_dist', QVariant.Int)
                    ])
    a2b1.updateFields()
    QgsProject.instance().addMapLayer(a2b1)
    a2b1.loadNamedStyle(f"{STYLE_PATH}a2b1.qml")
    # A1B2:
    a1b2 = QgsVectorLayer(uri_l, "A1B2", "memory")
    a1b2.setCustomProperty("skipMemoryLayersCheck", 1)
    pr = a1b2.dataProvider()
    pr.addAttributes([
                    QgsField('m_dist', QVariant.Int)
                    ])
    a1b2.updateFields()
    QgsProject.instance().addMapLayer(a1b2)
    a1b2.loadNamedStyle(f"{STYLE_PATH}a1b2.qml")
    # A1B1:
    a1b1 = QgsVectorLayer(uri_l, "A1B1", "memory")
    a1b1.setCustomProperty("skipMemoryLayersCheck", 1)
    pr = a1b1.dataProvider()
    pr.addAttributes([
                    QgsField('m_dist', QVariant.Int)
                    ])
    a1b1.updateFields()
    QgsProject.instance().addMapLayer(a1b1)
    a1b1.loadNamedStyle(f"{STYLE_PATH}a1b1.qml")
    # C:
    c = QgsVectorLayer(uri_p, "C", "memory")
    c.setCustomProperty("skipMemoryLayersCheck", 1)
    # pr = c.dataProvider()
    # pr.addAttributes([
    #                 QgsField('id', QVariant.String)
    #                 ])
    # c.updateFields()
    QgsProject.instance().addMapLayer(c)
    c.loadNamedStyle(f"{STYLE_PATH}c.qml")
    # B_2:
    b_2 = QgsVectorLayer(uri_p, "B_2", "memory")
    b_2.setCustomProperty("skipMemoryLayersCheck", 1)
    pr = b_2.dataProvider()
    pr.addAttributes([
                    QgsField('id', QVariant.String),
                    QgsField('name', QVariant.String)
                    ])
    b_2.updateFields()
    QgsProject.instance().addMapLayer(b_2)
    b_2.loadNamedStyle(f"{STYLE_PATH}b2.qml")
    # B_1:
    b_1 = QgsVectorLayer(uri_p, "B_1", "memory")
    b_1.setCustomProperty("skipMemoryLayersCheck", 1)
    pr = b_1.dataProvider()
    pr.addAttributes([
                    QgsField('id', QVariant.String),
                    QgsField('name', QVariant.String)
                    ])
    b_1.updateFields()
    QgsProject.instance().addMapLayer(b_1)
    b_1.loadNamedStyle(f"{STYLE_PATH}b1.qml")
    # A_2:
    a_2 = QgsVectorLayer(uri_p, "A_2", "memory")
    a_2.setCustomProperty("skipMemoryLayersCheck", 1)
    pr = a_2.dataProvider()
    pr.addAttributes([
                    QgsField('id', QVariant.String),
                    QgsField('name', QVariant.String)
                    ])
    a_2.updateFields()
    QgsProject.instance().addMapLayer(a_2)
    a_2.loadNamedStyle(f"{STYLE_PATH}a2.qml")
    # A_1:
    a_1 = QgsVectorLayer(uri_p, "A_1", "memory")
    a_1.setCustomProperty("skipMemoryLayersCheck", 1)
    pr = a_1.dataProvider()
    pr.addAttributes([
                    QgsField('id', QVariant.String),
                    QgsField('name', QVariant.String)
                    ])
    a_1.updateFields()
    QgsProject.instance().addMapLayer(a_1)
    a_1.loadNamedStyle(f"{STYLE_PATH}a1.qml")

def new_project():
    """Utworzenie nowego projektu. Uruchamia się po naciśnięciu btn_new_prj."""
    global PATH_PRJ
    PATH_PRJ = file_dialog(is_folder=True)
    if os.path.isdir(PATH_PRJ):
        dlg.lab_path_content.setText(PATH_PRJ)
        try:
            os.makedirs(f"{PATH_PRJ}{os.path.sep}data")
        except FileExistsError:
            pass
        open_project(True)

def open_project(new=False):
    """Załadowanie zapisanego projektu. Uruchamia się po naciśnięciu btn_open_prj."""
    global PATH_PRJ
    btn_reset()
    if not new:
        PATH_PRJ = file_dialog(is_folder=True)
        if not os.path.isdir(PATH_PRJ):
            return
        dlg.lab_path_content.setText(PATH_PRJ)
    else:
        print(PATH_PRJ)
    check_files()
    # Próba wczytania zbioru danych A:
    f_path = f"{PATH_PRJ}{os.path.sep}adf.parq"
    f_path = f_path.replace("\\", "/")
    if os.path.isfile(f_path):
        dlg.load_adf(load_parq(f_path))
    # Próba wczytania zbioru danych B:
    idfs = idfs_load()
    if not idfs:  # Nie ma kompletu plików
        return
    f_path = f"{PATH_PRJ}{os.path.sep}bdf.parq"
    dlg.load_idf(idfs)
    dlg.load_bdf(load_parq(f_path))
    # Próba wczytania abdf:
    f_path = f"{PATH_PRJ}{os.path.sep}abdf.parq"
    if not os.path.isfile(f_path):
        dlg.abdf = pd.DataFrame(columns=['a_idx', 'b_idx', 'ab'])
        dlg.abdf['a_idx'] = dlg.abdf['a_idx'].astype('int64')
        dlg.abdf['b_idx'] = dlg.abdf['b_idx'].astype('int64')
        dlg.abdf['ab'] = dlg.abdf['ab'].astype('int64')
        dlg.abdf.to_parquet(f_path, compression='gzip')
    else:
        dlg.abdf = load_parq(f_path)
    # Próba wczytania badf:
    f_path = f"{PATH_PRJ}{os.path.sep}badf.parq"
    if not os.path.isfile(f_path):
        dlg.badf = pd.DataFrame(columns=['b_idx', 'a_idx', 'ba'])
        dlg.badf['b_idx'] = dlg.badf['b_idx'].astype('int64')
        dlg.badf['a_idx'] = dlg.badf['a_idx'].astype('int64')
        dlg.badf['ba'] = dlg.badf['ba'].astype('int64')
        dlg.badf.to_parquet(f_path, compression='gzip')
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
    check_files()

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

def btn_reset():
    """Resetuje stan przycisków importu baz."""
    # dlg.frm_import.setVisible(True)
    # dlg.frm_status.setVisible(False)
    dlg.btn_adf.setEnabled(True)
    dlg.btn_adf.setText("Importuj bazę A")
    dlg.btn_bdf.setEnabled(True)
    dlg.btn_bdf.setText("Importuj bazę B")

def check_files():
    """Ustala wartość 'gui_mode' na podstawie zawartości folderu projektu."""
    print("check_files")
    # Sprawdzenie folderu 'data':
    has_data = True if os.path.isdir(f"{PATH_PRJ}{os.path.sep}data") else False
    base_files = ["adf.parq", "bdf.parq", "hdf.parq", "rdf.parq", "zdf.parq"]
    work_files = ["abdf.parq", "badf.parq"]
    # Sprawdzenie plików bazowych:
    has_base = True
    for file_name in base_files:
        if not os.path.isfile(f"{PATH_PRJ}{os.path.sep}{file_name}"):
            has_base = False
            break
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
        print("change gui_mode to new")
    elif has_data and has_base:
        dlg.gui_mode = "automatic"
    elif not has_data and has_base and has_work:
        dlg.gui_mode = "manual"
