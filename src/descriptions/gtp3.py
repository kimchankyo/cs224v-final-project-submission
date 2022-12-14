import openai
from nltk.translate.bleu_score import sentence_bleu
from typing import List
import time
import warnings
warnings.filterwarnings("ignore")

API_KEY_FILE = "descriptions/api-key-openai.txt"
openai.api_key = open(API_KEY_FILE, "r").read()

OPENAI_REQUEST_LIMIT_DELAY = 0.1  # 60 Requests / Minute (1 Req. per sec.) (0.5 sec. buffer)


class DeploymentEngine:
  TEXT_DAVINCI_002 = "text-davinci-002"
  TEXT_DAVINCI_003 = "text-davinci-003"
  TEXT_CURIE_001 = "text-curie-001"

  AVAILABLE_ENGINES = [
    TEXT_DAVINCI_002,
    TEXT_DAVINCI_003,
    TEXT_CURIE_001
  ]


def completeText(prompt: str, deploymentID: DeploymentEngine,
                 temperature: float = 0.5, maxTokens: int = 256, minTokens: int = 50,
                 topP: float = 1.0, frequencyPenalty: float = 0.0,
                 presencePenalty: float = 0.0, nTries: int = 5) -> str:
  response = ""
  while len(response.split()) < minTokens and nTries > 0:
    time.sleep(OPENAI_REQUEST_LIMIT_DELAY)
    nTries -= 1
    response = openai.Completion.create(
      engine=deploymentID,
      prompt=prompt,
      temperature=temperature,
      max_tokens=maxTokens,
      top_p=topP,
      frequency_penalty=frequencyPenalty,
      presence_penalty=presencePenalty
    ).get("choices")[0].get("text").strip()
  return response


DISPLAY_NAME_RAW = "RAW"
DISPLAY_NAME_GTP = "GTP"


class DescriptionPromptTracker:
  def __init__(self) -> None:
    self.prompts = []
    self.answers = []
    self.text = ""
  
  def append(self, prompt: str, answer: str):
    self.text = "{}{}:\n{}\nGive me a room description.\n".format(self.text, DISPLAY_NAME_RAW, prompt)
    # self.text = "{}{}:\n{}\n".format(self.text, DISPLAY_NAME_RAW, prompt)
    self.text = "{}{}:\n{}\n".format(self.text, DISPLAY_NAME_GTP, answer)

  def getPromptGTP(self, prompt: str) -> None:
    return "{}{}:\n{}\nGive me a room description.\n{}:".format(self.text, DISPLAY_NAME_RAW, prompt, DISPLAY_NAME_GTP)
    # return "{}{}:\n{}\n{}:".format(self.text, DISPLAY_NAME_RAW, prompt, DISPLAY_NAME_GTP)

  def __str__(self) -> str:
    return self.text


def calculateBleuScore(reference: str, candidate: str, weights: List[float] = [1, 0, 0, 0]) -> float:
  return round(sentence_bleu([reference.split()], candidate.split(), weights=weights), 4)