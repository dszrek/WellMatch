#!/usr/bin/python

from qgis.gui import QgsMapToolIdentify, QgsMapTool, QgsRubberBand
from qgis.core import QgsWkbTypes, QgsPointXY, QgsFeatureRequest, QgsRectangle, QgsPointLocator, QgsSettings
from qgis.PyQt.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor
from qgis.utils import iface

from .classes import threading_func

class MapToolManager:
    """Menedżer maptool'ów."""
    def __init__(self, dlg, canvas):
        self.maptool = None  # Instancja klasy maptool'a
        self.mt_name = None  # Nazwa maptool'a
        self.params = {}  # Słownik z parametrami maptool'a
        self.dlg = dlg  # Referencja do wtyczki
        self.canvas = canvas  # Referencja do mapy
        self.old_button = None
        self.canvas.mapToolSet.connect(self.maptool_change)
        self.tool_kinds = (PointPickerMapTool, PointDrawMapTool)
        self.maptools = [
            {"name" : "c_loc_add", "class" : PointDrawMapTool, "button" : self.dlg.btn_c_add, "fn" : self.dlg.loc_c_add},
            {"name" : "b_pick", "class" : PointPickerMapTool, "button" : self.dlg.btn_b_sel, "lyr" : ["B_INNE"], "fn" : self.dlg.b_pick, "extra" : [["B_INNE"]]}
        ]

    def maptool_change(self, new_tool, old_tool):
        if not new_tool and not old_tool:
            # Jeśli wyłączany jest maptool o klasie QgsMapToolIdentify,
            # event jest puszczany dwukrotnie (pierwszy raz z wartościami None, None)
            return
        if type(old_tool).__name__ == 'QObject':
            # Workaround dla QGIS > 3.10:
            # event jest puszczany dwukrotnie przy włączaniu MOEK maptool'a
            return
        if not isinstance(new_tool, (self.tool_kinds)) and self.mt_name:
            # Reset ustawień MapToolManager'a, jeśli został wybrany maptool spoza wtyczki
            self.maptool = None
            self.mt_name = None
            self.params = {}
        if self.old_button:
            try:
                self.old_button.setChecked(False)
            except:
                pass
        try:  # Maptool może nie mieć atrybutu '.button()'
            self.old_button = new_tool.button()
        except:
            self.old_button = None

    def init(self, maptool, extra=None):
        """Zainicjowanie zmiany maptool'a."""
        if not self.mt_name:  # Nie ma obecnie uruchomionego maptool'a
            self.tool_on(maptool, extra)  # Włączenie maptool'a
        else:
            mt_old = self.mt_name
            if mt_old != maptool:  # Inny maptool był włączony
                self.tool_on(maptool, extra)  # Włączenie nowego maptool'a
            else:
                iface.actionPan().trigger()

    def tool_on(self, maptool, extra=None):
        """Włączenie maptool'a."""
        self.params = self.dict_name(maptool)  # Wczytanie parametrów maptool'a
        if "lyr" in self.params:
            lyr = self.lyr_ref(self.params["lyr"])
        if self.params["class"] == PointPickerMapTool:
            self.maptool = self.params["class"](self.dlg, self.canvas, lyr, self.params["button"], self.params["extra"][0])
            self.maptool.picked.connect(self.params["fn"])
        elif self.params["class"] == PointDrawMapTool:
            self.maptool = self.params["class"](self.canvas, self.params["button"])
            self.maptool.drawn.connect(self.params["fn"])
        self.canvas.setMapTool(self.maptool)
        self.mt_name = self.params["name"]

    def dict_name(self, maptool):
        """Wyszukuje na liście wybrany toolmap na podstawie nazwy i zwraca słownik z jego parametrami."""
        for tool in self.maptools:
            if tool["name"] == maptool:
                return tool

    def lyr_ref(self, lyr):
        """Zwraca referencje warstw na podstawie ich nazw."""
        layer = []
        for l in lyr:
            layer.append(self.dlg.proj.mapLayersByName(l)[0])
        return layer


class PointDrawMapTool(QgsMapTool):
    """Maptool do rysowania obiektów punktowych."""
    drawn = pyqtSignal(object)

    def __init__(self, canvas, button):
        QgsMapTool.__init__(self, canvas)
        self.canvas = canvas
        self._button = button
        if not self._button.isChecked():
            self._button.setChecked(True)
        self.setCursor(Qt.CrossCursor)

    def button(self):
        return self._button

    def canvasReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            point = self.toMapCoordinates(event.pos())
            self.drawn.emit(point)
        else:
            self.drawn.emit(None)

    def keyReleaseEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.drawn.emit(None)


class PointPickerMapTool(QgsMapToolIdentify):
    """Maptool do wspomaganego wybierania obiektu z wybranej warstwy."""
    picked = pyqtSignal(object, object)
    cursor_changed = pyqtSignal(str)

    def __init__(self, dlg, canvas, layer, button, extra):
        QgsMapToolIdentify.__init__(self, canvas)
        self.dlg = dlg
        self.canvas = canvas
        self._button = button
        if not self._button.isChecked():
            self._button.setChecked(True)
        self.dragging = False
        self.accepted = False
        self.canceled = False
        self.deactivated = False
        self.lyrs = layer
        self.lyr_names = extra
        self.temp_point = None
        self.cursor_changed.connect(self.cursor_change)
        self.cursor = "open_hand"
        self.marker = None
        self.snap_settings()
        self.rbs_create()

    def button(self):
        return self._button

    def __setattr__(self, attr, val):
        """Przechwycenie zmiany atrybutu."""
        super().__setattr__(attr, val)
        if attr == "cursor":
            self.cursor_changed.emit(val)

    def cursor_change(self, cur_name):
        """Zmiana cursora maptool'a."""
        cursors = [
                    ["arrow", Qt.ArrowCursor],
                    ["open_hand", Qt.OpenHandCursor],
                    ["closed_hand", Qt.ClosedHandCursor]
                ]
        for cursor in cursors:
            if cursor[0] == cur_name:
                self.setCursor(cursor[1])
                break

    def snap_settings(self):
        """Zmienia globalne ustawienia snappingu."""
        s = QgsSettings()
        s.setValue('/qgis/digitizing/default_snap_type', 'VertexAndSegment')
        s.setValue('/qgis/digitizing/search_radius_vertex_edit', 12)
        s.setValue('/qgis/digitizing/search_radius_vertex_edit_unit', 'Pixels')

    def rbs_create(self):
        """Stworzenie rubberband'ów."""
        self.marker = QgsRubberBand(self.canvas, QgsWkbTypes.PointGeometry)
        self.marker.setIcon(QgsRubberBand.ICON_CIRCLE)
        self.marker.setColor(QColor(255, 255, 255, 255))
        self.marker.setFillColor(QColor(0, 0, 0, 32))
        self.marker.setIconSize(30)
        self.marker.addPoint(QgsPointXY(0, 0), False)
        self.marker.setVisible(False)

    def snap_to_layer(self, event, layer):
        """Zwraca wyniki przyciągania do wierzchołków i krawędzi."""
        self.canvas.snappingUtils().setCurrentLayer(layer)
        v = self.canvas.snappingUtils().snapToCurrentLayer(event.pos(), QgsPointLocator.Vertex)
        return v

    @threading_func
    def find_nearest_feature(self, pos):
        """Zwraca najbliższy od kursora obiekt na wybranych warstwach."""
        pos = self.toLayerCoordinates(self.lyrs[0], pos)
        scale = iface.mapCanvas().scale()
        tolerance = scale / 250
        search_rect = QgsRectangle(pos.x() - tolerance,
                                  pos.y() - tolerance,
                                  pos.x() + tolerance,
                                  pos.y() + tolerance)
        request = QgsFeatureRequest()
        request.setFilterRect(search_rect)
        request.setFlags(QgsFeatureRequest.ExactIntersect)
        lyrs = self.get_lyrs()
        if self.lyr_names:
            for lyr in lyrs:
                for feat in lyr.getFeatures(request):
                    return lyr
        else:
            return None

    def get_lyrs(self):
        """Zwraca listę włączonych warstw z obiektami."""
        lyrs = []
        for _list in self.dlg.lyr.lyr_vis:
            if _list[1] and _list[0] in self.lyr_names:
                lyr = self.dlg.proj.mapLayersByName(_list[0])[0]
                lyrs.append(lyr)
        return lyrs

    def canvasMoveEvent(self, event):
        map_point = self.toMapCoordinates(event.pos())
        if event.buttons() == Qt.LeftButton:
            self.dragging = True
            self.cursor = "closed_hand"
            self.canvas.panAction(event)
        if event.buttons() == Qt.NoButton:
            th = self.find_nearest_feature(event.pos())
            result = th.get()
            snap_type = None
            if result:
                v = self.snap_to_layer(event, result)
                snap_type = v.type()
                if snap_type == 1:  # Kursor nad vertexem
                    if self.cursor != "arrow":
                        self.cursor = "arrow"
                    self.marker.movePoint(v.point(), 0)
                    self.temp_point = v.point()
                    self.marker.setVisible(True)
                else:  # Kursor poza otworami
                    if self.cursor != "open_hand":
                        self.cursor = "open_hand"
                    self.marker.setVisible(False)
                    self.temp_point = map_point
            else:
                if self.cursor != "open_hand":
                    self.cursor = "open_hand"
                self.marker.setVisible(False)
                self.temp_point = map_point

    def canvasReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self.dragging:  # Zakończenie panningu mapy
                self.cursor = "open_hand"
                self.canvas.panActionEnd(event.pos())
                self.dragging = False
                return
            self.accepted = True
            result = self.identify(event.x(), event.y(), self.TopDownStopAtFirst, self.lyrs, self.VectorLayer)
            self.accept_changes(result)
        elif event.button() == Qt.RightButton:
            self.canceled = True
            self.accept_changes(cancel=True)

    def keyReleaseEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.canceled = True
            self.accept_changes(cancel=True)

    def accept_changes(self, result=None, cancel=False, deactivated=False):
        """Zakończenie wybierania obiektu punktowego."""
        if not cancel and not deactivated:
            if len(result) > 0:
                self.picked.emit(result[0].mLayer, result[0].mFeature)
            else:
                self.picked.emit(None, None)
        elif cancel and not deactivated:
            self.picked.emit(None, None)
        if self.marker:
            self.canvas.scene().removeItem(self.marker)
            self.marker = None

    def deactivate(self):
        """Zakończenie działania maptool'a."""
        super().deactivate()
        if not self.canceled and not self.accepted:
            self.accept_changes(deactivated=True)
