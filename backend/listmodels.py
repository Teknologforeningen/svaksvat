from PyQt4.QtCore import *

class ListModelCommon(QAbstractListModel):
    def __init__(self, session, parent=None):
        super().__init__(parent)
        self.data = [1, 2]

    def rowCount(self, parent=QModelIndex()):
        return len(self.data)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid() or not 0 <= index.row() < self.rowCount():
            return None

        row = index.row()

        if role == Qt.DisplayRole:
            return str(self.data[row])

        return None

