class PontuacaoInvalidaError(Exception):
    def __init__(self, item_descricao, pontuacao_fornecida, pontuacao_maxima):
        self.item_descricao = item_descricao
        self.pontuacao_fornecida = pontuacao_fornecida
        self.pontuacao_maxima = pontuacao_maxima
        super().__init__(f"Pontuação inválida para o item '{item_descricao}': fornecida {pontuacao_fornecida}, máxima {pontuacao_maxima}.")