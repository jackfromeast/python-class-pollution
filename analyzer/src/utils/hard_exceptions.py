class TimeoutException(BaseException):
  """
  Custom exception for workflow work timeout.
  This cannot be captured by the general Exception class, like except(Exception) as e.
  """
  pass

def timeout_handler(signum, frame):
  raise TimeoutException("Analysis Worker timed out.")