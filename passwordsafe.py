"""Password Safe

Implements an OS independent password storage.
"""

# imports
import sys
import getpass
import configparser
import re
import time
import socket
import _thread as thread

from PyQt4 import QtGui
import sqlalchemy

import keyring

from backend import connect, sshwrapper
# constants
# exception classes

class CredentialDialogReject(Exception):
    def __str__(self):
        return "CredentialDialog rejected by user"

class UnsuccesfulPortforward(Exception):
    def __str__(self):
        return "Portforwarding unsuccesful."

# interface functions
# classes

class CredentialDialog(QtGui.QDialog):
    """Asks for credentials."""
    def __init__(self, context="", askpassword=True):
        """Creates a dialog that asks for username and optionally password."""
        super(CredentialDialog, self).__init__()

        self.askpassword = askpassword
        self.initUI(context)

    def initUI(self, context):
        """Creates the UI widgets.

        context -- String to set as windowtitle.

        """
        self.formlayout = QtGui.QFormLayout(self)

        self.username_le = QtGui.QLineEdit(self)
        self.username_le.returnPressed.connect(self.accept)

        if self.askpassword:
            self.formlayout.addRow("Användarnamn:", self.username_le)
            self.password_le = QtGui.QLineEdit(self)
            self.password_le.setEchoMode(QtGui.QLineEdit.Password)
            self.password_le.returnPressed.connect(self.accept)
            self.formlayout.addRow("Lösenord:", self.password_le)
        else:
            self.formlayout.addRow(context, self.username_le)

        self.okbutton = QtGui.QPushButton('OK', self)
        self.okbutton.clicked.connect(self.accept)

        self.cancelbutton = QtGui.QPushButton('Avbryt', self)
        self.cancelbutton.clicked.connect(self.reject)

        self.buttonrow = QtGui.QHBoxLayout()
        self.buttonrow.addWidget(self.okbutton)
        self.buttonrow.addWidget(self.cancelbutton)
        self.formlayout.addRow("", self.buttonrow)

        self.setWindowTitle(context)

        self.show()

    def getCredentials(self):
        """Returns the asked credentials or raises CredentialDialogReject."""
        if self.result(): # Accepted?
            username = self.username_le.text()
            password = ""
            if self.askpassword:
                password = self.password_le.text()

            return username, password

        raise CredentialDialogReject()


class PasswordSafe:
    def __init__(self, configfile="svaksvat.cfg", enablegui=False):
        self.configfile = configfile
        self.configparser = configparser.ConfigParser()
        self.configparser.read(configfile)

        self.inputfunc = input
        self.askcredentialsfunc = self.askcredentialsCLI
        if enablegui or not sys.stdin.isatty():
            self.askcredentialsfunc = self.askcredentialsQt
            self.inputfunc = self.inputfuncGUI

    def get_passid(self, service, usernameparameter):
        """Returns identifier for the password."""
        return service + ":" + usernameparameter

    def get_password(self, service, usernameparameter, username):
        return keyring.get_password(
            self.get_passid(service, usernameparameter),
            username)

    def set_password(self, service, usernameparameter, username, password):
        keyring.set_password(self.get_passid(service, usernameparameter),
                             username, password)

    def get_config_value(self, section, parameter):
        try:
            value = self.configparser.get(section, parameter)

        except configparser.NoOptionError:
            value = self.inputfunc("%s %s: " % (section, parameter))

        return value

    def askcredentials(self, authfunction, section, usernameparameter):
        if not self.configparser.has_section(section):
            self.configparser.add_section(section)
            self.configparser.set(section, usernameparameter, "")

        username = self.configparser.get(section, usernameparameter)
        password = None
        if username != '':
            password = self.get_password(section,
                                         usernameparameter,
                                         username)

        authreturn = None
        passwordchanged = False

        try:
            while True:
                authreturn = authfunction(username, password)
                if authreturn:
                    break
                passwordchanged = True
                username, password = self.askcredentialsfunc(section + " " +
                                                             usernameparameter)

        except Exception as e:
                print(e)
                return None, None, None

        if passwordchanged:
            self.store_credentials(self.configfile, section, usernameparameter,
                                   username, password)

        return authreturn, username, password

    def store_credentials(self, configfile, section,
                          usernameparameter, username, password):
        # store the username
        self.configparser.set(section, usernameparameter, username)
        self.configparser.write(open(configfile, 'w'))
        try:
            self.set_password(section, usernameparameter, username, password)
            print("Lösenordet sparat")
        except keyring.backend.PasswordSetError:
            print("Det gick inte att spara lösenordet")

    def askcredentialsQt(self, context=""):
        return self.inputfuncGUI(context, askpassword=True)

    def inputfuncGUI(self, context="", askpassword=False):
        app = None
        if not QtGui.QApplication.topLevelWidgets(): # If no QApplication
            app = QtGui.QApplication(sys.argv)

        cd = CredentialDialog(context, askpassword)

        if app:
            app.exec_()
        else:
            cd.exec_()

        username, password = cd.getCredentials()

        if askpassword:
            return username, password
        return username

    def askcredentialsCLI(self, context=""):
        print(context)
        username = input("Användarnamn:")
        password = getpass.getpass("Lösenord:")
        return username, password

    def connect_with_config(self, configsection):
        usernameparameter = "dbusername"
        host = self.configparser.get(configsection, "host")
        port = int(self.configparser.get(configsection, "port"))
        database = self.configparser.get(configsection, "database")
        dbtype = self.configparser.get(configsection, "dbtype")
        dbusername = self.configparser.get(configsection, usernameparameter)
        dbpassword = self.get_password(configsection, usernameparameter,
                dbusername) or "" # Can be None which doesn't store.
        create_metadata = bool(self.configparser.get(configsection, "create_metadata"))

        sshconnecting = False
        threadfinishedmutex = thread.allocate_lock()
        while True:
            try:
                SessionMaker = connect.connect(dbusername,
                                               dbpassword, host+":"+str(port),
                        database, dbtype, create_metadata)

                self.store_credentials(self.configfile, configsection,
                        usernameparameter, dbusername, dbpassword)

                return SessionMaker

            except sqlalchemy.exc.OperationalError as e:
                if re.match(
                    "(.*role .* does not exist.*)|" +
                    "(.*password authentication failed for user.*)|" +
                    "(.*no password supplied.*)", repr(e)):
                    dbusername, dbpassword = self.askcredentialsfunc(
                           "Fel inloggningsinformation för databasen!")

                elif re.match(".*no pg_hba.conf entry for host.*", repr(e)):
                    # Test if port is open
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    try:
                        s.connect(("localhost", int(port)))
                        s.shutdown(2)
                        print("Nätverksporten är redan öppen. Testar om" +
                                " portforwarding är redan igång...")

                    except: # Port not open. Commence SSH port forwarding.
                        print("Du måste logga in på servern.")

                        authfunc = lambda user, passwd: sshwrapper.connect_ssh(
                            host, user, passwd)
                        sshport = int(self.configparser.get(
                            configsection, "sshport"))
                        if (sshport):
                            print("Using ssh port:", sshport)
                            authfunc = lambda user, passwd: (
                                sshwrapper.connect_ssh(
                                    host, user, passwd, sshport))

                        client = self.askcredentials(
                            authfunc, configsection, "sshusername")[0]
                        thread.start_new_thread(
                            lambda: sshwrapper.portforward(
                                client,
                                threadfinishedmutex,
                                'localhost',
                                port,
                                port), ())

                    sshconnecting = True
                    host = "localhost"

                elif re.match(".*could not connect to server: Connection refused.*",
                              repr(e)) and sshconnecting:
                    time.sleep(1)
                    if threadfinishedmutex.locked(): # SSH-thread exited
                        threadfinishedmutex.release()
                        raise UnsuccesfulPortforward()

                else:
                    raise(e)


# internal functions & classes
def testauth(username, password):
    return username == password


def testfunction():
    import tempfile
    tempfilehandle, tempfilename = tempfile.mkstemp(suffix=".cfg")
    ps = PasswordSafe(configfile=tempfilename)
    testservice = "PasswordSafePasswordIdentifier"
    testuserparameter = "PasswordSafePasswordIdentifierUserParameter"
    testuser = "PasswordSafePasswordIdentifierUser"
    ps.set_password(testservice, testuserparameter, testuser, "")
    if ps.get_password(testservice, testuserparameter, testuser):
        return False

    testpass = "!#?R¤?FI?AF"
    ps.set_password(testservice, testuserparameter, testuser, testpass)
    if ps.get_password(testservice, testuserparameter, testuser) != testpass:
        return False

    ps.askcredentials(testauth, "testsection",
    "testusername")

    return True


def main():
    #ps = PasswordSafe(enablegui=True)
    #ps.connect_with_config("memberslocalhost")

    if testfunction():
        return 0
    return 1

if __name__ == '__main__':
    #print( QtGui.QInputDialog.getText(None, "",""))

    app = QtGui.QApplication(sys.argv)
    #pd = CredentialDialog("Hello")
    #ps = PasswordSafe(enablegui=True)
    #print(ps.inputfuncGUI("Hello"))
    #print(pd.getCredentials())
    status = main()
    sys.exit(status)
