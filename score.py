#!/usr/bin/env python
import sys
import os
import csv
import numpy as np
import gc
import time

def load_annot(file):
    events = []
    with open(file, 'r', newline='') as f:
        csv_reader = csv.reader(f)
        for row in csv_reader:
            events.append([float(element) for element in row])

    return events

def eventList2Mask(events, totalLen, fs):
    mask = np.zeros((int(totalLen),))
    for event in events:
        for i in range(min(int(event[0]*fs), int(totalLen)), min(int(event[1]*fs), int(totalLen))):
            mask[i] = 1
    return mask

def mask2eventList(mask, fs):
    events = list()
    tmp = []
    start_i = np.where(np.diff(np.array(mask, dtype=int)) == 1)[0]
    end_i = np.where(np.diff(np.array(mask, dtype=int)) == -1)[0]
    
    if len(start_i) == 0 and mask[0]:
        events.append([0, (len(mask)-1)/fs])
    else:
        # Edge effect
        if mask[0]:
            events.append([0, (end_i[0]+1)/fs])
            end_i = np.delete(end_i, 0)
        # Edge effect
        if mask[-1]:
            if len(start_i):
                tmp = [[(start_i[-1]+1)/fs, (len(mask))/fs]]
                start_i = np.delete(start_i, len(start_i)-1)
        for i in range(len(start_i)):
            events.append([(start_i[i]+1)/fs, (end_i[i]+1)/fs])
        events += tmp
    return events

def getOverlap(a, b):
    return max(0, min(a[1], b[1]) - max(a[0], b[0]))

def perf_measure_epoch(true_events, pred_events, rec_dur):
    """
    Evaluates the performance of predicted event intervals against actual event intervals.
    
    Parameters:
    actual (list of lists): List of [start, stop] times for actual events.
    predicted (list of lists): List of [start, stop] times for predicted events.
    duration (int): The total duration of the observation period in seconds.
    
    Returns:
    dict: A dictionary containing counts of TP, FN, TN, and FP.
    """
    resolution = 1  # Define a small time step to discretize the timeline
    time_steps = int(rec_dur / resolution)
    timeline = [0] * time_steps  # 0 indicates no event, 1 for actual, 2 for predicted, 3 for both
    
    # Mark actual events
    for start, stop in true_events:
        for i in range(int(start / resolution), int(stop / resolution)):
            timeline[i] |= 1  # Set bit for actual event
    
    # Mark predicted events
    for start, stop in pred_events:
        for i in range(int(start / resolution), int(stop / resolution)):
            timeline[i] |= 2  # Set bit for predicted event
    
    # Compute TP, FN, TN, FP
    TP = sum(1 for t in timeline if t == 3)  # Both actual and predicted
    FN = sum(1 for t in timeline if t == 1)  # Only actual
    FP = sum(1 for t in timeline if t == 2)  # Only predicted
    TN = sum(1 for t in timeline if t == 0)  # Neither actual nor predicted
    
    return TP, FP, TN, FN

def perf_measure_ovlp(true_events, pred_events):
    TP = 0
    FP = 0
    FN = 0

    for pr in pred_events:
        found = False
        for tr in true_events:
            if getOverlap(pr, tr) > 0:
                TP += 1
                found = True
        if not found:
            FP += 1
    for tr in true_events:
        found = False
        for pr in pred_events:
            if getOverlap(tr, pr) > 0:
                found = True
        if not found:
            FN += 1

    return TP, FP, FN


def get_metrics(true_events, pred_events, rec_dur):
    TP_epoch, FP_epoch, TN_epoch, FN_epoch = perf_measure_epoch(true_events, pred_events, rec_dur)

    TP_ovlp, FP_ovlp, FN_ovlp = perf_measure_ovlp(true_events, pred_events)

    if len(true_events) == 0:
        sens_ovlp = float("nan")
        prec_ovlp = float("nan")
        f1_ovlp = float("nan")
    else:
        sens_ovlp = TP_ovlp/(TP_ovlp + FN_ovlp)
        if TP_ovlp == 0 and FP_ovlp == 0:
            prec_ovlp = float("nan")
            f1_ovlp = float("nan")
        else:
            prec_ovlp = TP_ovlp/(TP_ovlp + FP_ovlp)
            if prec_ovlp+sens_ovlp == 0:
                f1_ovlp = float("nan")
            else:
                f1_ovlp = (2*prec_ovlp*sens_ovlp)/(prec_ovlp+sens_ovlp)
    
    FA_ovlp = FP_ovlp*3600/rec_dur
    FA_epoch = FP_epoch*3600/rec_dur

    if len(true_events) == 0:
        sens_epoch = float("nan")
        prec_epoch = float("nan")
        f1_epoch = float("nan")
    else:
        sens_epoch = TP_epoch/(TP_epoch + FN_epoch)
        if TP_ovlp == 0 and FP_ovlp == 0:
            prec_epoch = float("nan")
            f1_epoch = float("nan")
        else:
            prec_epoch = TP_epoch/(TP_epoch + FP_epoch)
            if prec_epoch+sens_epoch == 0:
                f1_epoch = float("nan")
            else:
                f1_epoch = (2*prec_epoch*sens_epoch)/(prec_epoch+sens_epoch)

    spec_epoch = TN_epoch/(TN_epoch + FP_epoch)

    return sens_ovlp, prec_ovlp, FA_ovlp, f1_ovlp, sens_epoch, spec_epoch, prec_epoch, FA_epoch, f1_epoch



if __name__ == "__main__":

    start_time = time.time()

    truth_dir = 'reference'
    output_dir = 'score_output'
    submit_dir = 'submit_output'

    output_filename = os.path.join(output_dir, 'scores.txt')              
    output_file = open(output_filename, 'w')
    
    recordings = [x for x in os.listdir(truth_dir) if '.csv' in x]

    sens_ovlp = []
    prec_ovlp = []
    fah_ovlp = []
    f1_ovlp = []

    sens_epoch = []
    spec_epoch = []
    prec_epoch = []
    fah_epoch = []
    f1_epoch = []

    score = []

    print("========= Running scoring function ==========")
    for i, rec in enumerate(recordings):
        print(str(i+1) + '/' + str(len(recordings)))
        
        true_events = load_annot(os.path.join(truth_dir, rec))
        pred_events = load_annot(os.path.join(submit_dir, rec))

        rec_dur = true_events[-1][1]
        true_events = true_events[:-1]

        sens_ovlp_rec, prec_ovlp_rec, fah_ovlp_rec, f1_ovlp_rec, sens_epoch_rec, spec_epoch_rec, prec_epoch_rec, fah_epoch_rec, f1_epoch_rec = get_metrics(true_events, pred_events, rec_dur)

        sens_ovlp.append(sens_ovlp_rec)
        prec_ovlp.append(prec_ovlp_rec)
        fah_ovlp.append(fah_ovlp_rec)
        f1_ovlp.append(f1_ovlp_rec)

        sens_epoch.append(sens_epoch_rec)
        spec_epoch.append(spec_epoch_rec)
        prec_epoch.append(prec_epoch_rec)
        fah_epoch.append(fah_epoch_rec)
        f1_epoch.append(f1_epoch_rec)

        score.append(sens_ovlp_rec*100-0.4*fah_epoch_rec)

        del true_events
        del pred_events
        gc.collect()

    sens_write = np.nanmean(sens_ovlp)
    fah_write = np.nanmean(fah_epoch)
    score_write = sens_write*100-0.4*fah_write

    print("--- %s seconds ---" % (time.time() - start_time))

    print("========= Successful evaluation!!! ==========")
    print('Sensitivity (any-overlap method): %.2f' % sens_write)
    print('False alarms per hour (epoch method): %.2f' % fah_write)
    print('Score: %.2f' % score_write)
    print('Mean score (per recording): %.2f' % np.nanmean(score))
    
    output_file.write("Score: %.2f" % score_write)
    output_file.close()
