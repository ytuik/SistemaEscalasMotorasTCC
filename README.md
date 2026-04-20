# Sistema de Escalas Motoras

Sistema para integração de resultados de escalas de avaliação motora aplicadas a idosos.
Desenvolvido como trabalho de graduação em Ciência da Computação.

---

## Requisitos
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) instalado e em execução

---

## Como executar

### 1. Clone ou extraia o projeto

```bash
git clone <colocar-a-url-aqui>
cd motor_scale_system
```

### 2. Suba os containers

```bash
docker compose up --build
```

Na primeira execução, o Docker vai:
- Baixar as imagens do Python e do MySQL
- Instalar as dependências Python
- Criar o banco de dados automaticamente
- Popular o banco com as escalas cadastradas

---

## Desenvolvimento local (sem Docker)

Se preferir rodar sem Docker, com Python e MySQL instalados na máquina:

### 1. Crie e ative o ambiente virtual

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux / macOS
source venv/bin/activate
```

### 2. Instale as dependências

```bash
pip install -r requirements.txt
```

### 3. Configure o arquivo `.env`

Renomeie o arquivo `.env.example` para `.env` e preencha com suas credenciais:

```
DB_USER=root
DB_PASSWORD=sua_senha
DB_HOST=localhost
DB_PORT=3306
DB_NAME=motor_scale_system_db
```

### 4. Crie o banco no MySQL

```sql
CREATE DATABASE motor_scale_system CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 5. Execute a demonstração

```bash
python scripts/demo_main.py
```

---

## Estrutura do projeto

```
motor_scale_system/
├── app/
│   ├── database.py        # conexão com o banco via SQLAlchemy
│   └── models/            # models das tabelas
├── scripts/
│   ├── criar_tabelas.py   # cria o schema no banco
│   └── demo.py            # interface interativa de demonstração
├── tests/
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env.example
└── README.md
```

---