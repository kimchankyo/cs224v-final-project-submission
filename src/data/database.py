import json
from typing import List, Dict


class TemplateDatabase:
  def __init__(self, file: str) -> None:
    self.raw = json.load(open(file, "r"))
    self.categories = self.raw.keys()
    self.codeIndex = {}
    self._index()

  def _index(self) -> None:
    for category in self.categories:
      templates = self.raw.get(category)
      for i in range(len(templates)):
        template = templates[i]
        code = template.get("code")
        self.codeIndex[code] = (category, i)

  def getTemplatesByCategory(self, category: str) -> List:
    return self.raw.get(category)
  
  def getTemplateByCode(self, code: str) -> Dict:
    category, idx = self.codeIndex.get(code)
    return self.raw.get(category)[idx]

  def getTemplateDescriptions(self, category: str) -> List:
    templates = self.raw.get(category)
    return [template.get("description") for template in templates]

class ProductDatabase:
  def __init__(self) -> None:
    pass