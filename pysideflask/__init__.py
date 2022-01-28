import sys
from PySide2 import QtCore, QtWidgets, QtGui, QtWebEngineWidgets
import socket


class ApplicationThread(QtCore.QThread):
    download_requested = QtCore.Signal(QtWebEngineWidgets.QWebEngineDownloadItem)
    def __init__(self, application, port=5000):
        super(ApplicationThread, self).__init__()
        self.application = application
        self.port = port

    def __del__(self):
        self.wait()

    def run(self):
        self.application.run(
            port=self.port, 
            threaded=True
            )

class WebPage(QtWebEngineWidgets.QWebEnginePage):
    download_requested = QtCore.Signal(QtWebEngineWidgets.QWebEngineDownloadItem)
    def __init__(self, root_url):
        super(WebPage, self).__init__()
        self.root_url = root_url

    def home(self):
        self.load(QtCore.QUrl(self.root_url))

    def acceptNavigationRequest(self, url, kind, is_main_frame):
        """Open external links in browser and internal links in the webview"""
        ready_url = url.toEncoded().data().decode()
        is_clicked = kind == self.NavigationTypeLinkClicked
        if is_clicked and self.root_url not in ready_url:
            QtGui.QDesktopServices.openUrl(url)
            return False
        return super(WebPage, self).acceptNavigationRequest(url, kind, is_main_frame)


def init_gui(
    application, 
    port=0, 
    width=None, 
    height=None,
    window_title="PySideFlask", 
    icon="appicon.png", 
    argv=None
    ):
    if argv is None:
        argv = sys.argv

    if port == 0:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(('localhost', 0))
        port = sock.getsockname()[1]
        sock.close()

    # Application Level
    qtapp = QtWidgets.QApplication(argv)
    webapp = ApplicationThread(application, port)
    webapp.start()
    qtapp.aboutToQuit.connect(webapp.terminate)

    # Main Window Level
    window = QtWidgets.QMainWindow()
    if not width or not height:
        availableGeometry = application.desktop().availableGeometry(window)
        if not width:
            width = availableGeometry.width() 
        if not height:
            height = availableGeometry.height()
    window.resize(width,height)

    window.resize(width, height)
    window.setWindowTitle(window_title)
    window.setWindowIcon(QtGui.QIcon(icon))

    # WebView Level
    webView = QtWebEngineWidgets.QWebEngineView(window)
    window.setCentralWidget(webView)
    


    
    # < DOWNLOAD >
    # https://doc.qt.io/archives/qtforpython-5.12/_modules/browsertabwidget.html#BrowserTabWidget
    # webView.page()
    # webView.download_requested = QtCore.Signal(QtWebEngineWidgets.QWebEngineDownloadItem)
    #     # self.profile().connect(self._download_requested)
    def download_function(download):
        download.accept()
    webView.page().profile().downloadRequested.connect(download_function)

    # # Download item
    # download = QtWebEngineWidgets.QWebEngineDownloadItem()
    # if download.DownloadRequested:
    #     

    # @QtCore.Slot("QWebEngineDownloadItem*")    
    # def on_downloadRequested(self, download):
    #     download.accept()

    def downloadfunction(download):
        download.accept()


    # < /DOWNLOAD >


    # WebPage Level
    page = WebPage('http://localhost:{}'.format(port))
    page.home()
    webView.setPage(page)

    window.show()
    return qtapp.exec_()
