import os

def predict(submission_path, recording):
    '''
        Predict method for classifying a Data instance. This function is mandatory to submit to the Epilepsy Data Challenge in CodaLab

    Args:
        - submission_path (str): fixed path to the code directory submission_program_dir (e.g. sample_code_submission/) that contains the code submission mandatory files (and possibly other functions the model.py depends upon).
        - recording (cls): a Data instance containing the data of a specific recording. The class is defined [here](https://github.com/biomedepi/seizeit2/blob/main/classes/data.py). The Data instance contains a 'data' object (list of arrays of the data in each of the loaded channels), 'channels' object (a list of strings containing the name of the channels of the data object in order) and an 'fs' object (a list of integers containing the sampling frequency of each of the signals in the data object in order).
    Output:
        - events (list[list[int int]]): a list of lists, where each sublist contains two integers, corresponding to the start and stop times in seconds of the seizure alarms produced by the model. The start and stop times are relative to the start of the recording, for example, if the model detected an event at 10 seconds from the start of the recording with a duration of 5 seconds, and another starting at 20 with a duration of 10 seconds, the output should be: events = [[10 15], [20, 30]]
    '''


    return events
