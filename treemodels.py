from PyQt4 import QtCore, QtGui
from backend.orm import (Group, Post, Department, Membership)

class TreeNode(object):
    def __init__(self, item, parent_item):
        self.item = item
        self.parent_item = parent_item
        self.child_items = []

    def appendChild(self, item):
        self.child_items.append(item)

    def child(self, row):
        return self.child_items[row]

    def childCount(self):
        return len(self.child_items)

    def columnCount(self):
        return 1

    def data(self, column):
        if hasattr(self.item, 'name_fld'):
            return self.item.name_fld

        elif hasattr(self.item, 'member'):
            return self.item.member.getWholeName()

        else:
            return self.item
        return ''

    def parent(self):
        return self.parent_item

    def row(self):
        if self.parent_item:
            return self.parent_item.child_items.index(self)
        return 0


class MembershipTreeModel(QtCore.QAbstractItemModel):
    def __init__(self, session, parent=None):
        super(MembershipTreeModel, self).__init__(parent)
        self.membershiptypes = ["Group", "Post", "Department", "Membership"]
        self.rootItem = TreeNode("ALL", None)
        self.parents = {0: self.rootItem}
        self.session = session
        self.setupModelData(self.session)

    def columnCount(self, parent=None):
        return 1

    def data(self, index, role):
        if not index.isValid():
            return None

        item = index.internalPointer()
        if role == QtCore.Qt.DisplayRole:
            return item.data(index.column())
        if role == QtCore.Qt.UserRole:
            if item:
                return item.data

        return None

    def headerData(self, column, orientation, role):
        return ''

    def index(self, row, column, parent):
        if not self.hasIndex(row, column, parent):
            return QtCore.QModelIndex()

        if not parent.isValid():
            parentItem = self.rootItem
        else:
            parentItem = parent.internalPointer()

        childItem = parentItem.child(row)
        if childItem:
            return self.createIndex(row, column, childItem)
        else:
            return QtCore.QModelIndex()

    def parent(self, index):
        if not index.isValid():
            return QtCore.QModelIndex()

        childItem = index.internalPointer()
        if not childItem:
            return QtCore.QModelIndex()

        parentItem = childItem.parent()

        if parentItem == self.rootItem:
            return QtCore.QModelIndex()

        return self.createIndex(parentItem.row(), 0, parentItem)

    def rowCount(self, parent=QtCore.QModelIndex()):
        if parent.column() > 0:
            return 0
        if not parent.isValid():
            p_item = self.rootItem
        else:
            p_item = parent.internalPointer()
        return p_item.childCount()

    def setupModelData(self, session):
        for membershiptype in self.membershiptypes:
            newparent = TreeNode(membershiptype, self.rootItem)
            self.rootItem.appendChild(newparent)
            for item in session.query(eval(membershiptype)).all():
                newchild = TreeNode(item, newparent)
                newparent.appendChild(newchild)
                for currentmship in item.getCurrentMemberships():
                    newsubchild = TreeNode(currentmship, newchild)
                    newchild.appendChild(newsubchild)


#TODO: columns with convenient information like how many members or mandate time. checkbox for filtering out only current memberships 
app = QtGui.QApplication([])

import passwordsafe
from sqlalchemy.orm import scoped_session
ps = passwordsafe.PasswordSafe(enablegui=True)
SessionMaker = scoped_session(ps.connect_with_config("memberslocalhost"))

model = MembershipTreeModel(SessionMaker)
dialog = QtGui.QDialog()

layout = QtGui.QVBoxLayout(dialog)

tv = QtGui.QTreeView(dialog)
tv.setModel(model)
tv.setAlternatingRowColors(True)
layout.addWidget(tv)

dialog.exec_()

app.closeAllWindows()
