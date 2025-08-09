from exceptions import RequestFailed
from typing import Optional, Any
import requests
import time
import json

class DataManager:
  def __init__(self):
    ...

  def json_to_dict(self,
              json_data: str) -> dict:
    return json.loads(json_data)

  def xml_to_dict(self,
                  xml_data: str):
    ...

class _ResponseData:
  """
  Management of request responses.
  """
  def __init__(self, response):
    self._content = response.content
    self._status_code = response.status_code
    self._headers = response.headers

    if self._status_code != 200:
      raise RequestFailed(self._status_code,
                          str(self.read()))

  def read(self,
           decodings = ['utf-8', 'latin-1']) -> str:
    """
    Returns the content of the response in a string. Raises ValueError if not able to decode with the given decodings.
    """
    for dec in decodings:
      try:
        return self._content.decode(dec)
      except UnicodeDecodeError:
        continue
    
    raise ValueError(f'Could not decode response with decodings: {decodings}')

  def raw(self) -> bytes:
    """
    Returns the raw content of the response in bytes.
    """
    return self._content

  def response_status(self) -> int:
    return self._status_code

  def response_headers(self) -> Any:
    return self._headers
   
class _Headers:
  """
  A class for managing headers.

  If overwrite is True, it will overwrite existing header values.
  """
  def __init__(self,
              overwrite: bool = False):
    self.headers = {}
    self.overwrite= overwrite
    
  def set_header(self,
                 key: str,
                 value: str) -> None:
    already_exists = self.headers.get(key)
    if already_exists:
      if not self.overwrite:
        raise ValueError(f'Header {key} already exists.')
    
    self.headers[key] = str(value)

  def get_header(self,
                 key: str,
                 raise_exception: bool = False) -> str:
    value = self.headers.get(key)
    if not value:
      if raise_exception:
        raise ValueError(f'Header {key} not found.')
    return str(value)

  def get_headers(self):
    return self.headers

class _RateLimitManager:
  """
  A class for managing rate limits.
  """
  def __init__(self,
               max_requests: int,
               wait_time: int):
    self.max_requests = max_requests
    self.wait_time = wait_time
    self. requests_made = 0

  def count(self):
    self.requests_made += 1
    self.check()

  def check(self):
    if self.requests_made >= self.max_requests:
      self.requests_made = 0
      print(f'Rate limit reached. Waiting {self.wait_time} seconds...')
      time.sleep(self.wait_time)

class WrapperCore:
  def __init__(self,
               rate_limit: tuple[int, int] = (20, 60),
               overwrite_existing_header: bool = False):
    self._request_headers = _Headers(overwrite_existing_header)
    self._rate_limit = rate_limit
    self._rate_limit_manager = _RateLimitManager(self._rate_limit[0], self._rate_limit[1])

  def get(self,
          url: str):
    """Does GET requests to the given URL."""
    response = requests.get(url, headers=self._request_headers.get_headers())
    self._rate_limit_manager.count()
    return _ResponseData(response)

  def headers(self):
    return self._request_headers

if __name__ == '__main__':
  # This sets a rate limit of 30 requests per 60 seconds.
  rate_limit = (30, 60)
  core = WrapperCore(rate_limit)
  core.headers().set_header('User-Agent', 'WrapperTemplate/1.0 (https://github.com/Stalot/Wrapper-Template)')

  # May contain offensive jokes, but who cares?
  joke_request = "https://v2.jokeapi.dev/joke/Any?format=json"

  #i = 1
  #while i < 11:
  #  joke = core.get(joke_request).read()
  #  print(f"JOKE-{i}: {joke}\n----\n")
  #  i += 1

  data_manager = DataManager()

  response = core.get(joke_request).read()
  joke = data_manager.json_to_dict(response)
  print(joke)