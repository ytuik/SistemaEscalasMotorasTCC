class ItemEscalaNaoEncontradoError(Exception):
    def __init__(self, item_id, nome_escala=None):
        self.item_id = item_id
        self.nome_escala = nome_escala
        super().__init__(f"Item de escala com ID {item_id} não encontrado na escala {nome_escala}.")