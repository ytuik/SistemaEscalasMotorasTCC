import os
import customtkinter as ctk
from customtkinter import filedialog
import tkinter.messagebox as messagebox
from datetime import date
from typing import Callable, Optional
import logging

from sqlalchemy.orm import Session

# Importações do Backend
from app.database import Base, engine, get_session, DB_PATH
from app.models.paciente import Paciente
from app.services.fisioterapeuta_service import listar_fisioterapeutas
from app.services.template_service import iniciar_avaliacao_xlsx
from app.services.planilha_service import importar_planilha_avaliacao
from app.services.paciente_service import obter_pacientes_por_nome, perfil_completo, listar_pacientes, resumo_executivo
from app.exceptions import PacienteNaoEncontradoError
from scripts.seed import popular_escalas


logger = logging.getLogger(__name__)

# Configuração visual do CustomTkinter
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

# ==================== UI CONFIGURATION ====================
class UIConfig:
    """Centraliza constantes de UI para fácil manutenção"""
    WINDOW_SIZE = (1100, 700)
    SIDEBAR_WIDTH = 250

    # Colors
    NAV_BUTTON_TEXT = ("gray10", "gray90")
    NAV_BUTTON_HOVER = ("gray70", "gray30")

    # Button defaults (fonts created after root window exists)
    @staticmethod
    def get_nav_button_config():
        return {
            "fg_color": "transparent",
            "text_color": UIConfig.NAV_BUTTON_TEXT,
            "hover_color": UIConfig.NAV_BUTTON_HOVER
        }

    @staticmethod
    def get_fonts():
        """Retorna dicionário com fonts (criados após window root)"""
        return {
            "title": ctk.CTkFont(size=20, weight="bold"),
            "section": ctk.CTkFont(size=12, weight="bold"),
            "body": ctk.CTkFont(size=10),
        }

# ==================== MAIN APPLICATION ====================
class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.frames={}
        
        self.title("Sistema de Avaliação Motora - Gestão Clínica")
        self.geometry(f"{UIConfig.WINDOW_SIZE[0]}x{UIConfig.WINDOW_SIZE[1]}")

        # Inicializar fonts após criar a janela root
        self.fonts = UIConfig.get_fonts()
        self.nav_button_config = UIConfig.get_nav_button_config()

        # Estado da aplicação
        self.current_patient_id: Optional[int] = None
        self.caminho_arquivo_importacao: Optional[str] = None

        # Setup layout
        self._setup_layout()
        self._setup_navigation()
        self._setup_frames()
        self.show_eval_gen()

    # ==================== LAYOUT SETUP ====================

    def _setup_layout(self):
        """Configuração de grid e estrutura principal"""
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

    def _setup_navigation(self):
        """Cria a barra lateral com navegação"""
        self.navigation_frame = ctk.CTkFrame(self, corner_radius=0)
        self.navigation_frame.grid(row=0, column=0, sticky="nsew")
        self.navigation_frame.grid_columnconfigure(0, weight=1)

        row = 0


        # Seção 1: Avaliações
        self._add_section_header(row, "1. AVALIAÇÕES")
        row += 1
        row = self._add_nav_buttons(row, [
            ("Gerar Template", self.show_eval_gen),
            ("Importar Planilha", self.show_eval_imp),
        ])
        
        # Seção 2: Fisioterapeutas
        self._add_section_header(row, "2. FISIOTERAPEUTAS")
        row += 1
        row = self._add_nav_buttons(row, [
            ("Listagem", self.show_fisio_list),
            ("Cadastro", self.show_fisio_cad),
        ])


        # Seção 3: Pacientes
        self._add_section_header(row, "3. PACIENTES")
        row += 1
        row = self._add_nav_buttons(row, [
            ("Listar Todos", self.show_pat_list),
        ])

    def _add_section_header(self, row: int, text: str) -> None:
        """Adiciona cabeçalho de seção"""
        lbl = ctk.CTkLabel(self.navigation_frame, text=text, font=self.fonts["section"])
        lbl.grid(row=row, column=0, padx=20, pady=(20, 0), sticky="w")

    def _add_nav_buttons(self, start_row: int, buttons: list[tuple[str, Callable]]) -> int:
        """Adiciona múltiplos botões de navegação e retorna próxima linha disponível"""
        current_row = start_row
        for text, command in buttons:
            btn = ctk.CTkButton(
                self.navigation_frame,
                text=text,
                command=command,
                **self.nav_button_config
            )
            btn.grid(row=current_row, column=0, sticky="ew", padx=10, pady=5)
            current_row += 1
        return current_row

    # ==================== FRAMES SETUP ====================

    def _setup_frames(self):
        """Inicializa todos os frames de conteúdo com segurança"""
        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)

        self.frames = {}

        self.frames["fisio_list"] = self._create_fisio_list_frame()
        self.frames["fisio_cad"] = self._create_fisio_cad_frame()
        self.frames["eval_gen"] = self._create_eval_gen_frame()
        self.frames["eval_imp"] = self._create_eval_imp_frame()
        
        self.frames["pat_list"] = self._create_pat_list_frame()
                
        self.frames["pat_detail"] = self._create_pat_detail_frame()

        for frame in self.frames.values():
            frame.pack_forget()

    def _create_fisio_list_frame(self) -> ctk.CTkFrame:
        """Frame: Listagem de Fisioterapeutas"""
        frame = ctk.CTkFrame(self.container, fg_color="transparent")
        ctk.CTkLabel(frame, text="Fisioterapeutas Cadastrados", font=self.fonts["title"]).pack(pady=10)
        self.fisio_scroll = ctk.CTkScrollableFrame(frame, width=600, height=400)
        self.fisio_scroll.pack(pady=10, fill="both", expand=True)
        return frame

    def _create_fisio_cad_frame(self) -> ctk.CTkFrame:
        """Frame: Cadastro de Fisioterapeutas"""
        frame = ctk.CTkFrame(self.container, fg_color="transparent")
        ctk.CTkLabel(frame, text="Novo Cadastro de Fisioterapeuta", font=self.fonts["title"]).pack(pady=20)

        self.ent_fisio_nome = ctk.CTkEntry(frame, placeholder_text="Nome Completo", width=400)
        self.ent_fisio_nome.pack(pady=10)

        self.ent_fisio_email = ctk.CTkEntry(frame, placeholder_text="E-mail", width=400)
        self.ent_fisio_email.pack(pady=10)

        self.ent_fisio_crefito = ctk.CTkEntry(frame, placeholder_text="CREFITO", width=400)
        self.ent_fisio_crefito.pack(pady=10)

        ctk.CTkButton(frame, text="Salvar Fisioterapeuta", command=self.acao_cadastrar_fisio).pack(pady=20)
        return frame

    def _create_eval_gen_frame(self) -> ctk.CTkFrame:
        """Frame: Gerar Template Excel"""
        frame = ctk.CTkFrame(self.container, fg_color="transparent")
        ctk.CTkLabel(frame, text="Gerar Template Excel", font=self.fonts["title"]).pack(pady=20)

        self.ent_temp_paciente = ctk.CTkEntry(frame, placeholder_text="Nome do Paciente", width=400)
        self.ent_temp_paciente.pack(pady=10)

        ctk.CTkButton(frame, text="Gerar e Abrir Pasta", command=self.acao_gerar_template).pack(pady=20)
        return frame

    def _create_eval_imp_frame(self) -> ctk.CTkFrame:
        """Frame: Importar Planilha Preenchida"""
        frame = ctk.CTkFrame(self.container, fg_color="transparent")
        ctk.CTkLabel(frame, text="Importar Planilha Preenchida", font=self.fonts["title"]).pack(pady=20)

        self.lbl_file_status = ctk.CTkLabel(frame, text="Nenhum arquivo selecionado", text_color="gray")
        self.lbl_file_status.pack(pady=5)

        ctk.CTkButton(frame, text="Selecionar Arquivo", command=self.acao_selecionar_planilha).pack(pady=10)
        ctk.CTkButton(frame, text="Iniciar Importação", fg_color="green", command=self.acao_importar_planilha).pack(pady=20)
        return frame

    def _create_pat_list_frame(self) -> ctk.CTkFrame:
        """Frame: Listagem de Pacientes"""
        frame = ctk.CTkFrame(self.container, fg_color="transparent")
        ctk.CTkLabel(frame, text="Gestão de Pacientes", font=self.fonts["title"]).pack(pady=10)

        search_container = ctk.CTkFrame(frame, fg_color="transparent")
        search_container.pack(fill="x", pady=5)

        self.ent_pat_search = ctk.CTkEntry(search_container, placeholder_text="Buscar por nome...", width=400)
        self.ent_pat_search.pack(side="left", padx=10)
        ctk.CTkButton(search_container, text="Buscar", width=100, command=self.acao_buscar_paciente).pack(side="left")

        self.pat_scroll = ctk.CTkScrollableFrame(frame, width=700, height=450)
        self.pat_scroll.pack(pady=10, fill="both", expand=True)
        return frame

    def _create_pat_detail_frame(self) -> ctk.CTkFrame:
        """Frame: Perfil Detalhado do Paciente"""
        frame = ctk.CTkFrame(self.container, fg_color="transparent")

        self.lbl_pat_name = ctk.CTkLabel(frame, text="Paciente", font=ctk.CTkFont(size=22, weight="bold"))
        self.lbl_pat_name.pack(pady=20)

        # Seletor de tipo de visualização
        ctk.CTkLabel(frame, text="Selecione o tipo de visualização:").pack(pady=5)
        self.resumo_var = ctk.StringVar(value="Executivo")
        self.resumo_menu = ctk.CTkOptionMenu(
            frame,
            values=["Executivo", "Completo", "Por Escala"],
            command=self.acao_atualizar_visualizacao,
            variable=self.resumo_var
        )
        self.resumo_menu.pack(pady=10)

        # Scroll area para detalhes
        self.pat_detail_scroll = ctk.CTkScrollableFrame(frame, width=700, height=400)
        self.pat_detail_scroll.pack(pady=10, fill="both", expand=True)

        # Botões de ação
        ctk.CTkButton(frame, text="Exportar como PDF", fg_color="darkred", command=self.acao_exportar_pdf).pack(pady=40)
        ctk.CTkButton(frame, text="Voltar para Lista", fg_color="gray", command=self.show_pat_list).pack(pady=10)

        return frame

    # ==================== FRAME NAVIGATION ====================

    def _hide_all_frames(self) -> None:
        """Oculta todos os frames"""
        for frame in self.frames.values():
            frame.pack_forget()

    def _show_frame(self, name: str) -> None:
        """Exibe um frame específico"""
        self._hide_all_frames()
        if name in self.frames:
            self.frames[name].pack(fill="both", expand=True)

    def show_fisio_list(self) -> None:
        self._show_frame("fisio_list")
        self.acao_listar_fisios()

    def show_fisio_cad(self) -> None:
        self._show_frame("fisio_cad")

    def show_eval_gen(self) -> None:
        self._show_frame("eval_gen")

    def show_eval_imp(self) -> None:
        self._show_frame("eval_imp")

    def show_pat_list(self) -> None:
        self._show_frame("pat_list")
        self.acao_listar_todos_pacientes()

    # ==================== AÇÕES: FISIOTERAPEUTAS ====================

    def acao_cadastrar_fisio(self) -> None:
        """Cadastra novo fisioterapeuta"""
        nome = self.ent_fisio_nome.get().strip()
        email = self.ent_fisio_email.get().strip()
        crefito = self.ent_fisio_crefito.get().strip()

        if not all([nome, email, crefito]):
            messagebox.showwarning("Aviso", "Preencha todos os campos.")
            return

        try:
            with get_session() as session:
                from app.models.fisioterapeuta import Fisioterapeuta
                fisio = Fisioterapeuta(nome=nome, email=email, registro_crefito=crefito)
                session.add(fisio)
                session.flush()

            messagebox.showinfo("Sucesso", f"Fisioterapeuta {nome} cadastrado com sucesso!")
            self.ent_fisio_nome.delete(0, 'end')
            self.ent_fisio_email.delete(0, 'end')
            self.ent_fisio_crefito.delete(0, 'end')
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao cadastrar: {str(e)}")

    def acao_listar_fisios(self) -> None:
        """Lista todos os fisioterapeutas"""
        for widget in self.fisio_scroll.winfo_children():
            widget.destroy()

        try:
            with get_session() as session:
                fisios = listar_fisioterapeutas(session)
                if not fisios:
                    ctk.CTkLabel(self.fisio_scroll, text="Nenhum fisioterapeuta cadastrado.").pack()
                    return

                for f in fisios:
                    info = f"CREFITO: {f.registro_crefito} | Nome: {f.nome} | Email: {f.email}"
                    ctk.CTkLabel(self.fisio_scroll, text=info, anchor="w").pack(fill="x", pady=2)
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao listar fisioterapeutas: {str(e)}")

    # ==================== AÇÕES: AVALIAÇÕES ====================

    def acao_gerar_template(self) -> None:
        """Gera template Excel para avaliação"""
        nome = self.ent_temp_paciente.get().strip()
        if not nome:
            messagebox.showwarning("Aviso", "Informe o nome do paciente.")
            return

        try:
            caminho = iniciar_avaliacao_xlsx(nome_paciente=nome)
            messagebox.showinfo("Sucesso", f"Template gerado em:\n{caminho}")
            self.ent_temp_paciente.delete(0, 'end')
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao gerar template: {str(e)}")

    def acao_selecionar_planilha(self) -> None:
        """Abre diálogo para selecionar arquivo XLSX"""
        path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx")])
        if path:
            self.caminho_arquivo_importacao = path
            self.lbl_file_status.configure(text=os.path.basename(path), text_color="white")

    def acao_importar_planilha(self) -> None:
        """Importa dados da planilha selecionada"""
        if not self.caminho_arquivo_importacao:
            messagebox.showwarning("Aviso", "Selecione um arquivo primeiro.")
            return

        try:
            with get_session() as session:
                res = importar_planilha_avaliacao(session, self.caminho_arquivo_importacao)

                if res["status"] == "ok":
                    escalas = ", ".join(res.get("escalas_importadas", []))
                    messagebox.showinfo(
                        "Sucesso",
                        f"Dados importados com sucesso!\n"
                        f"Paciente: {res['paciente']}\n"
                        f"Escalas: {escalas}"
                    )
                    self.caminho_arquivo_importacao = None
                    self.lbl_file_status.configure(text="Nenhum arquivo selecionado", text_color="gray")
                else:
                    messagebox.showerror("Erro de Importação", res["mensagem"])
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao importar: {str(e)}")

    # ==================== AÇÕES: PACIENTES ====================

    def acao_listar_todos_pacientes(self) -> None:
        """Lista todos os pacientes"""
        for widget in self.pat_scroll.winfo_children():
            widget.destroy()

        try:
            with get_session() as session:
                pacientes = listar_pacientes(session)
                self._render_lista_pacientes(pacientes)
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao listar pacientes: {str(e)}")

    def acao_buscar_paciente(self) -> None:
        """Busca pacientes por nome"""
        termo = self.ent_pat_search.get().strip()
        if not termo:
            messagebox.showwarning("Aviso", "Digite um nome para buscar.")
            return

        try:
            with get_session() as session:
                pacientes = obter_pacientes_por_nome(session, termo)
                self._render_lista_pacientes(pacientes)
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao buscar: {str(e)}")

    def _render_lista_pacientes(self, lista: list[Paciente]) -> None:
        """Renderiza lista de pacientes no scroll frame"""
        for widget in self.pat_scroll.winfo_children():
            widget.destroy()

        if not lista:
            ctk.CTkLabel(self.pat_scroll, text="Nenhum paciente encontrado.").pack()
            return

        for p in lista:
            frame_item = ctk.CTkFrame(self.pat_scroll, fg_color="transparent")
            frame_item.pack(fill="x", pady=2)

            info_text = f"ID: {p.id} | {p.nome} | Nasc: {p.data_nascimento}"
            ctk.CTkLabel(frame_item, text=info_text, anchor="w").pack(side="left", padx=10, fill="x", expand=True)
            ctk.CTkButton(frame_item, text="Abrir Perfil", width=100, command=lambda pid=p.id: self.show_perfil_paciente(pid)).pack(side="right", padx=10)

    # ==================== AÇÕES: PERFIL PACIENTE ====================

    def show_perfil_paciente(self, paciente_id: int) -> None:
        """Exibe perfil detalhado do paciente"""
        self.current_patient_id = paciente_id
        self._show_frame("pat_detail")

        # Limpar conteúdo anterior
        for widget in self.pat_detail_scroll.winfo_children():
            widget.destroy()

        try:
            with get_session() as session:
                # Buscar paciente e dados
                paciente = session.get(Paciente, paciente_id)
                if not paciente:
                    messagebox.showerror("Erro", "Paciente não encontrado.")
                    return

                self.lbl_pat_name.configure(text=f"Perfil: {paciente.nome}")

            # Buscar e exibir dados do perfil
            tipo_atual = self.resumo_var.get()
            self.acao_atualizar_visualizacao(tipo_atual)

        except PacienteNaoEncontradoError:
            messagebox.showerror("Erro", "Paciente não encontrado.")
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao carregar perfil: {str(e)}")

    def _render_perfil_completo(self, perfil) -> None:
        """Renderiza dados do perfil no scroll frame com layout alinhado."""
        
        # 1. Informações Principais do Paciente
        info_text = (
            f"Nome: {perfil.nome}\n"
            f"Data de Nascimento: {perfil.data_nascimento}\n"
            f"Idade: {perfil.idade} anos\n"
            f"Data de Cadastro: {perfil.data_cadastro}\n"
            f"Total de Avaliações: {perfil.total_avaliacoes}"
        )
        ctk.CTkLabel(
            self.pat_detail_scroll, 
            text=info_text, 
            justify="left", 
            anchor="nw"
        ).pack(pady=10, fill="x")

        # 2. Histórico de Avaliações
        if not perfil.avaliacoes:
            ctk.CTkLabel(
                self.pat_detail_scroll, 
                text="Nenhuma avaliação registrada ainda.", 
                text_color="gray"
            ).pack(pady=20)
            return

        ctk.CTkLabel(
            self.pat_detail_scroll, 
            text="Histórico Completo de Avaliações:", 
            font=self.fonts["section"]
        ).pack(pady=(20, 10), anchor="w")

        # Iterar sobre cada avaliação (Card de Avaliação)
        for av in perfil.avaliacoes:
            # Cria um "Card" para agrupar a avaliação de uma data
            card_av = ctk.CTkFrame(self.pat_detail_scroll, fg_color=("gray85", "gray15"))
            card_av.pack(fill="x", pady=8, padx=5)

            # Cabeçalho do Card (Data e Fisio)
            header_text = f"📅 Data: {av.data}   |   🧑‍⚕️ Fisioterapeuta: {av.fisioterapeuta_nome}"
            ctk.CTkLabel(
                card_av, 
                text=header_text, 
                font=self.fonts["section"], 
                anchor="w"
            ).pack(pady=(10, 5), padx=15, fill="x")

            # Observações (se houver)
            if av.observacoes:
                ctk.CTkLabel(
                    card_av, 
                    text=f"Obs: {av.observacoes}", 
                    anchor="w", 
                    text_color="gray"
                ).pack(pady=(0, 10), padx=15, fill="x")

            # Lista de Escalas desta Avaliação (Igual ao Executivo)
            for app in av.aplicacoes:
                maximo = f"/{app.pontuacao_maxima}" if app.pontuacao_maxima else " s"
                percentual = f"  ({app.percentual:.1f}%)" if app.percentual is not None else ""
                status = "⚠ Abaixo do corte" if app.abaixo_do_corte else "✓ Dentro do esperado"
                cor = "#FF6B6B" if app.abaixo_do_corte else "#6BCB77"

                # Cria a "linha" invisível para alinhar as colunas
                row = ctk.CTkFrame(card_av, fg_color="transparent")
                row.pack(fill="x", pady=2, padx=15)

                # Coluna 1: Nome da Escala
                ctk.CTkLabel(
                    row,
                    text=f" • {app.escala_nome}",
                    anchor="w",
                    width=350  # Mantém alinhado com o Executivo
                ).pack(side="left")

                # Coluna 2: Pontuação + Percentual
                ctk.CTkLabel(
                    row,
                    text=f"{app.pontuacao_total}{maximo}{percentual}",
                    anchor="w",
                    width=120
                ).pack(side="left")

                # Coluna 3: Status Colorido
                ctk.CTkLabel(
                    row,
                    text=status,
                    anchor="w",
                    text_color=cor
                ).pack(side="left")
            
            # Espaçador interno no final do card
            ctk.CTkFrame(card_av, fg_color="transparent", height=5).pack()
            

    def acao_exportar_pdf(self) -> None:
        """Exporta perfil como PDF"""
        if not self.current_patient_id:
            messagebox.showwarning("Aviso", "Nenhum paciente selecionado.")
            return

        tipo = self.resumo_var.get()

        try:
            # TODO: Integrar com gerar_relatorio_pdf da relatorio_service
            messagebox.showinfo(
                "Exportar PDF",
                f"Exportação de PDF\n"
                f"Tipo: {tipo}\n"
                f"Paciente ID: {self.current_patient_id}\n\n"
                f"(Módulo de PDF será integrado em breve)"
            )
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao exportar: {str(e)}")
            
            

    def acao_atualizar_visualizacao(self, escolha: str) -> None:
        """Troca a visualização do perfil conforme opção selecionada."""
        if not self.current_patient_id:
            return

        for widget in self.pat_detail_scroll.winfo_children():
            widget.destroy()

        try:
            with get_session() as session:
                if escolha == "Executivo":
                    resumo = resumo_executivo(session, self.current_patient_id)
                    self._render_resumo_executivo(resumo)
                elif escolha == "Completo":
                    perfil = perfil_completo(session, self.current_patient_id)
                    self._render_perfil_completo(perfil)
                elif escolha == "Por Escala":
                    perfil = perfil_completo(session, self.current_patient_id)
                    self._render_perfil_por_escalas(perfil)
        except PacienteNaoEncontradoError:
            messagebox.showerror("Erro", "Paciente não encontrado.")
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao carregar visualização: {str(e)}")


    def acao_visualizar_historico_escala(self, nome_escala: str) -> None:
        """Carrega o histórico de evolução da escala selecionada."""
        if not self.current_patient_id:
            return

        for widget in self.pat_detail_scroll.winfo_children():
            widget.destroy()

        try:
            with get_session() as session:
                hist = historico_escala(session, self.current_patient_id, nome_escala)
                print(hist)  # Debug: Verificar dados retornados
                self._render_historico_escala(hist)
        except PacienteNaoEncontradoError:
            messagebox.showerror("Erro", "Paciente não encontrado.")
        except EscalaNaoEncontradaError:
            messagebox.showerror("Erro", f"Escala '{nome_escala}' não encontrada.")
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao carregar histórico: {str(e)}")


    def _render_resumo_executivo(self, resumo) -> None:
        """Renderiza o resumo executivo do paciente."""

        # Cabeçalho
        info_text = (
            f"Nome: {resumo.paciente_nome}\n"
            f"Data de Nascimento: {resumo.data_nascimento}\n"
            f"Total de Avaliações: {resumo.total_avaliacoes}\n"
            f"Última Avaliação: {resumo.data_ultima_avaliacao or 'Nenhuma'}"
        )
        ctk.CTkLabel(
            self.pat_detail_scroll,
            text=info_text,
            justify="left",
            anchor="nw"
        ).pack(pady=10, fill="x")

        # Alertas
        if resumo.alertas:
            ctk.CTkLabel(
                self.pat_detail_scroll,
                text=f"⚠  {len(resumo.alertas)} alerta(s) de ponto de corte:",
                font=self.fonts["section"],
                text_color="#FF6B6B"
            ).pack(pady=(20, 5), anchor="w")

            for alerta in resumo.alertas:
                texto = (
                    f"  • {alerta.escala_nome}:  "
                    f"{alerta.pontuacao} < corte {alerta.pontuacao_corte}  "
                    f"(avaliação: {alerta.data_avaliacao})"
                )
                ctk.CTkLabel(
                    self.pat_detail_scroll,
                    text=texto,
                    anchor="w",
                    text_color="#FF6B6B"
                ).pack(pady=2, fill="x")

        # Última pontuação por escala
        ctk.CTkLabel(
            self.pat_detail_scroll,
            text="Última pontuação por escala:",
            font=self.fonts["section"]
        ).pack(pady=(20, 5), anchor="w")

        if not resumo.ultima_pontuacao_por_escala:
            ctk.CTkLabel(
                self.pat_detail_scroll,
                text="  Nenhuma escala registrada.",
                text_color="gray"
            ).pack(anchor="w")
            return

        for ap in resumo.ultima_pontuacao_por_escala:
            maximo = f"/{ap.pontuacao_maxima}" if ap.pontuacao_maxima else " s"
            percentual = f"  ({ap.percentual:.1f}%)" if ap.percentual is not None else ""
            status = "⚠ Abaixo do corte" if ap.abaixo_do_corte else "✓ Dentro do esperado"
            cor = "#FF6B6B" if ap.abaixo_do_corte else "#6BCB77"

            row = ctk.CTkFrame(self.pat_detail_scroll, fg_color="transparent")
            row.pack(fill="x", pady=2)

            ctk.CTkLabel(
                row,
                text=f"  {ap.escala_nome}",
                anchor="w",
                width=380
            ).pack(side="left")

            ctk.CTkLabel(
                row,
                text=f"{ap.pontuacao_total}{maximo}{percentual}",
                anchor="w",
                width=120
            ).pack(side="left")

            ctk.CTkLabel(
                row,
                text=status,
                anchor="w",
                text_color=cor
            ).pack(side="left")


    def _render_perfil_por_escalas(self, perfil) -> None:
        """Renderiza o perfil agrupado por escalas com histórico de cada uma."""
        # Cabeçalho
        ctk.CTkLabel(
            self.pat_detail_scroll,
            text="Histórico por Escala",
            font=self.fonts["title"]
        ).pack(pady=10, anchor="w")

        # Coletar dados: dicionário {escala_nome: lista de aplicacoes}
        escalas_dict = {}
        cortes_dict = {}  # {escala_nome: pontuacao_corte}
        maximos_dict = {}  # {escala_nome: pontuacao_maxima}

        for avaliacao in perfil.avaliacoes:
            for app in avaliacao.aplicacoes:
                if app.escala_nome not in escalas_dict:
                    escalas_dict[app.escala_nome] = []
                    cortes_dict[app.escala_nome] = app.pontuacao_corte
                    maximos_dict[app.escala_nome] = app.pontuacao_maxima

                escalas_dict[app.escala_nome].append({
                    'data': avaliacao.data,
                    'fisioterapeuta': avaliacao.fisioterapeuta_nome,
                    'pontuacao_total': app.pontuacao_total,
                    'pontuacao_maxima': app.pontuacao_maxima,
                    'percentual': app.percentual,
                    'abaixo_do_corte': app.abaixo_do_corte
                })

        if not escalas_dict:
            ctk.CTkLabel(
                self.pat_detail_scroll,
                text="Nenhuma escala registrada.",
                text_color="gray"
            ).pack(pady=20)
            return

        # Renderizar cada escala
        for escala_nome in sorted(escalas_dict.keys()):
            # Card da escala
            card = ctk.CTkFrame(self.pat_detail_scroll, fg_color="transparent")
            card.pack(fill="x", pady=15)

            # Cabeçalho da escala
            header_text = f"📊 {escala_nome}"
            if cortes_dict[escala_nome]:
                header_text += f" | Corte: {cortes_dict[escala_nome]}"
            if maximos_dict[escala_nome]:
                header_text += f" | Máximo: {maximos_dict[escala_nome]}"

            ctk.CTkLabel(
                card,
                text=header_text,
                font=self.fonts["section"],
                anchor="w"
            ).pack(fill="x", pady=(0, 10), padx=10)

            # Tabela de histórico da escala
            for i, app_data in enumerate(escalas_dict[escala_nome]):
                maximo = f"/{app_data['pontuacao_maxima']}" if app_data['pontuacao_maxima'] else ""
                percentual = f"  ({app_data['percentual']:.1f}%)" if app_data['percentual'] is not None else ""
                status = "⚠ Abaixo do corte" if app_data['abaixo_do_corte'] else "✓ OK"
                cor = "#FF6B6B" if app_data['abaixo_do_corte'] else "#6BCB77"

                linha = ctk.CTkFrame(card, fg_color="transparent")
                linha.pack(fill="x", pady=2, padx=20)

                # Data
                ctk.CTkLabel(
                    linha,
                    text=str(app_data['data']),
                    anchor="w",
                    width=100
                ).pack(side="left")

                # Pontuação + Percentual
                ctk.CTkLabel(
                    linha,
                    text=f"{app_data['pontuacao_total']}{maximo}{percentual}",
                    anchor="w",
                    width=130
                ).pack(side="left")

                # Fisioterapeuta
                ctk.CTkLabel(
                    linha,
                    text=app_data['fisioterapeuta'],
                    anchor="w",
                    width=200
                ).pack(side="left")

                # Status colorido
                ctk.CTkLabel(
                    linha,
                    text=status,
                    anchor="w",
                    text_color=cor
                ).pack(side="left")

            # Separador visual entre escalas
            ctk.CTkFrame(self.pat_detail_scroll, height=1, fg_color="gray").pack(fill="x", pady=5)


    def _render_historico_escala(self, hist) -> None:
        """Renderiza o histórico de evolução de uma escala."""

        # Cabeçalho
        cabecalho = f"Paciente: {hist.paciente_nome}\nEscala: {hist.escala_nome}"
        if hist.pontuacao_corte:
            cabecalho += f"\nPonto de corte: {hist.pontuacao_corte}"
        if hist.pontuacao_maxima:
            cabecalho += f"  |  Máximo: {hist.pontuacao_maxima}"

        ctk.CTkLabel(
            self.pat_detail_scroll,
            text=cabecalho,
            justify="left",
            anchor="nw"
        ).pack(pady=10, fill="x")

        if not hist.pontos:
            ctk.CTkLabel(
                self.pat_detail_scroll,
                text="Nenhuma avaliação com esta escala encontrada.",
                text_color="gray"
            ).pack(pady=20)
            return

        # Tendência
        variacao = hist.variacao_total
        if variacao is not None:
            cor_tend = "#6BCB77" if variacao > 0 else ("#FF6B6B" if variacao < 0 else "gray")
            ctk.CTkLabel(
                self.pat_detail_scroll,
                text=f"Tendência: {hist.tendencia}",
                text_color=cor_tend,
                font=self.fonts["section"]
            ).pack(pady=(0, 10), anchor="w")

        # Cabeçalho da tabela
        header = ctk.CTkFrame(self.pat_detail_scroll, fg_color="transparent")
        header.pack(fill="x", pady=(10, 2))
        for texto, largura in [("Data", 120), ("Pontuação", 100), ("Fisioterapeuta", 220), ("Status", 160)]:
            ctk.CTkLabel(
                header,
                text=texto,
                font=self.fonts["section"],
                width=largura,
                anchor="w"
            ).pack(side="left", padx=4)

        # Linhas de dados
        for ponto in hist.pontos:
            maximo = f"/{ponto.pontuacao_maxima}" if ponto.pontuacao_maxima else " s"
            status = "⚠ Abaixo do corte" if ponto.abaixo_do_corte else "✓ Dentro do esperado"
            cor = "#FF6B6B" if ponto.abaixo_do_corte else "#6BCB77"

            linha = ctk.CTkFrame(self.pat_detail_scroll, fg_color="transparent")
            linha.pack(fill="x", pady=1)

            for texto, largura in [
                (str(ponto.data), 120),
                (f"{ponto.pontuacao}{maximo}", 100),
                (ponto.fisioterapeuta, 220),
            ]:
                ctk.CTkLabel(
                    linha,
                    text=texto,
                    anchor="w",
                    width=largura
                ).pack(side="left", padx=4)

            ctk.CTkLabel(
                linha,
                text=status,
                anchor="w",
                width=160,
                text_color=cor
            ).pack(side="left", padx=4)

# ==================== INICIALIZAÇÃO ====================

def inicializar_sistema() -> None:
    """Inicializa o banco de dados e escalas"""
    try:
        if not DB_PATH.exists():
            Base.metadata.create_all(bind=engine)
            with get_session() as session:
                popular_escalas(session)
            logger.info("[DB] Banco de dados criado e populado com sucesso.")
        else:
            logger.info("[DB] Banco de dados encontrado.")
    except Exception as e:
        logger.error(f"[ERRO] Falha ao inicializar sistema: {str(e)}")
        raise

if __name__ == "__main__":
    inicializar_sistema()
    app = App()
    app.mainloop()
