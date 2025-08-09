

from exceptions import RequestFailed
from requests.structures import CaseInsensitiveDict
from typing import Optional, Any
import requests
import time
import json
import urllib.parse

class _Url:
  def __init__(self, base: str):
    self._base = base
    self._params = {}

  def add_param(self,
                key: str,
                value: Any):
    if isinstance(value, list):
      self._params[key] = ",".join(map(str, value))
    else:
      self._params[key] = str(value)

  def remove_param(self,
                key: str):
    self._params.pop(key, None)

  def clear_params(self):
    self._params.clear()

  def get_string(self):
    if not self._params:
      return self._base
    query_string = urllib.parse.urlencode(self._params, doseq=True)
    return f"{self._base}?{query_string}"

class _UrlManager:
  def __init__(self):
    self._base_url = "https://v2.jokeapi.dev/joke/Any"

  def new_url(self) -> _Url:
    return _Url(self._base_url)

class _DataManager:
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

  def response_headers(self) -> CaseInsensitiveDict:
    return self._headers
   
class _Headers:
  """
  A class for managing headers.

  If overwrite is True, it will overwrite existing header values.
  """
  def __init__(self,
              overwrite: bool = False):
    self._headers = {}
    self._overwrite= overwrite
    
  def set_header(self,
                 key: str,
                 value: str) -> None:
    already_exists = self._headers.get(key)
    if already_exists:
      if not self._overwrite:
        raise ValueError(f'Header {key} already exists.')
    
    self._headers[key] = str(value)

  def get_header(self,
                 key: str,
                 raise_exception: bool = False) -> str:
    value = self._headers.get(key)
    if not value:
      if raise_exception:
        raise ValueError(f'Header {key} not found.')
    return str(value)

  def get_headers(self):
    return self._headers

class _RateLimitManager:
  """
  A class for managing rate limits.
  """
  def __init__(self,
               max_requests: int,
               wait_time: int):
    self._max_requests = max_requests
    self._wait_time = wait_time
    self._requests_made = 0

  def count(self):
    self._requests_made += 1
    self.check()

  def check(self):
    if self._requests_made >= self._max_requests:
      self._requests_made = 0
      print(f'Rate limit reached. Waiting {self._wait_time} seconds...')
      time.sleep(self._wait_time)

class _WrapperCore:
  def __init__(self,
               rate_limit: tuple[int, int] = (20, 60),
               overwrite_existing_header: bool = False):
    if not isinstance(rate_limit, tuple):
      raise TypeError('rate_limit must be a tuple.')
    if not isinstance(overwrite_existing_header, bool):
      raise TypeError('overwrite_existing_header must be a bool.')
    
    self._request_headers = _Headers(overwrite_existing_header)
    self._rate_limit = rate_limit
    self._rate_limit_manager = _RateLimitManager(self._rate_limit[0], self._rate_limit[1])
    self._data_manager = _DataManager()
    self._url_manager = _UrlManager()

  def _get(self,
          url: str) -> _ResponseData:
    """Does GET requests to the given URL."""
    response = requests.get(url, headers=self._request_headers.get_headers())
    self._rate_limit_manager.count()
    return _ResponseData(response)

  def headers(self):
    return self._request_headers

if __name__ == '__main__':
  url_manager = _UrlManager()
  url = url_manager.new_url()
  url.add_param("blacklistFlags", ["nsfw", "racist"])
  url.add_param("lang", "pt")
  url.add_param("format", "json")

  url.clear_params()

  print(url.get_string())