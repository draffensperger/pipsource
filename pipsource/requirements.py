import logging

from typing import NamedTuple
from typing import List

class Requirement(NamedTuple):
    package: str
    version: str

def parse(requirements_file: str) -> List[Requirement]:
  """Parses out the requirements from a requirements.txt formatted file."""
  with open(requirements_file) as f:
     requirements_lines = f.readlines()

  requirements = []
  for line in requirements_lines:
    if line.startswith('#') or len(line.strip()) == 0:
      continue
    parts = line.split('=')
    if len(parts) != 2:
      logging.critical('Malformed requirements line: %s', line)
      sys.exit(1)
    requirements.append(Requirement(package=parts[0], version=parts[1].strip()))
  return requirements
