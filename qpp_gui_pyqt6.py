#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Downloader M3U8/TS com interface PyQt6
- Colar link .m3u8
- Selecionar pasta destino
- Barra de progresso por número de segmentos
- Log visual (fundo preto, texto verde) mostrando etapas
- Remove arquivos .ts temporários ao final
"""

import os
import requests
from urllib.parse import urljoin
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QLineEdit, QPushButton,
    QProgressBar, QTextEdit, QFileDialog, QHBoxLayout, QVBoxLayout, QMessageBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
import sys
import traceback

# ---------------- Worker Thread ----------------
class DownloadWorker(QThread):
    progress_changed = pyqtSignal(int, int)  # atual, total
    log = pyqtSignal(str)
    finished_success = pyqtSignal(str)
    finished_error = pyqtSignal(str)

    def __init__(self, m3u8_url: str, pasta_destino: str, nome_saida: str = "resultado.mp4"):
        super().__init__()
        self.m3u8_url = m3u8_url
        self.pasta_destino = pasta_destino
        self.nome_saida = nome_saida
        self._is_running = True

    def stop(self):
        self._is_running = False

    def run(self):
        try:
            self.log.emit("Buscando endereço .m3u8...")
            # Busca playlist
            resp = requests.get(self.m3u8_url, timeout=30)
            resp.raise_for_status()
            conteudo = resp.text

            # Extrair segmentos: linhas não vazias que não começam com #
            linhas = [l.strip() for l in conteudo.splitlines() if l.strip() != ""]
            segmentos = [l for l in linhas if not l.startswith("#")]

            # Em muitos casos o arquivo tem linhas de extensão e linhas de segmentos.
            # Filtrar por .ts se possível, se não, aceitar as linhas não comentadas.
            ts_segmentos = [s for s in segmentos if ".ts" in s]
            if ts_segmentos:
                segmentos = ts_segmentos

            total = len(segmentos)
            if total == 0:
                self.log.emit("Nenhum segmento (.ts) encontrado na playlist.")
                self.finished_error.emit("Nenhum arquivo .ts encontrado no .m3u8.")
                return

            self.log.emit(f"{total} segmentos encontrados. Iniciando download sequencial...")

            os.makedirs(self.pasta_destino, exist_ok=True)
            arquivos_ts = []

            # Download sequencial
            for idx, seg in enumerate(segmentos, start=1):
                if not self._is_running:
                    self.log.emit("Operação cancelada pelo usuário.")
                    self.finished_error.emit("Cancelado")
                    return

                # Construir URL absoluto
                url_ts = urljoin(self.m3u8_url, seg)
                nome_ts = os.path.join(self.pasta_destino, f"seg_{idx:05d}.ts")
                self.log.emit(f"Processando arquivo sequencial {idx:03d}/{total}: {os.path.basename(nome_ts)}")
                # Download com streaming
                with requests.get(url_ts, stream=True, timeout=60) as r:
                    r.raise_for_status()
                    with open(nome_ts, "wb") as f:
                        for chunk in r.iter_content(chunk_size=1024*1024):
                            if not self._is_running:
                                self.log.emit("Operação cancelada pelo usuário.")
                                self.finished_error.emit("Cancelado")
                                return
                            if chunk:
                                f.write(chunk)

                arquivos_ts.append(nome_ts)
                self.progress_changed.emit(idx, total)

            self.log.emit("Todos os segmentos baixados. Juntando arquivos em saída final...")
            # Criar arquivo final juntando os TS
            caminho_saida = os.path.join(self.pasta_destino, self.nome_saida)
            with open(caminho_saida, "wb") as outfile:
                for ts in arquivos_ts:
                    with open(ts, "rb") as infile:
                        while True:
                            buf = infile.read(1024*1024)
                            if not buf:
                                break
                            outfile.write(buf)

            self.log.emit(f"Gravando em pasta: {caminho_saida}")
            # Remover arquivos temporários
            self.log.emit("Removendo temporários (.ts)...")
            erros_remocao = []
            for ts in arquivos_ts:
                try:
                    os.remove(ts)
                except Exception as ex:
                    erros_remocao.append((ts, str(ex)))

            if erros_remocao:
                msg = f"Arquivos finais gerados, mas ocorreram erros na remoção de temporários: {erros_remocao}"
                self.log.emit(msg)
                # sinaliza sucesso apesar de problemas na limpeza
                self.finished_success.emit(caminho_saida)
            else:
                self.log.emit("Arquivos temporários removidos com sucesso.")
                self.finished_success.emit(caminho_saida)

        except Exception as e:
            tb = traceback.format_exc()
            self.log.emit(f"Erro: {str(e)}")
            self.log.emit(tb)
            self.finished_error.emit(str(e))


# ---------------- Main Window ----------------
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Baixar MP4 de M3U8/TS - Versão AI.01.00")
        self.setMinimumSize(700, 520)

        # Widgets
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout()
        central.setLayout(layout)

        # Destino
        h_dest = QHBoxLayout()
        lbl_dest = QLabel("Pasta de destino:")
        self.input_dest = QLineEdit()
        self.input_dest.setPlaceholderText("Selecione pasta de destino")
        btn_browse = QPushButton("Selecionar")
        btn_browse.clicked.connect(self.selecionar_pasta)
        h_dest.addWidget(lbl_dest)
        h_dest.addWidget(self.input_dest)
        h_dest.addWidget(btn_browse)
        layout.addLayout(h_dest)

        # URL
        lbl_url = QLabel("URL do arquivo .m3u8:")
        #self.input_url = QLineEdit()
        self.input_url = QTextEdit()
        self.input_url.setPlaceholderText("Cole aqui a URL do .m3u8")
        self.input_url.setFixedHeight(230) # Adicionado
        layout.addWidget(lbl_url)
        layout.addWidget(self.input_url)        

        # Botões
        h_buttons = QHBoxLayout()
        self.btn_start = QPushButton("Iniciar Download")
        self.btn_start.setFixedHeight(40) # Adicionado
        self.btn_start.clicked.connect(self.iniciar_download)
        self.btn_cancel = QPushButton("Cancelar")
        self.btn_cancel.setFixedHeight(40) # Adicionado
        self.btn_cancel.clicked.connect(self.cancelar_download)
        self.btn_cancel.setEnabled(False)
        h_buttons.addWidget(self.btn_start)
        h_buttons.addWidget(self.btn_cancel)
        layout.addLayout(h_buttons)

        # Progresso
        lbl_prog = QLabel("Progresso:")
        self.progress = QProgressBar()
        self.progress.setMinimum(0)
        self.progress.setValue(0)
        layout.addWidget(lbl_prog)
        layout.addWidget(self.progress)

        # Log (fundo preto, texto verde)
        lbl_log = QLabel("Log de execução:")
        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        # Estilo: fundo preto e texto verde
        self.log_area.setStyleSheet("background-color: black; color: #00FF66; font-family: Consolas, monospace;")
        layout.addWidget(lbl_log)
        layout.addWidget(self.log_area)

        # Status
        self.status_label = QLabel("")
        layout.addWidget(self.status_label)

        # Worker
        self.worker = None

    def selecionar_pasta(self):
        pasta = QFileDialog.getExistingDirectory(self, "Selecionar pasta de destino", os.path.expanduser("~"))
        if pasta:
            self.input_dest.setText(pasta)

    def iniciar_download(self):
        url = self.input_url.text().strip()
        pasta = self.input_dest.text().strip()
        if not url:
            QMessageBox.warning(self, "Atenção", "Informe a URL do arquivo .m3u8.")
            return
        if not pasta:
            QMessageBox.warning(self, "Atenção", "Selecione a pasta de destino.")
            return

        # Desabilitar botões
        self.btn_start.setEnabled(False)
        self.btn_cancel.setEnabled(True)
        self.log_area.clear()
        self.progress.setValue(0)
        self.status_label.setText("Iniciando...")

        # Criar e iniciar worker
        nome_saida = "resultado.mp4"
        self.worker = DownloadWorker(url, pasta, nome_saida)
        self.worker.progress_changed.connect(self.on_progress)
        self.worker.log.connect(self.on_log)
        self.worker.finished_success.connect(self.on_finished_success)
        self.worker.finished_error.connect(self.on_finished_error)
        self.worker.start()

    def cancelar_download(self):
        if self.worker and self.worker.isRunning():
            self.worker.stop()
            self.on_log("Solicitado cancelamento. Aguardando interrupção...")

    def on_progress(self, atual, total):
        # Atualiza barra de progresso com percentagem
        pct = int((atual / total) * 100) if total else 0
        self.progress.setMaximum(100)
        self.progress.setValue(pct)
        self.status_label.setText(f"Baixando {atual}/{total} ({pct}%)")

    def on_log(self, texto):
        # Append no QTextEdit mantendo scroll no final
        self.log_area.append(texto)

    def on_finished_success(self, caminho_saida):
        self.on_log("Processo finalizado com sucesso.")
        self.on_log(f"Arquivo final: {caminho_saida}")
        QMessageBox.information(self, "Concluído", f"Download concluído:\n{caminho_saida}")
        self.btn_start.setEnabled(True)
        self.btn_cancel.setEnabled(False)
        self.status_label.setText("Concluído")
        self.progress.setValue(100)

    def on_finished_error(self, erro):
        self.on_log(f"Finalizado com erro: {erro}")
        QMessageBox.critical(self, "Erro", f"Ocorreu um erro:\n{erro}")
        self.btn_start.setEnabled(True)
        self.btn_cancel.setEnabled(False)
        self.status_label.setText("Erro")

# ---------------- Run ----------------
def main():
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
