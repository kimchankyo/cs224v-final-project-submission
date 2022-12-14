from flair.models import TARSClassifier
from flair.data import Sentence, Label
from typing import Tuple, List


ROOM_TYPE_CLASSES = [
  "bedroom", 
  "dining", 
  "kitchen", 
  "living", 
  "office", 
  "bathroom", 
  "children", 
  "outdoor", 
  "hallway"
]

BINARY_RESPONSE = ["yes", "no"]


# Initialize Saved Few-Shot TARS Classification Model
# NOTE: predict_zero_shot used instead of predict to reduct the allowable
#       classification predictions to be within the ROOM_TYPE_CLASSES
tars = TARSClassifier.load("classifier/cached/tars-few-shot-furniture.pt")


def getHighestLabel(labels: List[Label]) -> Label:
  # Assumes labels is not empty
  highest = labels[0]
  for label in labels:
    if label.score > highest.score:
      highest = label
  return highest


def getBinaryResponse(inputText: str) -> Tuple[bool]:
  t = Sentence(inputText)
  tars.predict_zero_shot(t, BINARY_RESPONSE)

  # If cannot determine label, return False
  if len(t.get_labels()) == 0:
    return False, False
  else:
    response = getHighestLabel(t.get_labels()).value
    return True, True if response == BINARY_RESPONSE[0] else False


def getRoomTypeClass(inputText: str) -> Tuple[bool]:
  t = Sentence(inputText)
  tars.predict_zero_shot(t, ROOM_TYPE_CLASSES)

  # If cannot determine label, return False
  if len(t.get_labels()) == 0:
    return False, False
  else:
    return True, getHighestLabel(t.get_labels()).value


