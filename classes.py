#!/usr/bin/python
import os
import pandas as pd
import numpy as np

from qgis.gui import QgsMapTool
from qgis.PyQt.QtCore import Qt, QSize, QAbstractTableModel, pyqtSignal, pyqtProperty, pyqtSlot, QVariant, QModelIndex, QObject, QRect
from qgis.PyQt.QtGui import QColor, QPen, QBrush, QPalette, QPainter, QIcon
from qgis.PyQt.QtWidgets import QHeaderView, QStyledItemDelegate, QItemDelegate, QStyle, QStyleOptionViewItem, QTableView, QToolButton

ICON_PATH = os.path.dirname(os.path.realpath(__file__)) + os.path.sep + 'ui' + os.path.sep

class CurrentThread(QObject):

    _on_execute = pyqtSignal(object, tuple, dict)

    def __init__(self):
        super(QObject, self).__init__()
        self._on_execute.connect(self._execute_in_thread)

    def execute(self, f, args, kwargs):
        self._on_execute.emit(f, args, kwargs)

    def _execute_in_thread(self, f, args, kwargs):
        f(*args, **kwargs)

main_thread = CurrentThread()

def run_in_main_thread(f):
    def result(*args, **kwargs):
        main_thread.execute(f, args, kwargs)
    return result


class ADfDelegate(QStyledItemDelegate):
    def __init__(self, parent=None, *args):
        QStyledItemDelegate.__init__(self, parent, *args)

    def paint(self, painter, option, index):
        super().paint(painter, option, index)
        selected = option.state & QStyle.State_Selected
        rect = QRect(option.rect)
        # painter.setRenderHint(QPainter.Antialiasing)
        if index.column() == 2 or index.column() == 3 or index.column() == 6:
            painter.setPen(QPen(QColor(255,255,255), 1))
            painter.drawLine(rect.topRight(), rect.bottomRight())
        elif index.column() == 4 or index.column() == 7:
            painter.setPen(QPen(QColor(0,0,0), 1))
            painter.drawLine(rect.topRight(), rect.bottomRight())
        elif index.column() == 5 or index.column() == 8:
            painter.setPen(QPen(QColor(0,0,0), 1))
            painter.drawLine(rect.topLeft(), rect.bottomLeft())
            painter.setPen(QPen(QColor(255,255,255), 1))
            painter.drawLine(rect.topRight(), rect.bottomRight())
        if selected:
            painter.setPen(QPen(QColor(255,0,0), 2))
            painter.drawLine(rect.topLeft(), rect.topRight())
            painter.drawLine(rect.bottomLeft(), rect.bottomRight())
        
    def initStyleOption(self, option, index):
        super().initStyleOption(option, index)
        selected = option.state & QStyle.State_Selected
        focused = option.state & QStyle.State_HasFocus
        # option.font.setBold(selected)
        # print(option.value())
        # override what you need to change in option
        if selected:
            option.state = option.state & ~QStyle.State_Selected
        if focused:
            option.state = option.state & ~QStyle.State_HasFocus
            # option.backgroundBrush = QColor(255,255,255,255)
        # else:

class PDfDelegate(QStyledItemDelegate):
    def __init__(self, parent=None, *args):
        QStyledItemDelegate.__init__(self, parent, *args)

    def paint(self, painter, option, index):
        super().paint(painter, option, index)
        rect = QRect(option.rect)
        if not index.siblingAtColumn(0).data() == '-':
            painter.setPen(QPen(QColor(0,0,255), 2))
            painter.drawLine(rect.topLeft(), rect.topRight())
            painter.drawLine(rect.bottomLeft(), rect.bottomRight())
        selected = option.state & QStyle.State_Selected
        rect = QRect(option.rect)
        if index.column() == 6:
            painter.setPen(QPen(QColor(255,255,255), 1))
            painter.drawLine(rect.topRight(), rect.bottomRight())
        elif index.column() == 2 or index.column() == 4 or index.column() == 7:
            painter.setPen(QPen(QColor(0,0,0), 1))
            painter.drawLine(rect.topRight(), rect.bottomRight())
        elif index.column() == 3 or index.column() == 5 or index.column() == 8:
            painter.setPen(QPen(QColor(0,0,0), 1))
            painter.drawLine(rect.topLeft(), rect.bottomLeft())
            painter.setPen(QPen(QColor(255,255,255), 1))
            painter.drawLine(rect.topRight(), rect.bottomRight())
        if selected:
            painter.setPen(QPen(QColor(255,0,0), 2))
            painter.drawLine(rect.topLeft(), rect.topRight())
            painter.drawLine(rect.bottomLeft(), rect.bottomRight())
        
    def initStyleOption(self, option, index):
        super().initStyleOption(option, index)
        selected = option.state & QStyle.State_Selected
        focused = option.state & QStyle.State_HasFocus
        # print(option)
        # option.font.setBold(selected)
        # print(option.text)
        # override what you need to change in option
        if selected:
            option.state = option.state & ~QStyle.State_Selected
        if focused:
            option.state = option.state & ~QStyle.State_HasFocus
            # option.backgroundBrush = QColor(255,255,255,255)
        # else:


class DataFrameModel(QAbstractTableModel):
    """Podstawowy model tabeli zasilany przez pandas dataframe."""
    DtypeRole = Qt.UserRole + 1000
    ValueRole = Qt.UserRole + 1001

    def __init__(self, df=pd.DataFrame(), tv=None, col_names=[], parent=None):
        super(DataFrameModel, self).__init__(parent)
        self._dataframe = df
        self.col_names = col_names
        self.tv = tv  # Referencja do tableview
        self.tv.setModel(self)
        self.tv.selectionModel().selectionChanged.connect(lambda: self.layoutChanged.emit())
        self.tv.horizontalHeader().setSortIndicatorShown(False)
        self.sort_col = -1
        self.sort_ord = 1
        

    def col_names(self, df, col_names):
        """Nadanie nazw kolumn tableview'u."""
        df.columns = col_names
        return df

    def sort_reset(self):
        """Wyłącza sortowanie po kolumnie."""
        self.sort_col = -1
        self.sort_ord = 1

    def setDataFrame(self, dataframe):
        self.beginResetModel()
        self._dataframe = dataframe.copy()
        self.endResetModel()

    def dataFrame(self):
        return self._dataframe

    dataFrame = pyqtProperty(pd.DataFrame, fget=dataFrame, fset=setDataFrame)

    @pyqtSlot(int, Qt.Orientation, result=str)
    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.DisplayRole):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                if self.col_names:
                    try:
                        return self.col_names[section]  # type: ignore
                    except:
                        pass
                return self._dataframe.columns[section]
            else:
                return str(self._dataframe.index[section])
        return QVariant()
        # if role == Qt.DecorationRole and orientation == Qt.Horizontal:
        #     self.tv.setSortIndicatorShown(False)

    def rowCount(self, parent=QModelIndex()):
        if parent.isValid():
            return 0
        return len(self._dataframe.index)

    def columnCount(self, parent=QModelIndex()):
        if parent.isValid():
            return 0
        return self._dataframe.columns.size

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid() or not (0 <= index.row() < self.rowCount() \
            and 0 <= index.column() < self.columnCount()):
            return QVariant()
        row = self._dataframe.index[index.row()]
        col = self._dataframe.columns[index.column()]
        dt = self._dataframe[col].dtype
        try:
            val = self._dataframe.iloc[row][col]
        except:
            return QVariant()
        # if role == Qt.DisplayRole:
        # #     # Get the raw value
        # #     if isinstance(val, float) and (index.column() == 2 or index.column() == 3):
        # #         return "%.2f" % val
        # #     if isinstance(val, float) and (index.column() == 4 or index.column() == 5):
        # #         return "%.1f" % val
        # #     if isinstance(val, float) & index.column() == 6:
        # #         return "%.0f" % val
        #     return str(val)
        if role == DataFrameModel.ValueRole:
            return val
        if role == DataFrameModel.DtypeRole:
            return dt
        return QVariant()

    def roleNames(self):
        roles = {
            Qt.DisplayRole: b'display',
            DataFrameModel.DtypeRole: b'dtype',
            DataFrameModel.ValueRole: b'value'
        }
        return roles

class ADfModel(DataFrameModel):
    """Subklasa dataframemodel dla tableview wyświetlającą adf."""

    COLORS = ['#f8696b', '#f98370', '#fb9d75', '#fcb77a', '#fed17f', '#ffeb84', '#e0e282', '#c1d980', '#a1d07f', '#82c77d', '#63be7b']

    def __init__(self, df=pd.DataFrame(), tv=None, col_widths=[], col_names=[], parent=None):
        super().__init__(df, tv, col_names)
        self.tv = tv  # Referencja do tableview
        de = ADfDelegate()
        self.tv.setItemDelegate(de)
        self.col_format(col_widths)

    def col_format(self, col_widths):
        """Formatowanie szerokości kolumn tableview'u."""
        cols = list(enumerate(col_widths, 0))
        for col in cols:
            self.tv.setColumnWidth(col[0], col[1])
        header = self.tv.horizontalHeader()
        header.setMinimumSectionSize(15)
        header.setDefaultSectionSize(30)
        header.setSectionResizeMode(QHeaderView.Fixed)
        header.setSectionResizeMode(0, QHeaderView.Interactive)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.resizeSection(0, 60)
        header.resizeSection(2, 15)

    def data(self, index, role=Qt.DisplayRole):
        # super().data(index, role=Qt.DisplayRole)
        if not index.isValid() or not (0 <= index.row() < self.rowCount() \
            and 0 <= index.column() < self.columnCount()):
            return QVariant()
        row = self._dataframe.index[index.row()]
        col = self._dataframe.columns[index.column()]
        dt = self._dataframe[col].dtype
        try:
            val = self._dataframe.iloc[row][col]
        except:
            return QVariant()
        if role == Qt.TextAlignmentRole:
            return Qt.AlignVCenter + Qt.AlignHCenter
        elif role == Qt.DisplayRole:
            if pd.isnull(val) or val != val:
                return '-'
            if index.column() == 2:
                return str(val)
            if isinstance(val, (float, np.float32)) and index.column() >= 3:
                return "%.2f" % val
            return str(val)
        elif role == Qt.BackgroundRole:
            if index.column() == 0 or index.column() == 1:
                return QVariant()
            elif index.column() == 2:
                return QColor('#404040')
            elif (isinstance(val, float) or isinstance(val, np.float32)) and index.column() >= 3:
                if not pd.isnull(val) or not val:
                    mod_val = int(round(val * 10, 0))
                    return QColor(ADfModel.COLORS[mod_val])
                else:
                    return QVariant()
        elif role == Qt.ForegroundRole:
            if index.column() == 2:
                return QColor('#ffffff')
        elif role == DataFrameModel.ValueRole:
            return val
        if role == DataFrameModel.DtypeRole:
            return dt
        return QVariant()

    def setDataFrame(self, dataframe):
        sel_tv = self.tv.selectionModel()
        if sel_tv.hasSelection():
            is_sel = True
            index = sel_tv.currentIndex()
            row_cnt = self.rowCount() - 1
            if index.row() == row_cnt:  # Zaznaczony jest ostatni wiersz
                last_row = (index.row() - 1)
                index = self.index(last_row, 0)
        else:
            is_sel = False
        self.beginResetModel()
        self._dataframe = dataframe.copy()
        if self.sort_col >= 0:  # Sortowanie włączone
            self._dataframe = self._dataframe.sort_values(by=self._dataframe.columns[self.sort_col], ascending= not self.sort_ord).reset_index(drop=True)
        self.endResetModel()
        if is_sel:
            self.tv.setCurrentIndex(index)

    def sort(self, col, order):
        try:
            self.layoutAboutToBeChanged.emit()
            self.tv.selectionModel().clearSelection()
            self.tv.setCurrentIndex(QModelIndex())
            self._dataframe = self._dataframe.sort_values(by=self._dataframe.columns[col], ascending= not order).reset_index(drop=True)
            self.sort_col = col
            self.sort_ord = order
            self.layoutChanged.emit()
        except Exception as e:
            print(e)

class PDfModel(DataFrameModel):
    """Subklasa dataframemodel dla tableview wyświetlającą adf."""

    def __init__(self, df=pd.DataFrame(), tv=None, col_widths=[], col_names=[], parent=None):
        super().__init__(df, tv, col_names)
        self.tv = tv  # Referencja do tableview
        de = PDfDelegate()
        self.tv.setItemDelegate(de)
        self.col_format(col_widths)

    def col_format(self, col_widths):
        """Formatowanie szerokości kolumn tableview'u."""
        cols = list(enumerate(col_widths, 0))
        for col in cols:
            self.tv.setColumnWidth(col[0], col[1])
        header = self.tv.horizontalHeader()
        header.setMinimumSectionSize(1)
        header.setDefaultSectionSize(30)
        header.setSectionResizeMode(QHeaderView.Fixed)
        header.setSectionResizeMode(1, QHeaderView.Interactive)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.resizeSection(0, 1)
        header.resizeSection(1, 60)
        header.resizeSection(10, 1)

    def data(self, index, role=Qt.DisplayRole):
        # super().data(index, role=Qt.DisplayRole)
        if not index.isValid() or not (0 <= index.row() < self.rowCount() \
            and 0 <= index.column() < self.columnCount()):
            return QVariant()
        row = self._dataframe.index[index.row()]
        col = self._dataframe.columns[index.column()]
        dt = self._dataframe[col].dtype
        try:
            val = self._dataframe.iloc[row][col]
        except:
            return QVariant()
        if role == Qt.TextAlignmentRole:
            return Qt.AlignVCenter + Qt.AlignHCenter
        elif role == Qt.DisplayRole:
            if pd.isnull(val) or val != val:
                return '-'
            # if index.column() == 3:
            #     return str(val.astype(int))
            if isinstance(val, (float, np.float32)) and (index.column() >= 3 and index.column() < 10):
                return "%.2f" % val
            return str(val)
        elif role == Qt.BackgroundRole:
            adata = index.siblingAtColumn(0).data()
            # idata = index.siblingAtColumn(11).data()
            if index.column() < 3 and adata != '-':
                return QColor('#c0c0ff')
            # elif index.column() == 3:
            #     return QColor('#404040')
            elif (isinstance(val, float) or isinstance(val, np.float32)) and (index.column() >= 3 and index.column() < 11):
                if not pd.isnull(val):
                    mod_val = int(round(val * 10, 0))
                    return QColor(ADfModel.COLORS[mod_val])
        elif role == Qt.ForegroundRole:
            adata = index.siblingAtColumn(0).data()
            idata = index.siblingAtColumn(10).data()
            # if index.column() == 3:
            #     return QColor('#ffffff')
            # else:
            if adata != idata or adata != idata:
                return QColor('#808080')
        elif role == DataFrameModel.ValueRole:
            return val
        elif role == DataFrameModel.DtypeRole:
            return dt
        return QVariant()


class IDfModel(DataFrameModel):
    """Subklasa dataframemodel dla tableview wyświetlającą adf."""

    def __init__(self, df=pd.DataFrame(), tv=None, col_widths=[], col_names=[], parent=None):
        super().__init__(df, tv, col_names)
        self.tv = tv  # Referencja do tableview
        self.col_format(col_widths)

    def col_format(self, col_widths):
        """Formatowanie szerokości kolumn tableview'u."""
        cols = list(enumerate(col_widths, 0))
        for col in cols:
            self.tv.setColumnWidth(col[0], col[1])
        self.tv.horizontalHeader().setMinimumSectionSize(1)

    def data(self, index, role=Qt.DisplayRole):
        # if role == Qt.BackgroundRole and index.column() == 2:
        #     return QColor('blue')
        if not index.isValid() or not (0 <= index.row() < self.rowCount() \
            and 0 <= index.column() < self.columnCount()):
            return QVariant()
        row = self._dataframe.index[index.row()]
        col = self._dataframe.columns[index.column()]
        dt = self._dataframe[col].dtype
        val = self._dataframe.iloc[row][col]
        if role == Qt.DisplayRole:
            # Get the raw value
            if isinstance(val, float) and (index.column() == 2 or index.column() == 3):
                return "%.2f" % val
            if isinstance(val, float) and (index.column() == 4 or index.column() == 5):
                return "%.1f" % val
            if isinstance(val, float) & index.column() == 6:
                return "%.0f" % val
            return str(val)
        elif role == DataFrameModel.ValueRole:
            return val
        if role == DataFrameModel.DtypeRole:
            return dt
        return QVariant()

class CustomButton(QToolButton):
    """Fabryka guzików."""
    def __init__(self, *args, size=25, hsize=0, name="", icon="", visible=True, enabled=True, checkable=False, tooltip=""):
        super().__init__(*args)
        name = icon if len(icon) > 0 else name
        self.shown = visible  # Dubluje setVisible() - .isVisible() może zależeć od rodzica
        self.setVisible(visible)
        self.setEnabled(enabled)
        self.setCheckable(checkable)
        self.setToolTip(tooltip)
        self.setToolButtonStyle(Qt.ToolButtonIconOnly)
        self.setAutoRaise(True)
        self.setStyleSheet("QToolButton {border: none}")
        self.set_icon(name, size, hsize)
        self.setMouseTracking(True)

    def set_icon(self, name, size=25, hsize=0):
        """Ładowanie ikon do guzika."""
        if hsize == 0:
            wsize, hsize = size, size
        else:
            wsize = size
        self.setFixedSize(wsize, hsize)
        self.setIconSize(QSize(wsize, hsize))
        icon = QIcon()
        icon.addFile(ICON_PATH + name + "_0.png", size=QSize(wsize, hsize), mode=QIcon.Normal, state=QIcon.Off)
        icon.addFile(ICON_PATH + name + "_0_act.png", size=QSize(wsize, hsize), mode=QIcon.Active, state=QIcon.Off)
        icon.addFile(ICON_PATH + name + "_0.png", size=QSize(wsize, hsize), mode=QIcon.Selected, state=QIcon.Off)
        icon.addFile(ICON_PATH + name + "_dis.png", size=QSize(wsize, hsize), mode=QIcon.Disabled, state=QIcon.Off)
        if self.isCheckable():
            icon.addFile(ICON_PATH + name + "_1.png", size=QSize(wsize, hsize), mode=QIcon.Normal, state=QIcon.On)
            icon.addFile(ICON_PATH + name + "_1_act.png", size=QSize(wsize, hsize), mode=QIcon.Active, state=QIcon.On)
            icon.addFile(ICON_PATH + name + "_1.png", size=QSize(wsize, hsize), mode=QIcon.Selected, state=QIcon.On)
        self.setIcon(icon)


class AddCLoc(QgsMapTool):
    """Maptool do pobierania współrzędnych lokalizacji C."""
    c_added = pyqtSignal(object)

    def __init__(self, dlg, canvas):
        self.dlg = dlg
        self.canvas = canvas
        QgsMapTool.__init__(self, canvas)
        self.setCursor(Qt.CrossCursor)
 
    def canvasReleaseEvent(self, event):
        point = self.toMapCoordinates(event.pos())
        self.c_added.emit(point)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.dlg.localizing = False
