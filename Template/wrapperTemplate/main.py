from structure import _WrapperCore
from typing import Optional

class WrapperExample(_WrapperCore):
  """
  May contain offensive jokes, but who cares?

  A simple wrapper example for the JokeAPI.
  """
  def __init__(self):
    super().__init__()

  def get_joke(self,
               black_list: Optional[list[str]] = None,
               language = "en",
               format: str = "txt") -> str | dict:
    url = self._url_manager.new_url()
    if black_list:
      url.add_param("blacklistFlags", black_list)

    url.add_param("lang", language)
    url.add_param("format", format)
    response = str(self._get(url.get_string()).read())

    #if format == "json":
    #  return self._data_manager.json_to_dict(response)
    #elif format == "xml":
    #  ...
    return response

if __name__ == '__main__':
  wrapper = WrapperExample()
  def main():
    response = wrapper.get_joke(["nsfw"])
    joke = f'Joke: {response}\n'
    print(joke)
    user_input = input("""\nNEXT ACTION:\nPRESS ENTER: Get another joke.\nTYPE 'QUIT': Quit the program.\n---> """)
    print("")

    if user_input.upper() == 'QUIT':
      print("Quitting...")
      return

    main()

  main()