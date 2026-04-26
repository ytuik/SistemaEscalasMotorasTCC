class PlanilhaInvalidaError(Exception):
    """Exceção para indicar que a planilha importada é inválida ou não segue o formato esperado."""
    def __init__(self, mensagem: str = "Planilha inválida: o arquivo não segue o formato esperado. Verifique se as abas e os campos estão corretos."):
        self.mensagem = mensagem
        super().__init__(mensagem)