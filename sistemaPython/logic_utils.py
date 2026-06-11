import sys
import os
import sqlite3
import pandas as pd
import time
from datetime import datetime # Agora o amarelo vai sumir
from tkinter import messagebox
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from database import registrar_log, EXPORT_DIR

class LogicMixin:
    def exportar_excel(self):
        try:
            # 1. Conexão com o banco (usando caminho relativo seguro)
            conn = sqlite3.connect("producao.db")
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
            
            c.showPage()
            c.save()

            # Espera o Windows processar o arquivo antes de abrir
            time.sleep(0.5)
            if os.path.exists(caminho_final):
                os.startfile(caminho_final)
                
        except Exception as e:
            messagebox.showerror("Erro PDF", f"Falha: {e}")