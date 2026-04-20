class EscalaNaoEncontradaError(Exception):
    def __init__(self, escala_nome):
        self.escala_nome = escala_nome
        super().__init__(f"Escala com nome '{escala_nome}' não encontrada.")