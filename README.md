# iDesign: A Room Furnishing Virtual Assistant
### Fall 2022 CS 224V Project by Chris Kim (chankyo) and Mia Miao (yanmiao)
A copy of this repository can be found at [this link](https://github.com/kimchankyo/cs224v-final-project-submission). Please request for permission to Chris Kim if you cannot see the repository. Please note that the repository is missing the TARS model .pt file due to the high file size (>100 MB) and will be added in a zipped archive shared through a Google Drive Link (https://drive.google.com/file/d/1nUUj50uZWpjKECB6ihBghn77hvSKOmA5/view?usp=sharing)

In this repository/zipped archive of our project submission, we have included executable code files for replicating results found in our final report. Unfortunately, due to inability to connect to our Google Cloud VM instance that houses our Genie model, we will be unable to include the Genie skill portion of the code in this archive. 

The three main code executables showcased in this archive are as follows
<ul>
  <li>IKEA Catalog Web Scraping and Databse Construction</li>
  <li>Large Language Model (GTP-3) Experiment Replication</li>
  <li>Interactive Virtual Assistant Demo with TARS Classification Model</li>
</ul>


## 0. Installing Dependencies
We highly recommend installing the [Anaconda3](https://www.anaconda.com/) package manager for executing our code because we have provided an <tt>environment.yaml</tt> file to quickly create a working conda environment. The other option is to use the Python 3.7.3 virtual environment and manually installing the required PyPI dependencies using pip.

### If using Anaconda3/Miniconda
Simply create a new conda environment using the <tt>environment.yaml</tt> file.
```
$ conda env create --file environment.yaml
```
Please note that you will need to replace the <tt>[anaconda_home]</tt> section in the <tt>prefix</tt> section to direct towards your anaconda3 location

### If using Python Virtual Environment
IMPORTANT: MAKE SURE YOU ARE USING PYTHON 3.7.3 WHEN CREATING THE VIRTUAL ENVIRONMENT OR ELSE YOU WILL RUN INTO DEPENDENCY ERRORS.

NOTE: PLEASE TRY CONDA ENVIRONMENT METHOD BEFORE PROCEEDING

Manually install the following libraries using pip
```
$ pip install selenium
$ pip install openai
$ pip install nltk
$ pip install numpy
$ pip install flair
$ pip install scipy
$ pip install tqdm
$ pip install matplotlib
```

## 1. IKEA Catalog Web Scraping and Databse Construction
Construction of the IKEA dataset used in this project can be replicated using the <tt>scrape.py</tt> script located in <tt>src/scrape.py</tt>

NOTE: You will need to install [Google Chrome](https://www.google.com/chrome/) and the [ChromeDriver](https://chromedriver.chromium.org/downloads) if you have not already. Please be careful of which versions of Chrome and ChromeDriver you install, as they need to be the same version for compatability. Please update the <tt>CHROME_EXECUTABLE_PATH</tt> and <tt>CHROME_DRIVER_PATH</tt> in the <tt>scrape.py</tt> file as necessary

Run the following line from the <tt>src/</tt> directory with the conda environment active
```
$ python scrape.py
```
NOTE: This data collection process takes a significant amount of time (~2+ hours). We recommend observing the process for a few seconds, or a few items, and then moving on.


## 2. Large Language Model (GTP-3) Experiment
Results from our Large Language Model Experiment can be replicated using the <tt>experiment.py</tt> script located in <tt>src/experiment.py</tt>

You will need to first setup an [OpenAI](https://openai.com/) account and [find/create your API Key](https://beta.openai.com/account/api-keys). Please enter this key into the <tt>src/descriptions/api-key-openai.txt</tt> file and replace the <tt>[replace with openai api key]</tt> text

We have provided two experimental sample sets for you to play around with. One small and one medium sample sets are located in 
```
src/experiment/samples/experiment_samples_small.json
src/experiment/samples/experiment_samples_medium.json
```
respectively. The small set contains 3 template samples and the medium set contains 18 template samples. We recommend running the small sample first, as it is faster, produces replicable results, and does not charge your OpenAI account as much.

To run the experiments, run the following command from the <tt>src/</tt> directory
```
$ python experiment.py -sf experiment/samples/<your_desired_samples>.json -tf data/templates.json -e text-davinci-003
```

You will see the output stored as the most recent timestamp folder in the <tt>src/experiment/output/</tt> directory.


## 3. Interactive Virtual Assistant Demo with TARS Classification Model
We have created an interactive demo of our TARS classification model virtual assistant, which can be activated using the <tt>demo_tars.py</tt> script located in <tt>src/demo_tars.py</tt>.

To try it out, run the following command from the <tt>src/</tt> directory.
```
$ python demo_tars.py
```

Unfortunately, we are unable to provide the Genie room type semantic parsing model version of the assistant at this time due to resource constraints, the expected performance of the model is similar to the TARS version.

Please have fun, poke around, and let us know if you find anything that is interesting, buggy, or can be improved!

## 4. Contact
<tt>Chris Kim   chankyo@stanford.edu</tt>

<tt>Mia Miao    yanmiao@stanford.edu</tt>