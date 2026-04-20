class FisioterapeutaNotFoundError(Exception):
    def __init__(self, fisioterapeuta_id):
        self.fisioterapeuta_id = fisioterapeuta_id
        super().__init__(f"Fisioterapeuta com ID {fisioterapeuta_id} não encontrado.")