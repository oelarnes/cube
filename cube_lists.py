"""
python / cli functions for downloading a cube tutor list by id

from shell usage: `python cube_tutor.py 135529 --download-dir /path/to/download/location`
"""
import argparse
import os.path
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import requests


# install chromedriver with homebrew or what have you and place the path to the executable here
CHROMEDRIVER_PATH = "/Users/joel/Projects/cube/chromedriver"
COBRA='cubecobra'
TUTOR='cubetutor'

def view_cube_url(cube_id: int) -> str:
  return f"http://www.cubetutor.com/viewcube/{cube_id}"


def download_cube_list(cube_id: any, download_dir: str = ".", source=COBRA) -> None:
  if source==TUTOR:
    options = Options()
    options.add_argument('--headless')
    driver = webdriver.Chrome(CHROMEDRIVER_PATH, chrome_options=options)

    # enable download from headless chrome
    # https://stackoverflow.com/questions/45631715/downloading-with-chrome-headless-and-selenium?rq=1
    driver.command_executor._commands["send_command"] = ("POST", '/session/$sessionId/chromium/send_command')
    params = {'cmd': 'Page.setDownloadBehavior', 'params': {'behavior': 'allow', 'downloadPath': download_dir}}
    driver.execute("send_command", params)

    driver.get(view_cube_url(cube_id))
    driver.find_element_by_id("exportListForm").submit()
  elif source==COBRA:
    response = requests.get(f'https://cubecobra.com/cube/download/plaintext/{cube_id}')
    filename = os.path.join(
      download_dir,
      response.headers['Content-disposition'].split("filename=")[1]
    )
    with open(filename, 'w') as target_file:
      target_file.write(response.text)
  else:
      raise ValueError('bad source')


def main():
  parser = argparse.ArgumentParser(description="download a cube list in txt format from cubetutor.com")
  parser.add_argument("cube_id", default=1, type=int)
  parser.add_argument("--download-dir", default=".")
  args = parser.parse_args()
  download_cube_list(args.cube_id, args.download_dir)


if __name__ == "__main__":
  main()
