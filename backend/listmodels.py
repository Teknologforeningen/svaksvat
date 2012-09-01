import datetime

from PyQt4.QtCore import *

class MembershipListModel(QAbstractListModel):
    def __init__(self, session, member, parent=None):
        super().__init__(parent)
        self.member = session.merge(member) # Get local object for this Model
        self.data = self.member.groupmemberships

    def rowCount(self, parent=QModelIndex()):
        return len(self.data)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid() or not 0 <= index.row() < self.rowCount():
            return None

        row = index.row()

        if role == Qt.DisplayRole:
            membership = self.data[row]
            duration = self.membershipDuration(membership)
            return "%s %s" % (membership.group.name_fld,
            duration)

        return None

    def membershipDuration(self, membership):
        startyear = membership.startTime_fld.year
        endyear = membership.endTime_fld.year
        if startyear == endyear:
            return startyear
        startmonth = membership.startTime_fld.month
        endmonth = membership.endTime_fld.month
        return "%d.%d - %d.%d" % (startmonth, startyear, endmonth, endyear)


