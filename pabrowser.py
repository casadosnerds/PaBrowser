import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QToolBar, QAction, QLineEdit,
    QPushButton, QCheckBox, QMenu, QMessageBox, QInputDialog, QFileDialog,
    QPlainTextEdit
)
from PyQt5.QtGui import QIcon
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineProfile, QWebEnginePage, QWebEngineDownloadItem
from PyQt5.QtWebEngineCore import QWebEngineUrlRequestInterceptor
from PyQt5.QtCore import QUrl
from PyQt5.QtWebEngineWidgets import QWebEngineContextMenuData



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
    def __init__(self, profile, parent=None):
        super().__init__(profile, parent)
        self.browser_parent = parent

    def createWindow(self, _type):
        return self.browser_parent.criar_nova_janela()

    def contextMenuEvent(self, event):
        menu = QMenu()

        context_data = self.contextMenuData()

        # Navegação
        voltar_action = QAction("Voltar", self)
        voltar_action.triggered.connect(self.back)
        menu.addAction(voltar_action)

        avancar_action = QAction("Avançar", self)
        avancar_action.triggered.connect(self.forward)
        menu.addAction(avancar_action)

        recarregar_action = QAction("Recarregar", self)
        recarregar_action.triggered.connect(self.reload)
        menu.addAction(recarregar_action)

        menu.addSeparator()

        # Se tem link
        if context_data.linkUrl().isValid():
            link = context_data.linkUrl().toString()

            abrir_nova_janela_action = QAction("Abrir link em nova janela", self)
            abrir_nova_janela_action.triggered.connect(lambda: self.browser_parent.nova_janela_com_url(link))
            menu.addAction(abrir_nova_janela_action)

            baixar_link_action = QAction("Baixar link...", self)
            baixar_link_action.triggered.connect(lambda: self.browser_parent.baixar_url(link))
            menu.addAction(baixar_link_action)

            menu.addSeparator()

        # Se tem imagem
        if context_data.mediaType() == QWebEngineContextMenuData.MediaTypeImage:
            img_url = context_data.mediaUrl().toString()

            baixar_imagem_action = QAction("Baixar imagem...", self)
            baixar_imagem_action.triggered.connect(lambda: self.browser_parent.baixar_url(img_url))
            menu.addAction(baixar_imagem_action)

            menu.addSeparator()

        # Seleção
        selecionar_tudo_action = QAction("Selecionar tudo", self)
        selecionar_tudo_action.triggered.connect(self.selectAll)
        menu.addAction(selecionar_tudo_action)

        copiar_action = QAction("Copiar", self)
        copiar_action.triggered.connect(self.copy)
        menu.addAction(copiar_action)

        colar_action = QAction("Colar", self)
        colar_action.triggered.connect(self.paste)
        menu.addAction(colar_action)

        cortar_action = QAction("Cortar", self)
        cortar_action.triggered.connect(self.cut)
        menu.addAction(cortar_action)

        menu.addSeparator()

        # Salvar página
        salvar_pagina_action = QAction("Salvar página como...", self)
        salvar_pagina_action.triggered.connect(lambda: self.triggerAction(QWebEnginePage.SavePage))
        menu.addAction(salvar_pagina_action)

        menu.addSeparator()

        # Código fonte
        ver_codigo_action = QAction("Ver código-fonte da página", self)
        ver_codigo_action.triggered.connect(self.browser_parent.ver_codigo_fonte)
        menu.addAction(ver_codigo_action)

        menu.exec_(event.globalPos())


class PrivateBrowserWindow(QMainWindow):
    def __init__(self, url):
        super().__init__()
        self.setWindowTitle("PaBrowser - Modo Privado")

        self.profile = QWebEngineProfile(self)
        self.profile.setPersistentCookiesPolicy(QWebEngineProfile.NoPersistentCookies)
        self.profile.setHttpCacheType(QWebEngineProfile.MemoryHttpCache)

        self.page = CustomWebEnginePage(self.profile, self)
        self.browser = QWebEngineView()
        self.browser.setPage(self.page)
        self.setCentralWidget(self.browser)

        self.browser.titleChanged.connect(self.atualizar_titulo)

        self.browser.setUrl(QUrl(url))
        self.resize(1200, 800)
        self.show()

    def atualizar_titulo(self, title):
        self.setWindowTitle(f"{title} - Modo Privado")


class PaBrowser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PaBrowser")
        self.setGeometry(100, 100, 1200, 800)

        self.home_url = "https://start.duckduckgo.com"
        self.js_enabled = True

        self.profile = QWebEngineProfile.defaultProfile()
        self.profile.downloadRequested.connect(self.gerenciar_download)

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

        self.codigo_fonte_janela = None

    def atualizar_url(self, q):
        self.url_bar.setText(q.toString())

    def navegar_para_url(self):
        url = self.url_bar.text().strip()
        if not url.startswith("http://") and not url.startswith("https://"):
            url = "http://" + url
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

        menu.addAction("Modo Privado", self.abrir_janela_privada)
        menu.addAction("Alterar página inicial", self.alterar_pagina_inicial)
        menu.addAction("Desativar Javascript", self.toggle_javascript)
        menu.addAction("Limpar dados de navegação", self.limpar_dados)
        menu.addSeparator()
        menu.addAction("Política de Privacidade", lambda: self.abrir_url("https://casadosnerds.github.io/pabrowser/privacidade.html"))
        menu.addAction("Sobre", lambda: self.abrir_url("https://casadosnerds.github.io/pabrowser/sobre.html"))

        pos = self.mapToGlobal(self.rect().topRight())
        menu.exec_(pos)

    def abrir_janela_privada(self):
        url = self.browser.url().toString()
        if not url:
            url = self.home_url
        self.janela_privada = PrivateBrowserWindow(url)

    def alterar_pagina_inicial(self):
        url, ok = QInputDialog.getText(self, "Página Inicial", "Nova URL:")
        if ok and url:
            self.home_url = url if url.startswith("http") else "http://" + url
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

    def nova_janela_com_url(self, url):
        nova_janela = QMainWindow()
        profile = QWebEngineProfile()
        page = CustomWebEnginePage(profile, nova_janela)
        view = QWebEngineView()
        view.setPage(page)
        nova_janela.setCentralWidget(view)
        nova_janela.resize(1000, 700)
        nova_janela.setWindowTitle("Nova Janela")
        nova_janela.show()
        view.setUrl(QUrl(url))

    def baixar_url(self, url):
        path, _ = QFileDialog.getSaveFileName(self, "Salvar como", os.path.basename(url))
        if path:
            from urllib.request import urlretrieve
            try:
                urlretrieve(url, path)
                QMessageBox.information(self, "Download", f"Download concluído:\n{path}")
            except Exception as e:
                QMessageBox.warning(self, "Erro", f"Falha ao baixar:\n{e}")

    def gerenciar_download(self, download: QWebEngineDownloadItem):
        suggested = download.downloadFileName()
        path, _ = QFileDialog.getSaveFileName(self, "Salvar como", suggested)
        if path:
            download.setPath(path)
            download.accept()
            download.finished.connect(lambda: QMessageBox.information(self, "Download", f"Download concluído:\n{path}"))
        else:
            download.cancel()

    def ver_codigo_fonte(self):
        def mostrar_html(html):
            self.codigo_fonte_janela = QMainWindow()
            self.codigo_fonte_janela.setWindowTitle("Código-fonte da página")
            editor = QPlainTextEdit()
            editor.setPlainText(html)
            editor.setReadOnly(True)
            self.codigo_fonte_janela.setCentralWidget(editor)
            self.codigo_fonte_janela.resize(800, 600)
            self.codigo_fonte_janela.show()
        self.browser.page().toHtml(mostrar_html)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setApplicationName("PaBrowser")
    window = PaBrowser()
    window.show()
    sys.exit(app.exec_())
