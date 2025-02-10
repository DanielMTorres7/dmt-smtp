import logging

name = "DMT SMTP"
custom_format = "%(asctime)s - %(levelname)s [{name}] - %(message)s".format(name=name)
time_format = "%H:%M:%S"

class MyLogger:
    def __init__(self, logger: logging.Logger):
        """
        Aceita um objeto Logger existente e permite alterar temporariamente o formato do log.
        :param logger: Logger personalizado (instância de logging.Logger)
        """
        if not isinstance(logger, logging.Logger):
            raise ValueError("O argumento 'logger' precisa ser uma instância de logging.Logger")
        
        self.logger = logger
        self.custom_format = custom_format
        # Guarda o formato original do primeiro handler
        if self.logger.handlers:
            self.logger_format = self.logger.handlers[0].formatter
        else:
            self.logger_format = logging.Formatter(self.custom_format, time_format)  # Default caso não tenha handler
        
    def _log_with_temp_format(self, level, msg, *args, **kwargs):
        """
        Altera temporariamente o formato do log, executa o log e restaura o formato original.
        """
        # Se temp_format for fornecido, altera o formatador
        self.logger.handlers[0].setFormatter(logging.Formatter(self.custom_format, time_format))
        
        # Chama o método de log da classe pai
        self.logger._log(level, msg, args, **kwargs)
        
        # Restaura o formatador original
        self.logger.handlers[0].setFormatter(self.logger_format)

    def info(self, msg, *args,  **kwargs) -> None:
        self._log_with_temp_format(logging.INFO, msg, *args, **kwargs)

    def error(self, msg, *args,  **kwargs) -> None:
        self._log_with_temp_format(logging.ERROR, msg, *args, **kwargs)

    def debug(self, msg, *args,  **kwargs) -> None:
        self._log_with_temp_format(logging.DEBUG, msg, *args, **kwargs)

    def warning(self, msg, *args,  **kwargs) -> None:
        self._log_with_temp_format(logging.WARNING, msg, *args, **kwargs)

    def exception(self, msg, *args,  **kwargs) -> None:
        self._log_with_temp_format(logging.ERROR, msg, *args, exc_info=True, **kwargs)

# Função para configurar o logger
def setup_logger(logger: logging.Logger = None, level: int = logging.INFO) -> logging.Logger:
    """
    configura o logger para gravar em arquivo ou console.
    :param logger: Logger personalizado (default: Console)
    :param level: Nível de log (default: logging.INFO)
    """
    if isinstance(logger, logging.Logger):
        return MyLogger(logger)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.propagate = False  # Evita propagação para o root logger
    
    # Verificar se já há handlers
    if not logger.handlers:
        formatter = logging.Formatter(custom_format)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    return logger

__all__ = ["setup_logger", "logging"]