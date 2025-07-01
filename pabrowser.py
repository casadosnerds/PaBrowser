import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QToolBar, QAction, QLineEdit, QPushButton,
    QCheckBox, QDialog, QVBoxLayout, QLabel, QLineEdit as QLineEditDialog,
    QDialogButtonBox, QMenu, QMessageBox
)
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineProfile, QWebEngineSettings, QWebEnginePage
from PyQt5.QtCore import QUrl, Qt
from PyQt5.QtGui import QIcon, QPalette, QColor


class HomePageDialog(QDialog):
    def __init__(self, current_url, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configurar página inicial")
        self.setFixedSize(400, 120)

        layout = QVBoxLayout()

        label = QLabel("Digite a URL da página inicial:")
        layout.addWidget(label)

        self.url_input = QLineEditDialog()
        self.url_input.setText(current_url)
        layout.addWidget(self.url_input)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.setLayout(layout)

    def get_url(self):
        return self.url_input.text().strip()


class DNSDialog(QDialog):
    def __init__(self, current_dns='', parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configurar DNS personalizado (DoH)")
        self.setFixedSize(400, 150)

        layout = QVBoxLayout()
        label = QLabel("Digite o URL do servidor DoH:")
        layout.addWidget(label)

        self.dns_input = QLineEditDialog()
        self.dns_input.setText(current_dns)
        layout.addWidget(self.dns_input)

        self.reset_btn = QPushButton("Redefinir")
        self.reset_btn.clicked.connect(self.reset_dns)
        layout.addWidget(self.reset_btn)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.setLayout(layout)

    def get_dns(self):
        return self.dns_input.text().strip()

    def reset_dns(self):
        self.dns_input.setText("")


class PrivateBrowser(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("PaBrowser - Modo Privado")
        self.setGeometry(150, 150, 1000, 700)
        self.setWindowIcon(QIcon("icons/pabrowser.png"))

        # Perfil temporário sem persistência
        self.profile = QWebEngineProfile(self)
        self.profile.setPersistentCookiesPolicy(QWebEngineProfile.NoPersistentCookies)
        self.profile.setCachePath("")  # cache em memória
        self.profile.setPersistentStoragePath("")  # armazenamento em memória

        self.page = QWebEnginePage(self.profile, self)

        self.browser = QWebEngineView()
        self.browser.setPage(self.page)
        self.browser.setUrl(QUrl("https://www.google.com"))
        self.setCentralWidget(self.browser)

        self.browser.titleChanged.connect(self.update_title)

    def update_title(self, title):
        self.setWindowTitle(f"{title} - Modo Privado")


class PaBrowser(QMainWindow):
    def __init__(self):
        super().__init__()

        self.home_url = "https://www.google.com"
        self.custom_dns = ""
        self.javascript_enabled = True
        self.private_windows = []  # Guarda as janelas privadas abertas

        self.setWindowTitle("PaBrowser")
        self.setGeometry(100, 100, 1000, 700)
        self.setWindowIcon(QIcon("icons/pabrowser.png"))

        self.enable_dark_theme()

        self.browser = QWebEngineView()
        self.set_browser_profile()
        self.browser.setUrl(QUrl(self.home_url))
        self.setCentralWidget(self.browser)

        nav_bar = QToolBar()
        self.addToolBar(nav_bar)

        back_btn = QAction(QIcon("icons/voltar.png"), "Voltar", self)
        back_btn.triggered.connect(self.browser.back)
        nav_bar.addAction(back_btn)

        forward_btn = QAction(QIcon("icons/next.png"), "Avançar", self)
        forward_btn.triggered.connect(self.browser.forward)
        nav_bar.addAction(forward_btn)

        reload_btn = QAction(QIcon("icons/reload.png"), "Recarregar", self)
        reload_btn.triggered.connect(self.browser.reload)
        nav_bar.addAction(reload_btn)

        home_btn = QAction(QIcon("icons/home.png"), "Início", self)
        home_btn.triggered.connect(self.navigate_home)
        nav_bar.addAction(home_btn)

        self.url_bar = QLineEdit()
        self.url_bar.setPlaceholderText("Digite a URL")
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        nav_bar.addWidget(self.url_bar)

        go_button = QPushButton("Ir")
        go_button.clicked.connect(self.navigate_to_url)
        nav_bar.addWidget(go_button)

        self.adblock_checkbox = QCheckBox("Bloquear anúncios")
        self.adblock_checkbox.setChecked(False)
        nav_bar.addWidget(self.adblock_checkbox)

        settings_menu = QMenu()

        private_action = QAction("Modo privado", self)
        private_action.triggered.connect(self.open_private_window)
        settings_menu.addAction(private_action)

        home_action = QAction("Alterar página inicial", self)
        home_action.triggered.connect(self.open_settings_dialog)
        settings_menu.addAction(home_action)

        dns_action = QAction("DNS Personalizado", self)
        dns_action.triggered.connect(self.open_dns_dialog)
        settings_menu.addAction(dns_action)

        js_action = QAction("Desativar JavaScript", self, checkable=True)
        js_action.setChecked(not self.javascript_enabled)
        js_action.toggled.connect(self.toggle_javascript)
        settings_menu.addAction(js_action)

        clear_action = QAction("Limpar dados de navegação", self)
        clear_action.triggered.connect(self.clear_browser_data)
        settings_menu.addAction(clear_action)

        settings_menu.addSeparator()

        privacy_action = QAction("Política de Privacidade", self)
        privacy_action.triggered.connect(
            lambda: self.browser.setUrl(QUrl("https://seusite.com/privacidade"))
        )
        settings_menu.addAction(privacy_action)

        about_action = QAction("Sobre", self)
        about_action.triggered.connect(
            lambda: self.browser.setUrl(QUrl("https://seusite.com/sobre"))
        )
        settings_menu.addAction(about_action)

        settings_btn = QPushButton()
        settings_btn.setIcon(QIcon("icons/settings.png"))
        settings_btn.setMenu(settings_menu)
        nav_bar.addWidget(settings_btn)

        self.browser.urlChanged.connect(self.update_url)
        self.browser.loadFinished.connect(self.on_load_finished)
        self.browser.titleChanged.connect(self.setWindowTitle)

    def set_browser_profile(self):
        profile = QWebEngineProfile.defaultProfile()
        profile.settings().setAttribute(
            QWebEngineSettings.JavascriptEnabled, self.javascript_enabled
        )

    def navigate_home(self):
        self.browser.setUrl(QUrl(self.home_url))

    def navigate_to_url(self):
        url = self.url_bar.text().strip()
        if not url.startswith(("http://", "https://")):
            url = "http://" + url
        self.browser.setUrl(QUrl(url))

    def update_url(self, qurl):
        self.url_bar.setText(qurl.toString())

    def on_load_finished(self):
        if self.adblock_checkbox.isChecked():
            adblock_js = """
            const blockedDomains = [
                "doubleclick.net", "ads.google.com", "googlesyndication.com",
                "adservice.google.com", "facebook.net", "adnxs.com",
                "taboola.com", "outbrain.com", "zedo.com", "revcontent.com"
            ];
            function shouldBlock(url) {
                return blockedDomains.some(domain => url.includes(domain));
            }
            const iframes = document.getElementsByTagName('iframe');
            for (let i = iframes.length - 1; i >= 0; i--) {
                let src = iframes[i].src;
                if (shouldBlock(src)) iframes[i].remove();
            }
            const scripts = document.getElementsByTagName('script');
            for (let i = scripts.length - 1; i >= 0; i--) {
                let src = scripts[i].src;
                if (shouldBlock(src)) scripts[i].remove();
            }
            """
            self.browser.page().runJavaScript(adblock_js)

    def open_settings_dialog(self):
        dialog = HomePageDialog(self.home_url, self)
        if dialog.exec() == QDialog.Accepted:
            new_url = dialog.get_url()
            if new_url:
                if not new_url.startswith(("http://", "https://")):
                    new_url = "http://" + new_url
                self.home_url = new_url

    def open_dns_dialog(self):
        dialog = DNSDialog(self.custom_dns, self)
        if dialog.exec() == QDialog.Accepted:
            self.custom_dns = dialog.get_dns()
            QMessageBox.information(
                self, "DNS", "DNS personalizado atualizado! (Nota: simulado)"
            )

    def open_private_window(self):
        try:
            private_window = PrivateBrowser()
            private_window.show()
            self.private_windows.append(private_window)
        except Exception as e:
            import traceback

            print("Erro ao abrir janela privada:", e)
            traceback.print_exc()
            QMessageBox.critical(
                self, "Erro", f"Não foi possível abrir a janela privada:\n{e}"
            )

    def toggle_javascript(self, checked):
        self.javascript_enabled = not checked
        self.set_browser_profile()
        QMessageBox.information(
            self, "JavaScript", "JavaScript %s" % ("desativado" if checked else "ativado")
        )

    def clear_browser_data(self):
        reply = QMessageBox.question(
            self,
            "Limpar dados",
            "Deseja realmente limpar todos os dados de navegação?",
            QMessageBox.Ok | QMessageBox.Cancel,
        )
        if reply == QMessageBox.Ok:
            profile = QWebEngineProfile.defaultProfile()
            profile.clearHttpCache()
            profile.cookieStore().deleteAllCookies()
            QMessageBox.information(self, "Dados limpos", "Dados do usuário excluídos com sucesso.")

    def enable_dark_theme(self):
        dark_palette = QPalette()
        dark_palette.setColor(QPalette.Window, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.WindowText, Qt.white)
        dark_palette.setColor(QPalette.Base, QColor(25, 25, 25))
        dark_palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ToolTipBase, Qt.white)
        dark_palette.setColor(QPalette.ToolTipText, Qt.white)
        dark_palette.setColor(QPalette.Text, Qt.white)
        dark_palette.setColor(QPalette.Button, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ButtonText, Qt.white)
        dark_palette.setColor(QPalette.BrightText, Qt.red)
        dark_palette.setColor(QPalette.Link, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.HighlightedText, Qt.black)
        app.setPalette(dark_palette)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PaBrowser()
    window.show()
    sys.exit(app.exec_())
