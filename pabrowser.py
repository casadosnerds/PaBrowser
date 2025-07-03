import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QToolBar, QAction, QLineEdit,
    QPushButton, QCheckBox, QMenu, QMessageBox, QInputDialog, QFileDialog
)
from PyQt5.QtGui import QIcon
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineProfile, QWebEnginePage
from PyQt5.QtWebEngineCore import QWebEngineUrlRequestInterceptor
from PyQt5.QtCore import QUrl


def resource_path(relative_path):
    base_path = getattr(sys, "_MEIPASS", os.path.abspath("."))
    return os.path.join(base_path, relative_path)


class AdBlockInterceptor(QWebEngineUrlRequestInterceptor):
    def __init__(self, blocked_domains):
        super().__init__()
        self.blocked_domains = blocked_domains

    def interceptRequest(self, info):
        url = info.requestUrl().toString()
        for domain in self.blocked_domains:
            if domain in url:
                info.block(True)
                return
        info.block(False)


class CustomWebEnginePage(QWebEnginePage):
    def createWindow(self, _type):
        return self.parent().criar_nova_janela()


class PaBrowser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PaBrowser")
        self.setWindowIcon(QIcon(resource_path("icons/pabrowser.png")))
        self.setGeometry(100, 100, 1200, 800)

        self.home_url = "https://start.duckduckgo.com"
        self.js_enabled = True

        self.profile = QWebEngineProfile.defaultProfile()
        self.profile.downloadRequested.connect(self.gerenciar_download)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1e1e1e;
            }
            QToolBar {
                background-color: #2d2d2d;
                border: none;
            }
            QLineEdit {
                background-color: #3c3c3c;
                color: white;
                border: 1px solid #555;
                padding: 4px;
            }
            QPushButton {
                background-color: #3c3c3c;
                color: white;
                border: 1px solid #555;
                padding: 4px;
            }
            QCheckBox {
                color: white;
            }
            QMenu {
                background-color: #2d2d2d;
                color: white;
            }
            QMessageBox {
                background-color: #2d2d2d;
            }
        """)

        self.blocked_domains = [
            "ads.google.com",
            "doubleclick.net",
            "googlesyndication.com",
            "adservice.google.com",
            "pagead2.googlesyndication.com",
        ]
        self.interceptor = AdBlockInterceptor(self.blocked_domains)

        self.page = CustomWebEnginePage(self.profile, self)
        self.browser = QWebEngineView()
        self.browser.setPage(self.page)
        self.setCentralWidget(self.browser)
        self.browser.setUrl(QUrl(self.home_url))

        navtb = QToolBar("Navegação")
        self.addToolBar(navtb)

        back_btn = QAction(QIcon(resource_path("icons/voltar.png")), "Voltar", self)
        back_btn.triggered.connect(self.browser.back)
        navtb.addAction(back_btn)

        next_btn = QAction(QIcon(resource_path("icons/next.png")), "Avançar", self)
        next_btn.triggered.connect(self.browser.forward)
        navtb.addAction(next_btn)

        reload_btn = QAction(QIcon(resource_path("icons/reload.png")), "Recarregar", self)
        reload_btn.triggered.connect(self.browser.reload)
        navtb.addAction(reload_btn)

        home_btn = QAction(QIcon(resource_path("icons/home.png")), "Início", self)
        home_btn.triggered.connect(self.ir_home)
        navtb.addAction(home_btn)

        self.url_bar = QLineEdit()
        self.url_bar.returnPressed.connect(self.navegar_para_url)
        navtb.addWidget(self.url_bar)

        ir_btn = QPushButton("Ir")
        ir_btn.clicked.connect(self.navegar_para_url)
        navtb.addWidget(ir_btn)

        self.adblock_checkbox = QCheckBox("Bloquear anúncios")
        self.adblock_checkbox.stateChanged.connect(self.toggle_adblock)
        navtb.addWidget(self.adblock_checkbox)

        config_btn = QAction(QIcon(resource_path("icons/config.png")), "Configurações", self)
        config_btn.triggered.connect(self.abrir_menu_configuracoes)
        navtb.addAction(config_btn)

        self.browser.urlChanged.connect(self.atualizar_url)
        self.atualizar_url(self.browser.url())

    def atualizar_url(self, q):
        self.url_bar.setText(q.toString())

    def navegar_para_url(self):
        url = self.url_bar.text().strip()
        if not url.startswith("https://") and not url.startswith("https://"):
            url = "https://" + url
        self.browser.setUrl(QUrl(url))

    def ir_home(self):
        self.browser.setUrl(QUrl(self.home_url))

    def toggle_adblock(self, state):
        if state == 2:
            self.profile.setRequestInterceptor(self.interceptor)
        else:
            self.profile.setRequestInterceptor(None)
        self.browser.reload()

    def abrir_menu_configuracoes(self):
        menu = QMenu(self)

        menu.addAction("Alterar página inicial", self.alterar_pagina_inicial)
        menu.addAction("Ativar / Desativar Javascript", self.toggle_javascript)
        menu.addAction("Limpar dados de navegação", self.limpar_dados)
        menu.addAction("Ver código-fonte da página", self.ver_codigo_fonte)
        menu.addSeparator()
        menu.addAction("Política de Privacidade", lambda: self.abrir_url("https://casadosnerds.pages.dev/privacidade"))
        menu.addAction("Sobre", lambda: self.abrir_url("https://casadosnerds.pages.dev/pabrowser"))

        pos = self.mapToGlobal(self.rect().topRight())
        menu.exec_(pos)

    def alterar_pagina_inicial(self):
        url, ok = QInputDialog.getText(self, "Página Inicial", "Nova URL:")
        if ok and url:
            self.home_url = url if url.startswith("https") else "https://" + url
            QMessageBox.information(self, "Página inicial", f"Alterada para:\n{self.home_url}")

    def toggle_javascript(self):
        self.js_enabled = not self.js_enabled
        self.browser.settings().setAttribute(self.browser.settings().JavascriptEnabled, self.js_enabled)
        self.browser.reload()
        QMessageBox.information(self, "JavaScript", f"JavaScript {'ativado' if self.js_enabled else 'desativado'}")

    def limpar_dados(self):
        if QMessageBox.question(self, "Limpar dados", "Tem certeza?", QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            self.profile.clearHttpCache()
            self.profile.cookieStore().deleteAllCookies()
            QMessageBox.information(self, "Limpeza", "Dados apagados com sucesso.")

    def ver_codigo_fonte(self):
        url = self.browser.url().toString()
        if url:
            self.browser.setUrl(QUrl("view-source:" + url))

    def abrir_url(self, url):
        self.browser.setUrl(QUrl(url))

    def criar_nova_janela(self):
        nova_view = QWebEngineView()
        nova_page = CustomWebEnginePage(self.profile, self)
        nova_view.setPage(nova_page)

        nova_janela = QMainWindow()
        nova_janela.setCentralWidget(nova_view)
        nova_janela.resize(1000, 700)
        nova_janela.setWindowTitle("Nova Aba")
        nova_janela.show()

        return nova_page

    def gerenciar_download(self, download):
        suggested = download.downloadFileName()
        path, _ = QFileDialog.getSaveFileName(self, "Salvar como", suggested)

        if path:
            download.setPath(path)
            download.accept()
            download.finished.connect(lambda: QMessageBox.information(
                self, "Download", f"Download concluído:\n{path}"))
        else:
            download.cancel()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setApplicationName("PaBrowser")
    window = PaBrowser()
    window.show()
    sys.exit(app.exec_())
