# Una Europa Epilepsy Data Challenge - Submission guidelines
Repository with example code for submitting a project to the Una Europa Epilepsy Data Challenge.

The challenge submissions are made through the CodaLab platform. Participants must submit 4 mandatory files and any extra scripts required to run the model's evaluation.

In this repository, we include a starter pack containing the templates of the mandatory files ('starter_pack/'). Additionally, we included an example submission bundle with one of the benchmark models published in the [dataset paper]() ('submission_example.zip). Participants are required to submit the files as .zip , similar to the example. The scoring program used to evaluate the submissions is presented in the script 'score.py'.

## Mandatory files:
- model.py
  
  A python script with a required 'predict' function with fixed inputs and output that can be called as model.predict(Args)
  
  Args:
    - submission_path (str): fixed path to the code directory submission_program_dir (e.g. sample_code_submission/) that contains the code submission mandatory files (and possibly other functions the model.py depends upon).
    - recording (cls): a Data object containing the data of a specific recording. The class is defined [here](https://github.com/biomedepi/seizeit2/blob/main/classes/data.py). The Data instance contains a 'data' object (list of arrays of the data in each of the loaded channels), 'channels' object (a list of strings containing the name of the channels of the data object in order) and an 'fs' object (a list of integers containing the sampling frequency of each of the signals in the data object in order).
      
  Output:
    - events (list[list[int int]]): a list of lists, where each sublist contains two integers, corresponding to the start and stop times in seconds of the seizure alarms produced by the model. The start and stop times are relative to the start of the recording, for example, if the model detected an event at 10 seconds from the start of the recording with a duration of 5 seconds, and another starting at 20 with a duration of 10 seconds, the output should be: events = [[10 15], [20, 30]]

- modalities.txt
  
  A text file containing the modalities within the SeizeIT2 dataset that are required to be loaded for running the model. Please check the [dataset paper]() to see which modalities are available. Take into account that not all recordings contain all modalities. The file should contain the exact name of the modality in lower case in different rows (possible modalities: eeg, ecg, emg, mov).

- requirements.txt
  
  A text file containing any additional python packages needed to run the model.predict function (that are not present in the base environment of the challenge worker node, which can be found in 'challenge_environment.yml').

- metadata
  
  Metadata file with only a description required for the submitted code to run. This file should not be changed and it has to be included in the submission bundle.

