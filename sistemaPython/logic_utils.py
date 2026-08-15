import sys
import os
import sqlite3
import pandas as pd
import time
import io
from datetime import datetime # Agora o amarelo vai sumir
from tkinter import messagebox
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import qrcode
from database import registrar_log, EXPORT_DIR, DB_PATH

class LogicMixin:
    def exportar_excel(self):
        try:
            # 1. Conexão com o banco (usando caminho relativo seguro)
            conn = sqlite3.connect(DB_PATH, timeout=15)
            df = pd.read_sql_query("SELECT * FROM pedidos", conn)
            conn.close()

            # 2. Gerar nome com data e hora atual
            # O datetime.now() precisa da importação correta no topo
            data_str = datetime.now().strftime('%d%m%Y_%H%M')
            nome_arquivo = f"Relatorio_{data_str}.xlsx"
            
            # 3. Caminho final na pasta de exportação
            caminho_final = os.path.join(EXPORT_DIR, nome_arquivo)

            # 4. Salvar e registrar
            df.to_excel(caminho_final, index=False)
            registrar_log(f"Excel gerado: {nome_arquivo}")
            
            messagebox.showinfo("Sucesso", f"Excel salvo em:\n{nome_arquivo}")
            os.startfile(caminho_final)
            
        except Exception as e:
            messagebox.showerror("Erro Excel", f"Erro ao exportar: {e}")

    def _gerar_imagem_qrcode(self, p):
        """
        Gera a imagem do QR Code (em memória, sem tocar em disco) contendo
        os dados essenciais da ordem/nota, para conferência rápida por
        celular (número, produto, quantidade, cliente e status).
        """
        dados_qr = (
            f"OP: {p[1]}\n"
            f"Produto: {p[2]}\n"
            f"Quantidade: {p[3]}\n"
            f"Cliente: {p[4]}\n"
            f"Status: {p[10] if len(p) > 10 else ''}"
        )

        qr = qrcode.QRCode(
            version=None,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=10,
            border=2,
        )
        qr.add_data(dados_qr)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")

        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)
        return ImageReader(buffer)

    def gerar_pdf_simples(self, p):
        try:
            # Criar nome único para evitar o erro de 'arquivo corrompido'
            timestamp = int(time.time())
            nome_pdf = f"OP_{p[1]}_{timestamp}.pdf"
            caminho_final = os.path.join(EXPORT_DIR, nome_pdf)

            c = canvas.Canvas(caminho_final, pagesize=letter)
            c.setFont("Helvetica-Bold", 16)
            c.drawString(100, 750, f"ORDEM DE PRODUÇÃO: {p[1]}")
            
            c.setFont("Helvetica", 12)
            c.drawString(100, 720, f"Produto: {p[2]}")
            c.drawString(100, 700, f"Quantidade: {p[3]}")
            c.drawString(100, 680, f"Cliente: {p[4]}")

            # QR Code com os dados da nota/ordem, no canto superior direito
            try:
                qr_img = self._gerar_imagem_qrcode(p)
                tamanho_qr = 120
                c.drawImage(
                    qr_img,
                    letter[0] - 100 - tamanho_qr,  # x: alinhado à direita
                    letter[1] - 100 - tamanho_qr,  # y: alinhado ao topo
                    width=tamanho_qr,
                    height=tamanho_qr,
                    preserveAspectRatio=True,
                    mask='auto',
                )
                c.setFont("Helvetica-Oblique", 8)
                c.drawCentredString(
                    letter[0] - 100 - tamanho_qr / 2,
                    letter[1] - 105 - tamanho_qr,
                    "Escaneie para conferir os dados"
                )
            except Exception as e_qr:
                registrar_log(f"Falha ao gerar QR Code no PDF: {e_qr}")

            c.showPage()
            c.save()

            # Espera o Windows processar o arquivo antes de abrir
            time.sleep(0.5)
            if os.path.exists(caminho_final):
                os.startfile(caminho_final)
                
        except Exception as e:
            messagebox.showerror("Erro PDF", f"Falha: {e}")