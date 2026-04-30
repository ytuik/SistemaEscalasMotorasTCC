class PacienteNaoEncontradoError(Exception):
    """Exceção para indicar que um paciente com o ID especificado não foi encontrado no sistema."""
    def __init__(self, paciente_id: int):
        mensagem = f"Paciente não encontrado: nenhum paciente com o ID {paciente_id} foi encontrado no sistema."
        self.mensagem = mensagem
        super().__init__(mensagem)
