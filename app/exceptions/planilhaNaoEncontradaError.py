class PlanilhaNaoEncontradaError(Exception):
    """Exceção personalizada para indicar que a planilha não foi encontrada."""
    def __init__(self, caminho_arquivo):
        self.message = f"Planilha não encontrada: {caminho_arquivo}"
        super().__init__(self.message)