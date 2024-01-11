"""
python / cli functions for downloading a cube cobra list by id
"""
import argparse
import os.path
import requests

def view_cube_url(cube_id: int) -> str:
  return f"http://www.cubecobra.com/cube/list/{cube_id}"


def download_cube_list(cube_id: any, download_dir: str = ".") -> None:
  response = requests.get(f'https://cubecobra.com/cube/download/plaintext/{cube_id}')
  response.encoding = 'utf8'
  filename = os.path.join(
    download_dir,
    response.headers['Content-disposition'].split("filename=")[1]
  )
  
  lines = response.text.split('\n')
  lines = [line for line in lines if '#' not in line and len(line) > 1]
    
  print(f'Writing {len(lines)} lines to {filename}')
  with open(filename, 'w', encoding='utf8') as target_file:
    target_file.write('\n'.join(lines) + '\n')

def main():
  parser = argparse.ArgumentParser(description="download a cube list in txt format from cubecobra.com")
  parser.add_argument("cube_id", default=1, type=int)
  parser.add_argument("--download-dir", default=".")
  args = parser.parse_args()
  download_cube_list(args.cube_id, args.download_dir)


if __name__ == "__main__":
  main()
