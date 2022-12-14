from classifier.tars import getRoomTypeClass, getBinaryResponse
from descriptions.gtp3 import DescriptionPromptTracker, completeText, DeploymentEngine
from recommend import getRoomDescriptions, getMatchScoreList, getBasicRecommendations
import os


class ConversationStage:
  OFFER_HELP = 0
  ASK_ROOM_TYPE = 1
  CONFIRM_ROOM_TYPE = 2
  ASK_ROOM_DESCRIPTION = 3
  RETRY_ROOM_TYPE = 4
  RETRY = 5
  ASK_SATISFACTION = 6



def agentOut(message: str) -> None:
  print("AGENT:\t{}".format(message))

def userIn() -> str:
  res = input("USER:\t")
  while len(res) == 0:
    res = input("USER:\t")
  if res == "quit":
    exit()
  return res


def main() -> None:
  stage = ConversationStage.OFFER_HELP
  isRunning = True
  roomType = None

  agentOut("Hello! I am iDesign. I am a virtual assistant to help interior designers find the perfect furniture items")
  while isRunning:
    if stage == ConversationStage.OFFER_HELP:
      agentOut("Would you like my help?")
      ret, val = getBinaryResponse(userIn())
      if not ret:
        agentOut("I'm sorry I did not understand that. Let's try again.")
        continue
      isRunning = val
      stage = ConversationStage.ASK_ROOM_TYPE
    elif stage == ConversationStage.ASK_ROOM_TYPE:
      agentOut("What kind of room are you looking for today?")
      ret, val = getRoomTypeClass(userIn())
      if not ret:
        agentOut("I'm sorry I did not understand that. Let's try again.")
        continue
      stage = ConversationStage.CONFIRM_ROOM_TYPE
      roomType = val
    elif stage == ConversationStage.CONFIRM_ROOM_TYPE:
      agentOut("To confirm, are you looking to design a {} room today?".format(roomType))
      ret, val = getBinaryResponse(userIn())
      if not ret:
        agentOut("I'm sorry I did not understand that. Let's try again.")
        continue
      if val:
        stage = ConversationStage.ASK_ROOM_DESCRIPTION
      else:
        stage = ConversationStage.RETRY_ROOM_TYPE
    elif stage == ConversationStage.RETRY_ROOM_TYPE:
      agentOut("I apologize, I got the wrong room type. Would you like me to try again?")
      ret, val = getBinaryResponse(userIn())
      if not ret:
        agentOut("I'm sorry I did not understand that. Let's try again.")
        continue
      if val:
        stage = ConversationStage.ASK_ROOM_TYPE
        roomType = None
      else:
        isRunning = False
    elif stage == ConversationStage.ASK_ROOM_DESCRIPTION:
      agentOut("Could you please describe to me what kind of room style you are looking for?")
      description = userIn()
      agentOut("Sounds great. I will find a matching room design for you now")
      tracker = DescriptionPromptTracker()
      prompt = tracker.getPromptGTP(description)
      descriptionGTP = completeText(prompt, DeploymentEngine.TEXT_DAVINCI_003)
      options = getRoomDescriptions(roomType)
      matchScores = getMatchScoreList(descriptionGTP, options)
      getBasicRecommendations(matchScores)
      stage = ConversationStage.ASK_SATISFACTION
    elif stage == ConversationStage.ASK_SATISFACTION:
      agentOut("Were you satisfied with your recommendations?")
      ret, val = getBinaryResponse(userIn())
      if not ret:
        agentOut("I'm sorry I did not understand that. Let's try again.")
        continue
      if val:
        agentOut("I am glad to hear it!")
      else:
        agentOut("I'm sorry I failed to find what you are looking for.")
      stage = ConversationStage.RETRY
    elif stage == ConversationStage.RETRY:
      agentOut("Would you like me to try again?")
      ret, val = getBinaryResponse(userIn())
      if not ret:
        agentOut("I'm sorry I did not understand that. Let's try again.")
        continue
      if val:
        stage = ConversationStage.ASK_ROOM_TYPE
      else:
        isRunning = False
  agentOut("Goodbye, and have a nice day!")



if __name__ == "__main__":
  # Clear Terminal Screen
  if os.name == "nt":
    os.system("cls")    # Windows Systems
  else:
    os.system("clear")  # MacOS and Linux Systems

  # Main Demo
  main()