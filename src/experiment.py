import descriptions.gtp3 as gtp
from descriptions.gtp3 import DeploymentEngine
from typing import List, Dict
from data.database import TemplateDatabase
import matplotlib.pyplot as plt
import json
import numpy as np
from tqdm import tqdm
import time
import argparse
import os


def experimentGTPIteration(samples: List, templateData: TemplateDatabase,
                           niter: int = 5, useSame: bool = True, oneShot: bool = False,
                           engine: DeploymentEngine = DeploymentEngine.TEXT_DAVINCI_003,
                           verbose: bool = False) -> Dict:
  # Log Experiment Details
  if verbose:
    print("\nRunning GTP-3 Description Iteration Experiment")
    print("----------------------------------------------")
    print("Development Engine:\t{}".format(engine))
    print("Number of Iterations:\t{}".format(niter))
    print("Using One-Shot:\t\t{}".format(oneShot))
    print("Using Same Prompt:\t{}".format(useSame))
    print("Number of Samples:\t{}".format(len(samples)))
    print("----------------------------------------------")

  # Initialize Experiment Variables
  variables = {
    "numSamples": 0,
    "bleu-1": np.zeros(niter),
    "bleu-2": np.zeros(niter),
    "niter": niter,
    "engine": engine,
    "useSame": useSame,
    "oneShot": oneShot
  }

  # Iterate through each sample
  for i in range(len(samples)):
    sample = samples[i]

    # Initialize Prompt Description Tracker
    tracker = gtp.DescriptionPromptTracker()
    code = sample.get("templateCode")
    template = templateData.getTemplateByCode(code)
    description = template.get("description")
    prompts = sample.get("prompts")

    if len(prompts) < niter: continue
    print("Iterating GTP-3 Through Sample {}".format(i))

    if oneShot:
      tracker.append(prompts[0], description)

    variables["numSamples"] += 1
    for idx in tqdm(range(len(prompts))):
      prompt = prompts[idx]
      if useSame: prompt = prompts[0]
      if idx == 0: candidate = prompt
      else:
        promptGTP = tracker.getPromptGTP(prompt)
        candidate = gtp.completeText(promptGTP, engine)
        tracker.append(prompt, candidate)
      variables["bleu-1"][idx] += gtp.calculateBleuScore(description, candidate)
      variables["bleu-2"][idx] += gtp.calculateBleuScore(description, candidate, weights=[0, 1, 0, 0])
    print("Running Average -> (BLEU-1): {}\t(BLEU-2): {}".format(str(variables["bleu-1"]/variables["numSamples"]), str(variables["bleu-2"]/variables["numSamples"])))
  
  variables["bleu-1"] /= variables["numSamples"]
  variables["bleu-2"] /= variables["numSamples"]
  print("Final Results -> (BLEU-1): {}\t(BLEU-2): {}".format(variables["bleu-1"], variables["bleu-2"]))
  variables["bleu-1"] = list(variables["bleu-1"])
  variables["bleu-2"] = list(variables["bleu-2"])
  return variables


def extractScores(experiment: Dict) -> None:
  return np.array(experiment.get("bleu-1")), np.array(experiment.get("bleu-2"))


RGBA_MAX = (255, 255, 255, 1)
BAR_SPACING = 0.02


class ColorGradient:
  BLUE = ((180, 180, 240, 1), (20, 20, 210, 1))


def createBarPlot(data: np.ndarray, saveFile: str, 
                  gradient: ColorGradient = ColorGradient.BLUE, 
                  title: str = "", axes: List = None) -> None:
  # Create Figure
  fig = plt.figure()
  ax = fig.add_axes([0.1, 0.15, 0.8, 0.75])
  ax.set_title(title)
  ax.yaxis.grid(zorder=0)
  
  # Determine Bar Sizes
  nGroups, nBars = data.shape
  x = np.arange(nGroups)
  barWidth = 0.8 / nBars

  # Determine Bar Color
  baseColor, targColor = gradient
  baseColor = np.array(baseColor, dtype=np.float32)
  targColor = np.array(targColor, dtype=np.float32)
  maxColor = np.array(RGBA_MAX, dtype=np.float32)
  cvec = (targColor - baseColor) / (maxColor * nBars)

  # Plot Bars
  curColor = baseColor / maxColor
  for i in range(nBars):
    c = np.tile(curColor, (nGroups, 1))
    curColor += cvec
    ax.bar(x + (barWidth + BAR_SPACING) * i, data[:, i], color=c, width=barWidth, zorder=3)

  # Configure Axes
  if axes:
    ax.set_xticks(x + nBars / 2 * barWidth, axes)

  # Set Legend
  labels = ["raw input"]
  for i in range(1, nBars):
    labels.append("GTP-3 iter {}".format(i))
  ax.legend(labels=labels)

  fig.savefig(saveFile)


def plotExperiments(data: Dict, saveDir: str) -> None:
  bleuAxesLabels = ["BLEU-1", "BLEU-2"]
  experimentAxesLabels = ["Same Prompt\nNo One-Shot\n(Experiment 1)", 
                          "Different Prompt\nNo One-Shot\n(Experiment 3)", 
                          "Same Prompt\nOne-Shot\n(Experiment 2)", 
                          "Different Prompt\nOne-Shot\n(Experiment 4)"]

  # Plot 1: Experiment 1 BLEU Scores
  e1b1, e1b2 = extractScores(data.get("exp1"))
  data1 = np.vstack((e1b1, e1b2))
  file1 = "{}/experiment1.png".format(saveDir)
  createBarPlot(data1, file1, title="GTP-3 Iteration Experiment 1: Same Prompt, No One-Shot", axes=bleuAxesLabels)

  # Plot 2: Experiment 2 BLEU Scores
  e2b1, e2b2 = extractScores(data.get("exp2"))
  data2 = np.vstack((e2b1, e2b2))
  file2 = "{}/experiment2.png".format(saveDir)
  createBarPlot(data2, file2, title="GTP-3 Iteration Experiment 2: Same Prompt, One-Shot", axes=bleuAxesLabels)

  # Plot 3: Experiment 3 BLEU Scores
  e3b1, e3b2 = extractScores(data.get("exp3"))
  data3 = np.vstack((e3b1, e3b2))
  file3 = "{}/experiment3.png".format(saveDir)
  createBarPlot(data3, file3, title="GTP-3 Iteration Experiment 3: Different Prompt, No One-Shot", axes=bleuAxesLabels)

  # Plot 4: Experiment 4 BLEU Scores
  e4b1, e4b2 = extractScores(data.get("exp4"))
  data4 = np.vstack((e4b1, e4b2))
  file4 = "{}/experiment4.png".format(saveDir)
  createBarPlot(data4, file4, title="GTP-3 Iteration Experiment 4: Different Prompt, One-Shot", axes=bleuAxesLabels)

  # Plot 5: BLEU-1 Scores
  data5 = np.vstack((e1b1, e3b1, e2b1, e4b1))
  file5 = "{}/bleu1.png".format(saveDir)
  createBarPlot(data5, file5, title="GTP-3 Iteration Experiments 1-4 BLEU-1 Scores", axes=experimentAxesLabels)

  # Plot 6: BLEU-2 Scores
  data6 = np.vstack((e1b2, e3b2, e2b2, e4b2))
  file6 = "{}/bleu2.png".format(saveDir)
  createBarPlot(data6, file6, title="GTP-3 Iteration Experiments 1-4 BLEU-2 Scores", axes=experimentAxesLabels)


def main(samplesFile: str, templatesFile: str, engine: DeploymentEngine) -> None:
  # Extract Test Samples and Template Data
  testSamples = json.load(open(samplesFile, "r")).get("samples")
  templateData = TemplateDatabase(templatesFile)

  # Experiment 1: Use Same Prompt, No One-Shot
  var1 = experimentGTPIteration(testSamples, templateData, useSame=True, oneShot=False, engine=engine, verbose=True)

  # Experiment 2: Use Same Prompt, One-Shot
  var2 = experimentGTPIteration(testSamples, templateData, useSame=True, oneShot=True, engine=engine, verbose=True)

  # Experiment 3: No Same Prompt, No One-Shot
  var3 = experimentGTPIteration(testSamples, templateData, useSame=False, oneShot=False, engine=engine, verbose=True)

  # Experiment 4: No Same Prompt, One-shot
  var4 = experimentGTPIteration(testSamples, templateData, useSame=False, oneShot=True, engine=engine, verbose=True)

  # Save Results
  results = {
    "numSamples": var1.get("numSamples"),
    "engine": engine,
    "niter": var1.get("niter"),
    "exp1": {"useSame": var1.get("useSame"), "oneShot": var1.get("oneShot"), "bleu-1": var1.get("bleu-1"), "bleu-2": var1.get("bleu-2")},
    "exp2": {"useSame": var2.get("useSame"), "oneShot": var2.get("oneShot"), "bleu-1": var2.get("bleu-1"), "bleu-2": var2.get("bleu-2")},
    "exp3": {"useSame": var3.get("useSame"), "oneShot": var3.get("oneShot"), "bleu-1": var3.get("bleu-1"), "bleu-2": var3.get("bleu-2")},
    "exp4": {"useSame": var4.get("useSame"), "oneShot": var4.get("oneShot"), "bleu-1": var4.get("bleu-1"), "bleu-2": var4.get("bleu-2")},
  }

  saveDir = "experiment/output/{}".format(str(time.time()).replace(".", "_"))
  os.mkdir(saveDir)

  dataFile = "{}/data.json".format(saveDir)
  json.dump(results, open(dataFile, "w"), indent=2)

  plotExperiments(results, saveDir)
  

if __name__ == "__main__":
  """
  Example: 
  python experiment.py -sf experiment/samples/experiment_samples_small.json -tf data/templates.json -e text-davinci-003
  """
  parser = argparse.ArgumentParser()
  parser.add_argument("-sf", "--samplesFile", required=True, type=str)
  parser.add_argument("-tf", "--templatesFile", required=True, type=str)
  parser.add_argument("-e", "--engine", type=str)
  args = parser.parse_args()

  engine = args.engine if args.engine in DeploymentEngine.AVAILABLE_ENGINES else DeploymentEngine.TEXT_DAVINCI_003
  main(args.samplesFile, args.templatesFile, engine)