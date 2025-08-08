
class RequestFailed(Exception):
  def __init__(self,
               status_code: int,
               message: str):
    self.status_code = status_code
    self.message = message
    super().__init__(f'[{self.status_code} - {self.status_context()}]: {self.message}')

  def status_context(self) -> str:
    common_status_codes: dict = {
        400: "Bad Request",
        401: "Unauthorized",
        403: "Forbidden",
        404: "Not Found",
        408: "Request Timeout",
        409: "Conflict",
        429: "Too Many Requests",
        500: "Internal Server Error",
        502: "Bad Gateway",
        503: "Service Unavailable",
        504: "Gateway Timeout",
    }
    
    context: str | None = common_status_codes.get(self.status_code)
    return context if context else "Unknown"