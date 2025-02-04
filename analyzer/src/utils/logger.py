import logging
import os

class CustomFormatter(logging.Formatter):
  grey = "\x1b[38;20m"
  yellow = "\x1b[33;20m"
  green = "\x1b[32;20m"
  red = "\x1b[31;20m"
  bold_red = "\x1b[31;1m"
  reset = "\x1b[0m"
  format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)"

  FORMATS = {
    logging.DEBUG: green + format + reset,
    logging.INFO: green + format + reset,
    logging.WARNING: yellow + format + reset,
    logging.ERROR: red + format + reset,
    logging.CRITICAL: bold_red + format + reset
  }

  def format(self, record):
    log_fmt = self.FORMATS.get(record.levelno)
    formatter = logging.Formatter(log_fmt)
    return formatter.format(record)

class MultiLogger:
  """
  A wrapper around the standard logger that allows logging results separately.
  If `result=True` is passed in the log method, the log is written to `result.log`.
  """

  def __init__(self, logger, result_logger):
    self.logger = logger
    self.result_logger = result_logger

  def _log(self, level, msg, *args, result=False, **kwargs):
    if result:
      self.result_logger.log(level, msg, *args, **kwargs)
    else:
      self.logger.log(level, msg, *args, **kwargs)

  def debug(self, msg, *args, result=False, **kwargs):
    self._log(logging.DEBUG, msg, *args, result=result, **kwargs)

  def info(self, msg, *args, result=False, **kwargs):
    self._log(logging.INFO, msg, *args, result=result, **kwargs)

  def warning(self, msg, *args, result=False, **kwargs):
    self._log(logging.WARNING, msg, *args, result=result, **kwargs)

  def error(self, msg, *args, result=False, **kwargs):
    self._log(logging.ERROR, msg, *args, result=result, **kwargs)

  def critical(self, msg, *args, result=False, **kwargs):
    self._log(logging.CRITICAL, msg, *args, result=result, **kwargs)

  def exception(self, msg, *args, result=False, **kwargs):
    self._log(logging.ERROR, msg, *args, result=result, exc_info=True, **kwargs)


class LoggerFactory:
  """
  Logger factory to create and manage multiple loggers.

  Each class instance gets its own logger instance with a unique name.
  Loggers can write to:
  - A global logging folder (`global_logger_folder`).
  - A local logging folder (`local_logger_folder`).
  - The console.
  - A separate result log (`result.log`) when `result_logger=True`.

  The logger factory should be initialized once before usage.
  """

  _instance = None
  registered_logging_paths = []

  @classmethod
  def initialize(cls, workspace_path, config):
    """
    Initializes the LoggerFactory with global configuration.
    Should be called once at the beginning of the program.
    """
    if cls._instance is None:
      cls._instance = cls()
      cls._instance.config = config.LOG
      cls._instance.workspace_path = workspace_path  
      cls._instance.global_logging_path = cls._instance.config.LOG_PATH if cls._instance.config.LOG_PATH else os.path.join(workspace_path, "logs")
      cls._instance.file_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)')
  
  @classmethod
  def get_logger(cls, name, level=logging.INFO, global_level=logging.ERROR,
                 global_logger_folder="analysis", local_logger_folder=None,
                 result_logger=False, clear_log=True):
    """
    Returns a logger instance.
    
    @param name: Logger name (e.g., "CodeQLRunner", "Scheduler").
    @param level: Logging level for this logger.
    @param global_level: Logging level for the global logger.
    @param clear_log: Clear the log file before writing new logs.
    @param global_logger_folder: Folder name under the global logging path, default is "analysis".
    @param local_logger_folder: Path to the local log folder.
    @param result_logger: If True, and `LOG_RESULT` is enabled, the returned logger will log to `result.log`.
    """
    if cls._instance is None:
      raise ValueError("LoggerFactory has not been initialized. Call LoggerFactory.initialize() first.")

    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Remove any existing handlers to prevent duplicate logs
    if logger.hasHandlers():
      logger.handlers.clear()

    # Console logging
    if cls._instance.config.LOG_TO_CONSOLE:
      ch = logging.StreamHandler()
      ch.setFormatter(CustomFormatter())
      logger.addHandler(ch)

    # Global file logging
    if cls._instance.config.LOG_TO_GLOBAL_FILE:
      global_log_dir = os.path.join(cls._instance.global_logging_path, global_logger_folder)
      os.makedirs(global_log_dir, exist_ok=True)

      log_file_map = {
        logging.INFO: os.path.join(global_log_dir, "info.log"),
        logging.ERROR: os.path.join(global_log_dir, "error.log"),
      }

      log_path = log_file_map.get(global_level, log_file_map[logging.ERROR])  # Default to ERROR logs

      if clear_log and os.path.exists(log_path) and (log_path not in cls.registered_logging_paths):
        cls.registered_logging_paths.append(log_path)
        with open(log_path, 'w'):
          pass

      global_fh = logging.FileHandler(log_path)
      global_fh.setLevel(global_level)
      global_fh.setFormatter(cls._instance.file_format)
      logger.addHandler(global_fh)

    # Local file logging (per repository)
    if cls._instance.config.LOG_TO_LOCAL_FILE and local_logger_folder:
      local_log_dir = local_logger_folder
      os.makedirs(local_log_dir, exist_ok=True)

      local_info_log_path = os.path.join(local_log_dir, "info.log")
      local_error_log_path = os.path.join(local_log_dir, "error.log")

      for log_path, log_level in [(local_info_log_path, logging.INFO), (local_error_log_path, logging.ERROR)]:
        if clear_log and os.path.exists(log_path) and (log_path not in cls.registered_logging_paths):
          cls.registered_logging_paths.append(log_path)
          with open(log_path, 'w'):
            pass
          
        local_fh = logging.FileHandler(log_path)
        local_fh.setLevel(log_level)
        local_fh.setFormatter(cls._instance.file_format)
        logger.addHandler(local_fh)

    if cls._instance.config.LOG_RESULT and result_logger:
      result_log_path = os.path.join(cls._instance.global_logging_path, "result.log")

      result_logger = logging.getLogger("Result")
      result_logger.setLevel(logging.INFO)

      if not result_logger.hasHandlers():
        result_fh = logging.FileHandler(result_log_path)
        result_fh.setLevel(logging.INFO)
        result_fh.setFormatter(cls._instance.file_format)
        result_logger.addHandler(result_fh)

      return MultiLogger(logger, result_logger)

    return logger