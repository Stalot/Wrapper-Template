from exceptions import RequestFailed
from typing import Optional
import requests
import time

class ResponseData:
  def __init__(self, response):
    self.content = response.content
    self.status_code = response.status_code
    self.headers = response.headers

    if self.status_code != 200:
      raise RequestFailed(self.status_code,
                          str(self.read()))

  def read(self,
           decodings = ['utf-8', 'latin-1']) -> Optional[str]:
    for dec in decodings:
      try:
        return self.content.decode(dec)
      except UnicodeDecodeError:
        continue

  def raw(self) -> bytes:
    """
    Returns the raw content of the response in bytes.
    """
    return self.content

class Headers:
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
    
    self.headers[key] = value

  def get_header(self,
                 key: str,
                 raise_exception: bool = False):
    value = self.headers.get(key)
    if not value:
      if raise_exception:
        raise ValueError(f'Header {key} not found.')
    return value

  def get_headers(self):
    return self.headers

class RateLimitManager:
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
    self.request_headers = Headers(overwrite_existing_header)
    self.rate_limit = rate_limit

    self._rate_limit_manager = RateLimitManager(self.rate_limit[0], self.rate_limit[1])

  def get(self, url: str):
    response = requests.get(url, headers=self.request_headers.get_headers())
    self._rate_limit_manager.count()
    return ResponseData(response)

  def headers(self):
    return self.request_headers

if __name__ == '__main__':
  # This sets a rate limit of 30 requests per 60 seconds.
  rate_limit = (30, 60)
  core = WrapperCore(rate_limit)
  core.headers().set_header('User-Agent', 'WrapperTemplate/1.0 (https://github.com/Stalot/Wrapper-Template)')

  # May contain offensive jokes, but who cares?
  joke_request = "https://v2.jokeapi.dev/joke/Any?format=txt"

  i = 1
  while i < 11:
    joke = core.get(joke_request).read()
    print(f"JOKE-{i}: {joke}\n----\n")
    i += 1