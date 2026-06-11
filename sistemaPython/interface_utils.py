import os
import customtkinter as ctk
from tkinter import messagebox, ttk
import sqlite3
from styles import *
from database import registrar_log, cadastrar_usuario, autenticar_usuario

# Força tema escuro idêntico ao site web
import customtkinter as _ctk_setup
_ctk_setup.set_appearance_mode("Dark")

# No seu main.py, logo abaixo de DB_PATH:
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "producao.db")

# Nova pasta para arquivos
EXPORT_DIR = os.path.join(BASE_DIR, "arquivos_exportados")
if not os.path.exists(EXPORT_DIR):
    os.makedirs(EXPORT_DIR)

class InterfaceMixin:
    # --- NAVEGAÇÃO ---
    def toggle_sidebar(self):
        if not self.sidebar_aberta:
            self.sidebar_frame.place(x=0, y=70); self.sidebar_frame.lift(); self.sidebar_aberta = True
        else:
            self.sidebar_frame.place(x=-260, y=70); self.sidebar_aberta = False

    def fechar_telas_adicionais(self):
        if hasattr(self, 'frete_container'): self.frete_container.destroy()
        if hasattr(self, 'rastreio_container'): self.rastreio_container.destroy()
        if hasattr(self, 'tabela_container'): self.tabela_container.destroy()
        if hasattr(self, 'logs_container'): self.logs_container.destroy()

    def desligar_sistema(self):
        if messagebox.askyesno("Sair", "Encerrar o sistema?"): self.destroy(); import sys; sys.exit()

    def trocar_conta(self):
        if messagebox.askyesno("Trocar Conta", "Voltar para o login?"):
            for widget in self.winfo_children(): widget.destroy()
            self.tela_login()

    def alternar_tema(self):
        if ctk.get_appearance_mode() == "Light": ctk.set_appearance_mode("Dark")
        else: ctk.set_appearance_mode("Light")

    # --- TELAS PRINCIPAIS ---
    def tela_login(self):
        # Limpa widgets antigos para evitar sobreposição
        for widget in self.winfo_children():
            widget.destroy()

        # Container Principal de Login (Estilo Card Mercado Livre)
        self.login_frame = ctk.CTkFrame(
            self, 
            width=420, 
            height=560, 
            corner_radius=24, 
            border_width=1, 
            border_color="#1E3A5F",
            fg_color="#162040"
        )
        self.login_frame.place(relx=0.5, rely=0.5, anchor="center")
        self.login_frame.pack_propagate(False)

        # --- BOTÃO DE MUDAR TEMA (🌓) ---
        # Posicionado no canto superior direito do card
        self.btn_tema_login = ctk.CTkButton(
            self.login_frame, 
            text="🌓", 
            width=40, 
            height=40,
            fg_color="transparent", 
            text_color=ML_TEXTO,
            font=("Trebuchet MS", 18),
            hover_color="#1E2D4A",
            command=self.alternar_tema 
        )
        self.btn_tema_login.place(x=340, y=15)

        # Título do Sistema
        ctk.CTkLabel(
            self.login_frame, 
            text="LOGISTOCK PRO", 
            font=("Trebuchet MS", 28, "bold"), 
            text_color=ML_AZUL
        ).pack(pady=(60, 30))

        # Campos de Entrada Estilizados
        self.user_entry = ctk.CTkEntry(
            self.login_frame, 
            placeholder_text="E-mail", 
            width=300, 
            height=45, 
            corner_radius=10
        )
        self.user_entry.pack(pady=10)
        
        self.pass_entry = ctk.CTkEntry(
            self.login_frame, 
            placeholder_text="Senha", 
            show="*", 
            width=300, 
            height=45, 
            corner_radius=10
        )
        self.pass_entry.pack(pady=10)

        # Botão de Acesso Principal
        ctk.CTkButton(
            self.login_frame, 
            text="ENTRAR NO SISTEMA", 
            width=300, 
            height=50, 
            font=("Trebuchet MS", 14, "bold"),
            fg_color=ML_AZUL,
            hover_color="#FFD740",
            text_color="#0A1628",
            corner_radius=50,
            command=self.login_logic
        ).pack(pady=(20, 5))

        # Botão Criar Conta
        ctk.CTkButton(
            self.login_frame,
            text="Criar nova conta",
            width=300,
            height=36,
            font=("Trebuchet MS", 12),
            fg_color="transparent",
            text_color=ML_AZUL,
            hover_color="#1E2D4A",
            corner_radius=50,
            border_width=1,
            border_color=ML_AZUL,
            command=self.tela_cadastro
        ).pack(pady=(0, 10))

        # --- BOTÃO DE DESLIGAR SISTEMA ---
        # No rodapé do card para segurança
        ctk.CTkButton(
            self.login_frame, 
            text="DESLIGAR SISTEMA", 
            fg_color="transparent", 
            text_color=ML_VERMELHO, 
            font=("Trebuchet MS", 11, "bold"),
            hover_color=("#FFEBEE", "#3D1A1A"),
            command=self.desligar_sistema
        ).pack(pady=(0, 20))
        
    def login_logic(self):
        email = self.user_entry.get().strip()
        senha = self.pass_entry.get()

        if not email or not senha:
            messagebox.showwarning("Atenção", "Preencha o e-mail e a senha.")
            return

        ok, perfil = autenticar_usuario(email, senha)
        if not ok:
            messagebox.showerror("Acesso Negado", "E-mail ou senha incorretos.\nVerifique seus dados ou crie uma conta.")
            return

        # Desabilita o botão para evitar cliques duplos
        for widget in self.login_frame.winfo_children():
            if isinstance(widget, ctk.CTkButton) and "ENTRAR" in widget.cget("text"):
                widget.configure(state="disabled", text="Verificando...")

        if True:  # bloco para manter indentação original

            # Barra de progresso
            self._progress_bar = ctk.CTkProgressBar(
                self.login_frame,
                width=300,
                height=10,
                corner_radius=5,
                fg_color="#1E2D4A",
                progress_color=ML_AZUL
            )
            self._progress_bar.pack(pady=(0, 5))
            self._progress_bar.set(0)

            # Label de status
            self._status_label = ctk.CTkLabel(
                self.login_frame,
                text="Conectando ao sistema...",
                font=("Trebuchet MS", 11),
                text_color="#7F8C8D"
            )
            self._status_label.pack(pady=(0, 10))

            # Mensagens de progresso em 3 etapas (a cada 1 segundo)
            mensagens = [
                (1000, 0.33, "Autenticando usuário..."),
                (2000, 0.66, "Carregando dados..."),
                (3000, 1.0,  "Bem-vindo ao LogiStock Pro!"),
            ]

            def atualizar_progresso(idx=0):
                if idx < len(mensagens):
                    delay, valor, texto = mensagens[idx]
                    self._progress_bar.set(valor)
                    self._status_label.configure(text=texto)
                    self.after(1000, lambda: atualizar_progresso(idx + 1))
                else:
                    # 3 segundos completados — abre o sistema
                    self.login_frame.destroy()
                    if perfil == "Entregador":
                        self.tela_entrega_v2()
                    else:
                        self.tela_principal(perfil)

            self.after(1000, lambda: atualizar_progresso(0))
        
    def tela_cadastro(self):
        """Tela de cadastro de novo usuário."""
        # Remove a tela de login
        for widget in self.winfo_children():
            widget.destroy()

        cad_frame = ctk.CTkFrame(
            self,
            width=440,
            height=620,
            corner_radius=24,
            border_width=1,
            border_color="#1E3A5F",
            fg_color="#162040"
        )
        cad_frame.place(relx=0.5, rely=0.5, anchor="center")
        cad_frame.pack_propagate(False)

        # Botão tema
        ctk.CTkButton(
            cad_frame, text="🌓", width=40, height=40,
            fg_color="transparent", text_color=ML_TEXTO,
            font=("Trebuchet MS", 18), hover_color="#1E2D4A",
            command=self.alternar_tema
        ).place(x=360, y=15)

        ctk.CTkLabel(
            cad_frame, text="CRIAR CONTA",
            font=("Trebuchet MS", 26, "bold"), text_color=ML_AZUL
        ).pack(pady=(55, 5))

        ctk.CTkLabel(
            cad_frame, text="Preencha os dados abaixo",
            font=("Trebuchet MS", 12), text_color="#7F8C8D"
        ).pack(pady=(0, 20))

        # E-mail
        cad_email = ctk.CTkEntry(
            cad_frame, placeholder_text="E-mail",
            width=320, height=45, corner_radius=10
        )
        cad_email.pack(pady=6)

        # Senha
        cad_senha = ctk.CTkEntry(
            cad_frame, placeholder_text="Senha (mín. 6 caracteres)",
            show="*", width=320, height=45, corner_radius=10
        )
        cad_senha.pack(pady=6)

        # Confirmar senha
        cad_conf = ctk.CTkEntry(
            cad_frame, placeholder_text="Confirmar senha",
            show="*", width=320, height=45, corner_radius=10
        )
        cad_conf.pack(pady=6)

        # Perfil
        ctk.CTkLabel(
            cad_frame, text="Tipo de conta",
            font=("Trebuchet MS", 12, "bold"), text_color="#7F8C8D"
        ).pack(pady=(10, 0))

        perfil_var = ctk.StringVar(value="PCP")
        ctk.CTkSegmentedButton(
            cad_frame,
            values=["PCP", "Gestão", "Produção", "Entregador"],
            variable=perfil_var,
            width=320,
            height=38,
            font=("Trebuchet MS", 12, "bold"),
            fg_color="#0A1628",
            selected_color=ML_AZUL,
            selected_hover_color="#FFD740",
            unselected_color="#1E2D4A",
            unselected_hover_color="#243A5A",
            text_color="#E6EDF3",
        ).pack(pady=8)

        # Label de feedback
        lbl_feedback = ctk.CTkLabel(
            cad_frame, text="",
            font=("Trebuchet MS", 11),
            text_color="#E74C3C"
        )
        lbl_feedback.pack(pady=(2, 0))

        def realizar_cadastro():
            email = cad_email.get().strip()
            senha = cad_senha.get()
            conf = cad_conf.get()
            perfil = perfil_var.get()

            if senha != conf:
                lbl_feedback.configure(text="As senhas não coincidem.", text_color="#E74C3C")
                return

            ok, msg = cadastrar_usuario(email, senha, perfil)
            if ok:
                lbl_feedback.configure(text=msg, text_color="#2ECC71")
                self.after(1500, self.tela_login)
            else:
                lbl_feedback.configure(text=msg, text_color="#E74C3C")

        ctk.CTkButton(
            cad_frame, text="CADASTRAR",
            width=320, height=50,
            font=("Trebuchet MS", 14, "bold"),
            fg_color=ML_AZUL, hover_color="#FFD740",
            text_color="#0A1628", corner_radius=50,
            command=realizar_cadastro
        ).pack(pady=(10, 6))

        ctk.CTkButton(
            cad_frame, text="← Voltar ao login",
            width=320, height=36,
            font=("Trebuchet MS", 12),
            fg_color="transparent", text_color="#7F8C8D",
            hover_color="#1E2D4A", corner_radius=50,
            command=self.tela_login
        ).pack(pady=(0, 15))

    def tela_principal(self, perfil):
        self.perfil_atual = perfil
        
        # Se um entregador tentar acessar a tela principal, redireciona
        if perfil == "Entregador":
            self.tela_entrega_v2()
            return

        # Se não for entrega, continua o código normal do PCP
        self.top_bar = ctk.CTkFrame(self, height=72, fg_color="#162040", corner_radius=0)
        self.top_bar.pack(fill="x")
        
        ctk.CTkButton(self.top_bar, text="☰", width=50, height=50, fg_color="transparent", text_color="#E6EDF3", font=("Trebuchet MS", 24, "bold"), command=self.toggle_sidebar).pack(side="left", padx=10)
        ctk.CTkLabel(self.top_bar, text="LogiStock PRO", font=("Trebuchet MS", 22, "bold"), text_color="#E6EDF3").pack(side="left", padx=10)
        self.lbl_stats = ctk.CTkLabel(self.top_bar, text="", font=("Trebuchet MS", 11, "bold"), text_color="#E6EDF3"); self.lbl_stats.pack(side="left", padx=20)
        self.entrada_pesquisa = ctk.CTkEntry(self.top_bar, placeholder_text="Pesquisar por OP ou Cliente...", width=300, height=35); self.entrada_pesquisa.pack(side="left", padx=(50, 5))
        self.entrada_pesquisa.bind("<KeyRelease>", lambda event: self.atualizar_interface(self.entrada_pesquisa.get()))
        self.filtro_var = ctk.StringVar(value="Padrão")
        self.menu_filtro = ctk.CTkOptionMenu(
            self.top_bar,
            variable=self.filtro_var,
            values=["Padrão", "A a Z", "Z a A", "Alfabética", "Data", "OP"],
            width=120,
            height=35,
            fg_color="#1E3A5F",
            button_color="#162040",
            button_hover_color="#1E2D4A",
            text_color="#E6EDF3",
            dropdown_fg_color="#162040",
            dropdown_hover_color="#1E2D4A",
            dropdown_text_color="#E6EDF3",
            corner_radius=10,
            command=lambda _: self.atualizar_interface(self.entrada_pesquisa.get())
        )
        self.menu_filtro.pack(side="left", padx=(0, 10))
        ctk.CTkButton(self.top_bar, text="SAIR", fg_color="transparent", text_color="#E6EDF3", width=70, command=self.desligar_sistema).pack(side="right", padx=20)
        ctk.CTkButton(self.top_bar, text="TROCAR CONTA", fg_color="transparent", text_color="#E6EDF3", width=100, command=self.trocar_conta).pack(side="right", padx=10)
        ctk.CTkButton(self.top_bar, text="🌓", width=40, fg_color="transparent", text_color="#E6EDF3", command=self.alternar_tema).pack(side="right")
        if perfil == "PCP": ctk.CTkButton(self.top_bar, text="+ NOVA ORDEM", fg_color=ML_AZUL, text_color="#0A1628", font=("Trebuchet MS", 12, "bold"), corner_radius=50, height=36, command=self.abrir_cadastro).pack(side="right", padx=10)
        
        self.sidebar_frame = ctk.CTkFrame(self, width=280, height=1200, fg_color="#162040", border_width=1, border_color="#1E3A5F"); self.sidebar_frame.place(x=-260, y=70)
        menu_itens = [("Painel Kanban", lambda: [self.fechar_telas_adicionais(), self.toggle_sidebar()]), ("Tabela de Pedidos", self.tela_tabela), ("Calcular Frete", self.tela_frete), ("Rastreamento", self.tela_rastreio), ("Histórico de Logs", self.tela_logs)]
        for t, c in menu_itens:
            ctk.CTkButton(self.sidebar_frame, text=t, fg_color="transparent", text_color=ML_TEXTO, anchor="w", command=c).pack(fill="x", padx=10, pady=5)

        self.kanban_container = ctk.CTkFrame(self, fg_color="transparent"); self.kanban_container.pack(fill="both", expand=True, padx=15, pady=15)
        self.column_frames = {}
        for col in ["A Fazer", "Em Andamento", "Qualidade", "Finalizado"]:
            cw = ctk.CTkFrame(self.kanban_container, fg_color="#162040", corner_radius=14, border_width=1, border_color="#1E3A5F"); cw.pack(side="left", fill="both", expand=True, padx=8)
            h = ctk.CTkFrame(cw, fg_color="#0A1628", height=44, corner_radius=10); h.pack(fill="x", padx=4, pady=(4,0))
            ctk.CTkLabel(h, text=col.upper(), font=("Trebuchet MS", 12, "bold"), text_color="#F5C518").pack(pady=10)
            f = ctk.CTkScrollableFrame(cw, fg_color="transparent"); f.pack(fill="both", expand=True, padx=2, pady=5)
            self.column_frames[col] = f
        self.atualizar_interface()

    # --- LÓGICA DE INTERFACE ---
    def atualizar_interface(self, termo=""):
        for f in self.column_frames.values():
            for w in f.winfo_children(): w.destroy()
            
        conn = sqlite3.connect("producao.db"); cur = conn.cursor()
        cur.execute("SELECT status, COUNT(*) FROM pedidos GROUP BY status"); stats = dict(cur.fetchall())
        self.lbl_stats.configure(text=f"A Fazer: {stats.get('A Fazer', 0)} | Produção: {stats.get('Em Andamento', 0)} | Pronto: {stats.get('Finalizado', 0)}")
        
        filtro = getattr(self, 'filtro_var', None)
        filtro_val = filtro.get() if filtro else "Padrão"

        ordem_map = {
            "Padrão":     "CASE WHEN prioridade = 'Urgente' THEN 0 ELSE 1 END, id ASC",
            "A a Z":      "cliente ASC",
            "Z a A":      "cliente DESC",
            "Alfabética": "produto ASC",
            "Data":       "id DESC",
            "OP":         "CAST(numero AS INTEGER) ASC, numero ASC",
        }
        ordem_sql = ordem_map.get(filtro_val, "id ASC")

        if termo == "":
            cur.execute(f"SELECT * FROM pedidos ORDER BY {ordem_sql}")
        else:
            cur.execute(f"SELECT * FROM pedidos WHERE numero LIKE ? OR cliente LIKE ? ORDER BY {ordem_sql}", (f'%{termo}%', f'%{termo}%'))
        
        # --- AQUI COMEÇA A SUBSTITUIÇÃO ---
        for p in cur.fetchall():
            status_db = p[10] # Status real do banco
            
            # Agrupa os status de entrega na última coluna do Kanban
            if status_db in ["Finalizado", "Em Rota", "Entregue"]:
                status_destino = "Finalizado"
            else:
                status_destino = status_db

            if status_destino in self.column_frames:
                # Cria o card na coluna de destino (Finalizado)
# Exemplo de como deve estar o card para aceitar o tema escuro
                card = ctk.CTkFrame(
                    self.column_frames[status_destino], 
                    fg_color="#0A1628",          
                    corner_radius=12, 
                    border_width=1, 
                    border_color="#1E3A5F"  
                    )                
                card.pack(fill="x", padx=5, pady=6)

                # --- INDICADORES VISUAIS DE ENTREGA (O "PULO DO GATO") ---
                if status_db == "Em Rota":
                    ctk.CTkLabel(card, text="EM ROTA", font=("Trebuchet MS", 9, "bold"), fg_color="#F39C12", text_color="white", corner_radius=5, width=70).pack(anchor="e", padx=10, pady=5)
                elif status_db == "Entregue":
                    ctk.CTkLabel(card, text="ENTREGUE", font=("Trebuchet MS", 9, "bold"), fg_color=ML_VERDE, text_color="white", corner_radius=5, width=70).pack(anchor="e", padx=10, pady=5)
                elif p[9] == "Urgente":
                    ctk.CTkLabel(card, text="URGENTE", font=("Trebuchet MS", 9, "bold"), fg_color=ML_VERMELHO, text_color="white", corner_radius=5, width=65).pack(anchor="e", padx=10, pady=5)

                # --- CONTEÚDO DO CARD (Igual ao que você já tinha) ---
                ctk.CTkLabel(card, text=f"OP: {p[1]}", font=("Trebuchet MS", 15, "bold"), text_color=ML_AZUL).pack(anchor="w", padx=10, pady=(5,0))
                ctk.CTkLabel(card, text=f"{p[2]} | Qtd: {p[3]}", font=("Trebuchet MS", 12), text_color=ML_TEXTO).pack(anchor="w", padx=10)
                
                bf = ctk.CTkFrame(card, fg_color="transparent"); bf.pack(fill="x", pady=10)
                ctk.CTkButton(bf, text="VER", width=50, height=26, fg_color=("#F0F0F0", "#3D3D3D"), text_color=ML_AZUL, command=lambda ped=p: self.ver_detalhes(ped)).pack(side="left", padx=5)
                ctk.CTkButton(bf, text="PDF", width=50, height=26, fg_color=ML_VERMELHO, command=lambda ped=p: self.gerar_pdf_simples(ped)).pack(side="left", padx=2)
                
                # Só mostra o botão "Avançar" se for PCP e o pedido ainda estiver em "A Fazer", "Em Andamento" ou "Qualidade"
                if status_db not in ["Finalizado", "Em Rota", "Entregue"] and self.perfil_atual == "PCP":
                    ctk.CTkButton(bf, text="AVANÇAR →", width=85, height=26, fg_color=ML_AZUL, text_color="#0A1628", font=("Trebuchet MS", 11, "bold"), corner_radius=50, command=lambda i=p[0], s=status_db, n=p[1]: self.mover_db(i, s, n)).pack(side="right", padx=5)
                
                # Se estiver em qualquer fase de finalização, mostra o botão de remover
                if status_destino == "Finalizado" and self.perfil_atual in ["PCP", "Gestão"]:
                    ctk.CTkButton(card, text="Remover Registro", height=18, fg_color="transparent", text_color="#999", font=("Trebuchet MS", 9), command=lambda i=p[0], n=p[1]: self.excluir_pedido(i, n)).pack(pady=5)
        # --- AQUI TERMINA A SUBSTITUIÇÃO ---
        conn.close()

    # --- FUNÇÕES DE BANCO NO MIXIN (OPERACIONAL) ---
    def mover_db(self, id_p, status_atual, num_op=None):
        fluxo = ["A Fazer", "Em Andamento", "Qualidade", "Finalizado"]
        try:
            n = fluxo[fluxo.index(status_atual) + 1]; conn = sqlite3.connect("producao.db"); cur = conn.cursor()
            cur.execute("UPDATE pedidos SET status = ? WHERE id = ?", (n, id_p)); conn.commit(); conn.close()
            if num_op: registrar_log(f"OP {num_op} avançou para {n}")
            self.atualizar_interface()
        except: pass

    def excluir_pedido(self, id_p, num_op=None):
        if messagebox.askyesno("Excluir", "Deseja remover permanentemente?"):
            conn = sqlite3.connect("producao.db"); cur = conn.cursor(); cur.execute("DELETE FROM pedidos WHERE id = ?", (id_p,)); conn.commit(); conn.close()
            if num_op: registrar_log(f"OP {num_op} excluída.")
            self.atualizar_interface()

    # --- TELAS SECUNDÁRIAS ---
    def tela_logs(self):
        self.toggle_sidebar(); self.fechar_telas_adicionais()
        self.logs_container = ctk.CTkFrame(self, fg_color=ML_CINZA_FUNDO); self.logs_container.place(relx=0, rely=0.07, relwidth=1, relheight=0.93)
        ctk.CTkLabel(self.logs_container, text="AUDITORIA", font=("Trebuchet MS", 24, "bold"), text_color=ML_AZUL).pack(pady=20)
        f_logs = ctk.CTkScrollableFrame(self.logs_container, width=820, height=500, fg_color="#162040", corner_radius=14, border_width=1, border_color="#1E3A5F"); f_logs.pack(pady=10)
        conn = sqlite3.connect("producao.db"); cur = conn.cursor(); cur.execute("SELECT data_hora, acao FROM logs ORDER BY id DESC"); logs = cur.fetchall(); conn.close()
        for d, a in logs: ctk.CTkLabel(f_logs, text=f"[{d}] - {a}", font=("Consolas", 12), text_color="#E6EDF3").pack(anchor="w", padx=10)
        ctk.CTkButton(self.logs_container, text="VOLTAR", command=self.fechar_telas_adicionais).pack(pady=20)

    def tela_tabela(self):
        self.toggle_sidebar(); self.fechar_telas_adicionais()
        self.tabela_container = ctk.CTkFrame(self, fg_color=ML_CINZA_FUNDO); self.tabela_container.place(relx=0, rely=0.07, relwidth=1, relheight=0.93)
        ctk.CTkButton(self.tabela_container, text="EXCEL", fg_color=ML_VERDE, command=self.exportar_excel).pack(pady=10)
        tf = ctk.CTkFrame(self.tabela_container, fg_color="#162040"); tf.pack(fill="both", expand=True, padx=30, pady=10)
        cols = ("ID", "Nº OP", "Produto", "Qtd", "Cliente", "Bairro", "Status")
        self.tree = ttk.Treeview(tf, columns=cols, show="headings")
        for col in cols: self.tree.heading(col, text=col); self.tree.column(col, anchor="center")
        self.tree.pack(fill="both", expand=True); self.carregar_dados_tabela()
        ctk.CTkButton(self.tabela_container, text="VOLTAR", command=self.fechar_telas_adicionais).pack(pady=20)

    def carregar_dados_tabela(self):
        for i in self.tree.get_children(): self.tree.delete(i)
        conn = sqlite3.connect("producao.db"); cur = conn.cursor(); cur.execute("SELECT id, numero, produto, quantidade, cliente, bairro, status FROM pedidos"); [self.tree.insert("", "end", values=r) for r in cur.fetchall()]; conn.close()

    def buscar_cep_api(self, cep, campos):
        """Consulta ViaCEP e preenche rua e bairro automaticamente."""
        import urllib.request
        import json
        cep_limpo = cep.replace("-", "").replace(".", "").strip()
        if len(cep_limpo) != 8 or not cep_limpo.isdigit():
            return
        try:
            url = f"https://viacep.com.br/ws/{cep_limpo}/json/"
            with urllib.request.urlopen(url, timeout=5) as resp:
                dados = json.loads(resp.read().decode())
            if "erro" in dados:
                messagebox.showwarning("CEP não encontrado", f"CEP {cep} não localizado na base do ViaCEP.")
                return
            # Preenche rua se estiver vazio
            if dados.get("logradouro"):
                campos["Rua"].delete(0, "end")
                campos["Rua"].insert(0, dados["logradouro"])
            # Preenche bairro se estiver vazio
            if dados.get("bairro"):
                campos["Bairro"].delete(0, "end")
                campos["Bairro"].insert(0, dados["bairro"])
        except Exception:
            pass  # Silencia erros de rede; usuário pode preencher manualmente

    def abrir_cadastro(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Nova Ordem de Produção")
        dialog.geometry("520x780")
        dialog.resizable(False, False)
        dialog.configure(fg_color="#0A1628")
        dialog.attributes("-topmost", True)

        # ── Cabeçalho ──────────────────────────────────────────────────────────
        header = ctk.CTkFrame(dialog, fg_color="#162040", corner_radius=0, height=60)
        header.pack(fill="x")
        header.pack_propagate(False)
        ctk.CTkLabel(
            header,
            text="＋  NOVA ORDEM DE PRODUÇÃO",
            font=("Trebuchet MS", 16, "bold"),
            text_color="#F5C518"
        ).pack(side="left", padx=20, pady=15)

        # ── Área rolável ───────────────────────────────────────────────────────
        scroll = ctk.CTkScrollableFrame(dialog, fg_color="#0A1628")
        scroll.pack(fill="both", expand=True, padx=0, pady=0)

        def secao(pai, titulo):
            """Cria um card de seção com título."""
            card = ctk.CTkFrame(pai, fg_color="#162040", corner_radius=12,
                                border_width=1, border_color="#1E3A5F")
            card.pack(fill="x", padx=18, pady=(12, 0))
            ctk.CTkLabel(
                card,
                text=f"  {titulo}",
                font=("Trebuchet MS", 11, "bold"),
                text_color="#8896AB",
                anchor="w"
            ).pack(fill="x", padx=4, pady=(10, 4))
            sep = ctk.CTkFrame(card, fg_color="#1E3A5F", height=1, corner_radius=0)
            sep.pack(fill="x", padx=8, pady=(0, 8))
            return card

        def campo(pai, label, placeholder, largura=420):
            """Cria label + entry empilhados."""
            wrap = ctk.CTkFrame(pai, fg_color="transparent")
            wrap.pack(fill="x", padx=14, pady=(0, 8))
            ctk.CTkLabel(wrap, text=label, font=("Trebuchet MS", 11),
                         text_color="#B8C5D6", anchor="w").pack(anchor="w")
            ent = ctk.CTkEntry(wrap, placeholder_text=placeholder, width=largura,
                               height=36, corner_radius=8,
                               border_color="#1E3A5F", border_width=1)
            ent.pack(anchor="w")
            return ent

        # ── Seção 1: Dados da OP ───────────────────────────────────────────────
        card_op = secao(scroll, "📋  DADOS DA ORDEM")
        row1 = ctk.CTkFrame(card_op, fg_color="transparent")
        row1.pack(fill="x", padx=14, pady=(0, 8))

        ctk.CTkLabel(row1, text="Nº da OP  *", font=("Trebuchet MS", 11),
                     text_color="#B8C5D6").grid(row=0, column=0, sticky="w", padx=(0, 16))
        ctk.CTkLabel(row1, text="Quantidade  *", font=("Trebuchet MS", 11),
                     text_color="#B8C5D6").grid(row=0, column=1, sticky="w")

        ent_op  = ctk.CTkEntry(row1, placeholder_text="Ex: 1042", width=190, height=36,
                               corner_radius=8, border_color="#1E3A5F", border_width=1)
        ent_op.grid(row=1, column=0, sticky="w", padx=(0, 16), pady=(2, 0))

        ent_qtd = ctk.CTkEntry(row1, placeholder_text="Ex: 50", width=190, height=36,
                               corner_radius=8, border_color="#1E3A5F", border_width=1)
        ent_qtd.grid(row=1, column=1, sticky="w", pady=(2, 0))

        ent_prod = campo(card_op, "Produto  *", "Nome do produto ou referência")

        # ── Seção 2: Dados do Cliente ─────────────────────────────────────────
        card_cli = secao(scroll, "👤  DADOS DO CLIENTE")
        ent_cli = campo(card_cli, "Nome do Cliente  *", "Razão social ou nome completo")

        # ── Seção 3: Endereço com ViaCEP ─────────────────────────────────────
        card_end = secao(scroll, "📍  ENDEREÇO DE ENTREGA")

        # Status do CEP (feedback visual)
        lbl_cep_status = ctk.CTkLabel(card_end, text="", font=("Trebuchet MS", 10),
                                      text_color="#2ecc71", anchor="w")
        lbl_cep_status.pack(fill="x", padx=14)

        # Linha CEP + Nº
        row_cep = ctk.CTkFrame(card_end, fg_color="transparent")
        row_cep.pack(fill="x", padx=14, pady=(0, 8))

        ctk.CTkLabel(row_cep, text="CEP  *", font=("Trebuchet MS", 11),
                     text_color="#B8C5D6").grid(row=0, column=0, sticky="w", padx=(0, 16))
        ctk.CTkLabel(row_cep, text="Nº da Casa  *", font=("Trebuchet MS", 11),
                     text_color="#B8C5D6").grid(row=0, column=1, sticky="w")

        ent_cep = ctk.CTkEntry(row_cep, placeholder_text="00000-000", width=190, height=36,
                               corner_radius=8, border_color="#1E3A5F", border_width=1)
        ent_cep.grid(row=1, column=0, sticky="w", padx=(0, 16), pady=(2, 0))

        ent_casa = ctk.CTkEntry(row_cep, placeholder_text="Ex: 123 / S/N", width=190, height=36,
                                corner_radius=8, border_color="#1E3A5F", border_width=1)
        ent_casa.grid(row=1, column=1, sticky="w", pady=(2, 0))

        # Rua (preenchida pelo ViaCEP)
        wrap_rua = ctk.CTkFrame(card_end, fg_color="transparent")
        wrap_rua.pack(fill="x", padx=14, pady=(0, 8))
        ctk.CTkLabel(wrap_rua, text="Rua  *  (preenchida automaticamente pelo CEP)",
                     font=("Trebuchet MS", 11), text_color="#B8C5D6", anchor="w").pack(anchor="w")
        ent_rua = ctk.CTkEntry(wrap_rua, placeholder_text="Aguardando CEP...", width=420,
                               height=36, corner_radius=8,
                               border_color="#1E3A5F", border_width=1)
        ent_rua.pack(anchor="w")

        # Bairro (preenchido pelo ViaCEP)
        wrap_bairro = ctk.CTkFrame(card_end, fg_color="transparent")
        wrap_bairro.pack(fill="x", padx=14, pady=(0, 12))
        ctk.CTkLabel(wrap_bairro, text="Bairro  *  (preenchido automaticamente pelo CEP)",
                     font=("Trebuchet MS", 11), text_color="#B8C5D6", anchor="w").pack(anchor="w")
        ent_bairro = ctk.CTkEntry(wrap_bairro, placeholder_text="Aguardando CEP...", width=420,
                                  height=36, corner_radius=8,
                                  border_color="#1E3A5F", border_width=1)
        ent_bairro.pack(anchor="w")

        # Monta o dicionário de campos igual ao padrão salvar()
        campos = {
            "OP":     ent_op,
            "Prod":   ent_prod,
            "Qtd":    ent_qtd,
            "Cli":    ent_cli,
            "Rua":    ent_rua,
            "Nº":     ent_casa,
            "Bairro": ent_bairro,
            "CEP":    ent_cep,
        }

        def ao_sair_cep(event):
            cep_val = ent_cep.get().strip()
            if not cep_val:
                return
            lbl_cep_status.configure(text="🔎 Buscando CEP...", text_color="#F5C518")
            dialog.update_idletasks()

            import urllib.request, json as _json
            cep_limpo = cep_val.replace("-", "").replace(".", "")
            try:
                url = f"https://viacep.com.br/ws/{cep_limpo}/json/"
                with urllib.request.urlopen(url, timeout=5) as resp:
                    dados = _json.loads(resp.read().decode())
                if "erro" in dados:
                    lbl_cep_status.configure(text="⚠  CEP não encontrado", text_color="#e74c3c")
                    return
                if dados.get("logradouro"):
                    ent_rua.delete(0, "end"); ent_rua.insert(0, dados["logradouro"])
                if dados.get("bairro"):
                    ent_bairro.delete(0, "end"); ent_bairro.insert(0, dados["bairro"])
                lbl_cep_status.configure(
                    text=f"✔  Endereço encontrado — {dados.get('localidade','')}/{dados.get('uf','')}",
                    text_color="#2ecc71"
                )
            except Exception:
                lbl_cep_status.configure(text="⚠  Erro de conexão — preencha manualmente", text_color="#e74c3c")

        ent_cep.bind("<FocusOut>", ao_sair_cep)

        # ── Seção 4: Prioridade e Observações ────────────────────────────────
        card_obs = secao(scroll, "⚑  PRIORIDADE E OBSERVAÇÕES")

        ctk.CTkLabel(card_obs, text="Prioridade", font=("Trebuchet MS", 11),
                     text_color="#B8C5D6").pack(anchor="w", padx=14)
        pri_var = ctk.StringVar(value="Normal")
        ctk.CTkSegmentedButton(
            card_obs, variable=pri_var,
            values=["Normal", "Urgente"],
            selected_color="#e74c3c",
            selected_hover_color="#c0392b",
            unselected_color="#1E2D4A",
            text_color="#E6EDF3",
            width=420
        ).pack(padx=14, pady=(4, 10))

        ctk.CTkLabel(card_obs, text="Observações", font=("Trebuchet MS", 11),
                     text_color="#B8C5D6").pack(anchor="w", padx=14)
        desc_txt = ctk.CTkTextbox(card_obs, width=420, height=90, corner_radius=8,
                                  border_width=1, border_color="#1E3A5F",
                                  fg_color="#0A1628")
        desc_txt.pack(padx=14, pady=(4, 14))

        # ── Rodapé com botões ─────────────────────────────────────────────────
        ctk.CTkFrame(scroll, fg_color="transparent", height=8).pack()  # espaço

        btn_row = ctk.CTkFrame(scroll, fg_color="transparent")
        btn_row.pack(fill="x", padx=18, pady=(0, 20))

        ctk.CTkButton(
            btn_row, text="CANCELAR", width=180, height=42,
            fg_color="transparent", border_width=1, border_color="#1E3A5F",
            text_color="#B8C5D6", hover_color="#1E2D4A", corner_radius=50,
            command=dialog.destroy
        ).pack(side="left")

        def salvar():
            # Validação básica
            obrigatorios = [("OP", "Nº da OP"), ("Prod", "Produto"),
                            ("Qtd", "Quantidade"), ("Cli", "Cliente"),
                            ("CEP", "CEP"), ("Nº", "Nº da Casa")]
            for chave, nome in obrigatorios:
                if not campos[chave].get().strip():
                    messagebox.showwarning("Campo obrigatório", f"Preencha o campo: {nome}")
                    campos[chave].focus()
                    return
            conn = sqlite3.connect("producao.db")
            cur  = conn.cursor()
            cur.execute(
                "INSERT INTO pedidos (numero, produto, quantidade, cliente, rua, casa, bairro, cep, prioridade, status, descricao) "
                "VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                (campos["OP"].get(), campos["Prod"].get(), campos["Qtd"].get(),
                 campos["Cli"].get(), campos["Rua"].get(), campos["Nº"].get(),
                 campos["Bairro"].get(), campos["CEP"].get(),
                 pri_var.get(), "A Fazer",
                 desc_txt.get("0.0", "end").strip())
            )
            conn.commit(); conn.close()
            self.atualizar_interface()
            dialog.destroy()

        ctk.CTkButton(
            btn_row, text="✔  SALVAR ORDEM", width=230, height=42,
            fg_color="#2ecc71", hover_color="#27ae60",
            text_color="#0A1628", font=("Trebuchet MS", 13, "bold"),
            corner_radius=50, command=salvar
        ).pack(side="right")

    def ver_detalhes(self, p):
        janela = ctk.CTkToplevel(self); janela.title(f"Detalhes: {p[1]}"); janela.geometry("500x600"); janela.attributes("-topmost", True)
        ctk.CTkLabel(janela, text="DETALHES", font=("Trebuchet MS", 20, "bold"), text_color=ML_AZUL).pack(pady=20)
        txt = f"OP: {p[1]}\nProduto: {p[2]}\nQtd: {p[3]}\nCliente: {p[4]}\nEndereço: {p[5]}, {p[6]} - {p[7]}\nCEP: {p[8]}\nPrioridade: {p[9]}"
        ctk.CTkLabel(janela, text=txt, justify="left", font=("Trebuchet MS", 13)).pack(pady=10, padx=20, anchor="w")
        desc = ctk.CTkTextbox(janela, width=420, height=150, border_width=1); desc.pack(pady=10); desc.insert("0.0", str(p[11]) if p[11] else "Sem descrição."); desc.configure(state="disabled")
        ctk.CTkButton(janela, text="FECHAR", command=janela.destroy).pack(pady=20)

    def tela_frete(self):
        self.toggle_sidebar(); self.fechar_telas_adicionais()
        self.frete_container = ctk.CTkFrame(self, fg_color=ML_CINZA_FUNDO); self.frete_container.place(relx=0, rely=0.07, relwidth=1, relheight=0.93)
        ctk.CTkLabel(self.frete_container, text="CÁLCULO DE FRETE", font=("Trebuchet MS", 24, "bold"), text_color=ML_AZUL).pack(pady=30)
        card = ctk.CTkFrame(self.frete_container, fg_color="#162040", width=470, height=500, corner_radius=16, border_width=1, border_color="#1E3A5F"); card.pack(pady=10); card.pack_propagate(False)
        ctk.CTkLabel(card, text="CEP de Origem:", text_color=ML_TEXTO).pack(pady=(20, 0))
        ctk.CTkEntry(card, width=300, placeholder_text="00000-000").pack(pady=5)
        ctk.CTkLabel(card, text="CEP de Destino:", text_color=ML_TEXTO).pack(pady=(10, 0))
        ctk.CTkEntry(card, width=300, placeholder_text="00000-000").pack(pady=5)
        ctk.CTkLabel(card, text="Peso (kg):", text_color=ML_TEXTO).pack(pady=(10, 0))
        ent_peso = ctk.CTkEntry(card, width=300, placeholder_text="Ex: 10.5"); ent_peso.pack(pady=5)
        lbl_res = ctk.CTkLabel(card, text="", font=("Trebuchet MS", 18, "bold"), text_color=ML_VERDE); lbl_res.pack(pady=20)
        
        def calcular():
            try: v = float(ent_peso.get().replace(",", ".")) * 12.5; lbl_res.configure(text=f"Valor Estimado: R$ {v:.2f}")
            except: messagebox.showwarning("Erro", "Insira um peso válido")
        ctk.CTkButton(card, text="CALCULAR", fg_color=ML_AZUL, height=45, width=300, command=calcular).pack(pady=10)
        ctk.CTkButton(card, text="VOLTAR", fg_color="transparent", text_color=ML_TEXTO, command=self.fechar_telas_adicionais).pack()

    def exportar_excel(self):
        try:
            import pandas as pd
            import sqlite3
            import os

            # 1. Busca os dados
            conn = sqlite3.connect(DB_PATH)
            df = pd.read_sql_query("SELECT * FROM pedidos", conn)
            conn.close()

            # 2. Define o caminho da pasta separada
            pasta_export = os.path.join(os.path.dirname(os.path.abspath(__file__)), "arquivos_exportados")
            if not os.path.exists(pasta_export): os.makedirs(pasta_export)
            
            caminho_excel = os.path.join(pasta_export, "Relatorio_Pedidos.xlsx")

            # 3. Salva
            df.to_excel(caminho_excel, index=False)
            
            messagebox.showinfo("Sucesso", f"Excel gerado em:\n{caminho_excel}")
            os.startfile(pasta_export) # Abre a pasta para você ver o arquivo

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao gerar Excel: {e}")

    def tela_rastreio(self):
        self.toggle_sidebar(); self.fechar_telas_adicionais()
        self.rastreio_container = ctk.CTkFrame(self, fg_color=ML_CINZA_FUNDO); self.rastreio_container.place(relx=0, rely=0.07, relwidth=1, relheight=0.93)
        ctk.CTkLabel(self.rastreio_container, text="RASTREAMENTO DE CARGA", font=("Trebuchet MS", 24, "bold"), text_color=ML_AZUL).pack(pady=30)
        card = ctk.CTkFrame(self.rastreio_container, fg_color="#162040", width=520, height=450, corner_radius=16, border_width=1, border_color="#1E3A5F"); card.pack(pady=10); card.pack_propagate(False)
        ent_cod = ctk.CTkEntry(card, width=350, placeholder_text="Digite o número da OP"); ent_cod.pack(pady=30)
        lbl_res = ctk.CTkLabel(card, text="Aguardando consulta...", font=("Trebuchet MS", 14), text_color=ML_TEXTO); lbl_res.pack(pady=20)

        # --- ESSA É A FUNÇÃO QUE VOCÊ ALTERA ---
        def buscar():
            conn = sqlite3.connect("producao.db")
            cur = conn.cursor()
            cur.execute("SELECT status, cliente, produto FROM pedidos WHERE numero = ?", (ent_cod.get(),))
            r = cur.fetchone()
            conn.close()

            if r:
                status_txt = r[0]
                cor = ML_AZUL
                
                # Lógica de tradução de status para o usuário
                if status_txt == "Em Rota": 
                    status_txt = "SAIU PARA ENTREGA"
                    cor = "#f39c12" # Laranja
                elif status_txt == "Entregue": 
                    status_txt = "ENTREGUE AO CLIENTE"
                    cor = ML_VERDE # Verde
                elif status_txt == "Finalizado":
                    status_txt = "PRONTO PARA COLETA"
                    cor = ML_AZUL

                lbl_res.configure(text=f"Produto: {r[2]}\nStatus: {status_txt}\nCliente: {r[1]}", text_color=cor)
            else:
                lbl_res.configure(text="OP não encontrada!", text_color=ML_VERMELHO)
        # ---------------------------------------

        ctk.CTkButton(card, text="RASTREAR", fg_color=ML_AZUL, height=45, width=200, command=buscar).pack(pady=10)
        ctk.CTkButton(card, text="VOLTAR", fg_color="transparent", text_color=ML_TEXTO, command=self.fechar_telas_adicionais).pack()
        
        # --- NOVOS MÉTODOS PARA O ENTREGADOR ---
    def tela_entrega_v2(self):
        # Header minimalista (Sem menu lateral)
        header = ctk.CTkFrame(self, height=72, fg_color="#162040", corner_radius=0)
        header.pack(fill="x")
        
        ctk.CTkLabel(header, text="PAINEL DE LOGÍSTICA", font=("Trebuchet MS", 18, "bold"), text_color="#F5C518").pack(side="left", padx=20)
        
        ctk.CTkButton(header, text="SAIR", width=60, fg_color="#cc0000", command=self.desligar_sistema).pack(side="right", padx=10)
        ctk.CTkButton(header, text="TROCAR CONTA", width=110, fg_color="transparent", border_width=1, border_color="#1E3A5F", text_color="#B8C5D6", hover_color="#1E2D4A", corner_radius=50, command=self.trocar_conta).pack(side="right", padx=10)

        # Container da lista
        self.scroll_entrega = ctk.CTkScrollableFrame(self, fg_color="#0A1628")
        self.scroll_entrega.pack(fill="both", expand=True, padx=10, pady=10)
        self.atualizar_lista_entrega()

    def atualizar_lista_entrega(self):
        for w in self.scroll_entrega.winfo_children(): w.destroy()
        
        conn = sqlite3.connect("producao.db")
        cur = conn.cursor()
        # Busca pedidos prontos ou em transporte
        cur.execute("SELECT id, numero, produto, cliente, status, bairro FROM pedidos WHERE status IN ('Finalizado', 'Em Rota', 'Entregue')")
        pedidos = cur.fetchall()
        
        for p in pedidos:
            card = ctk.CTkFrame(self.scroll_entrega, fg_color="#162040", corner_radius=12, border_width=1, border_color="#1E3A5F")
            card.pack(fill="x", pady=8, padx=15)
            
            info = ctk.CTkFrame(card, fg_color="transparent")
            info.pack(side="left", padx=15, pady=10)
            
            ctk.CTkLabel(info, text=f"OP: {p[1]}", font=("Trebuchet MS", 15, "bold"), text_color=ML_AZUL).pack(anchor="w")
            ctk.CTkLabel(info, text=f"Entregar para: {p[3]}", font=("Trebuchet MS", 12, "bold"), text_color="#E6EDF3").pack(anchor="w")
            ctk.CTkLabel(info, text=f"Bairro: {p[5]}", font=("Trebuchet MS", 12), text_color="#8896AB").pack(anchor="w")
            
            # Botões de Status (Estilo Shopee)
            btn_area = ctk.CTkFrame(card, fg_color="transparent")
            btn_area.pack(side="right", padx=15)

            if p[4] == "Finalizado":
                ctk.CTkButton(btn_area, text="SAIR PARA ENTREGA", fg_color=ML_AZUL, command=lambda i=p[0], n=p[1]: self.mudar_status_entregador(i, "Em Rota", n)).pack()
            elif p[4] == "Em Rota":
                ctk.CTkButton(btn_area, text="MARCAR COMO ENTREGUE", fg_color=ML_VERDE, command=lambda i=p[0], n=p[1]: self.mudar_status_entregador(i, "Entregue", n)).pack()
            else:
                ctk.CTkLabel(btn_area, text="ENTREGUE", text_color=ML_VERDE, font=("Trebuchet MS", 12, "bold")).pack()
        conn.close()

    def mudar_status_entregador(self, id_p, novo, op):
        conn = sqlite3.connect("producao.db"); cur = conn.cursor()
        cur.execute("UPDATE pedidos SET status = ? WHERE id = ?", (novo, id_p))
        conn.commit(); conn.close()
        registrar_log(f"OP {op} atualizada para {novo} pelo entregador.")
        self.atualizar_lista_entrega()