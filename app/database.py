import os
from contextlib import contextmanager
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from dotenv import load_dotenv

load_dotenv()

# Configurações do Banco
DB_DIR = Path("data")
DB_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = DB_DIR / "banco_avaliacoes.db"

DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(
    DATABASE_URL, 
    echo=os.getenv("DB_ECHO", "false").lower() == "true",
    connect_args={"check_same_thread": False} 
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

class Base(DeclarativeBase):
    pass

@contextmanager
def get_session():
    """
    Gerenciador de contexto do banco de dados (Transaction Manager).
    Faz o commit automaticamente se não houver erros, ou rollback em caso de falha.
    """
    session = SessionLocal()
    try:
        yield session
        session.commit()    # <-- Salva as alterações se tudo no controller/service deu certo
    except Exception:
        session.rollback()  # <-- Desfaz tudo se ocorreu um erro de regra de negócio
        raise               # <-- Repassa o erro para a UI mostrar ao usuário
    finally:
        session.close()     # <-- Devolve a conexão de forma segura
        