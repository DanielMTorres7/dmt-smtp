import logging
import os

# Função para configurar o logger
def setup_logger(log_path: str = None, level: int = logging.INFO) -> logging.Logger:
    name = log_path.replace("/", "_").split(".")[0] if log_path else "DMT_SMTP"
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.propagate = False  # Evita propagação para o root logger

    # Verificar se já há handlers
    if not logger.handlers:
        formatter = logging.Formatter('%(asctime)s - %(levelname)s [SMTP] - %(message)s')

        if log_path:
            os.makedirs(os.path.dirname(log_path), exist_ok=True)  # Cria diretórios se não existirem
            file_handler = logging.FileHandler(log_path, encoding='utf-8')
            file_handler.setLevel(level)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        # Se não houver log_path, adicionar console_handler
        else:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(level)
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)

    return logger