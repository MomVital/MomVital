from pyVHR.analysis.pipeline import Pipeline
import numpy as np
import pyhrv.time_domain as td
import statistics
import time
from scipy.signal import find_peaks

import time
import functools
import json
import orjson


def execution_timer(func):
    """
    Decorator to measure and log the execution time of a function.

    Parameters:
        func (function): The function to be wrapped.

    Returns:
        function: Wrapped function with execution time measurement.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()  # Start timer
        result = func(*args, **kwargs)    # Execute function
        end_time = time.perf_counter()    # End timer
        execution_time = end_time - start_time  # Calculate elapsed time

        print(f"Function '{func.__name__}' executed in {execution_time:.4f} seconds.")
        return result

    return wrapper


def adaptive_peak_detection(signal, fs=30):
    """
    Adaptive peak detection for heart rate signal.
    
    Parameters:
        signal (numpy.ndarray): The input BVP signal.
        fs (int, optional): Sampling frequency of the signal (default is 30 Hz).
    
    Returns:
        numpy.ndarray: Indices of detected peaks in the signal.
    """
    # 基于信号统计的动态参数
    abs_signal = np.abs(signal)
    height_th = np.percentile(abs_signal, 75)  # 取75%分位数作为高度阈值

    # 根据心率范围计算distance
    max_bpm = 180
    min_distance = int(fs * 60 / max_bpm)  # 180 BPM → 10 samples

    peaks, _ = find_peaks(
        signal,
        distance=min_distance
    )
    return peaks


@execution_timer
def vhr_process(videoFileName='data/vid.avi'):
    """
    Process a video file to extract BVP (Blood Volume Pulse) signals and estimated heart rate.

    Parameters:
        videoFileName (str, optional): Path to the input video file (default: '../data/vid.avi').

    Returns:
        tuple: (bvps, timesES, bpmES)
            - bvps (numpy.ndarray): Extracted BVP signals.
            - timesES (numpy.ndarray): Time series of BVP extraction.
            - bpmES (numpy.ndarray): Estimated BPM values.
    """
    wsize = 6                  # window size in seconds
    roi_approach = 'holistic'  # use holistic approach instead of patches
    bpm_est = 'clustering'     # BPM final estimate if patches choose 'medians' or 'clustering'
    method = 'cupy_CHROM'       # one of the methods implemented in pyVHR

    # run
    pipe = Pipeline()          # object to execute the pipeline
    bvps, timesES, bpmES = pipe.run_on_video(videoFileName,
                                            winsize=wsize,
                                            roi_method='convexhull',
                                            roi_approach=roi_approach,
                                            method=method,
                                            estimate=bpm_est,
                                            RGB_LOW_HIGH_TH=(5,230),
                                            Skin_LOW_HIGH_TH=(5,230),
                                            pre_filt=True,
                                            post_filt=True,
                                            cuda=True,
                                            verb=True)

    return bvps, timesES, bpmES


@execution_timer
def bvp_transform(bvps):
    """
    Transform raw BVP signals into a sequence of NN intervals for HRV analysis.

    Parameters:
        bvps (numpy.ndarray): Extracted BVP signals.

    Returns:
        numpy.ndarray: Sequence of NN intervals (differences between detected peak times).
    """
    bvps_squeezed = np.squeeze(bvps, axis=1)
    stdev, mean = statistics.stdev(bvps_squeezed.flatten()), statistics.mean(bvps_squeezed.flatten())
    # 动态设置高度阈值（例如：基于信号幅度的统计）
    abs_heights = np.abs(bvps_squeezed)
    height_th = np.median(abs_heights) + 0.5 * np.std(abs_heights)  # 中位数+0.5倍标准差
    non_overlap_idx = round(bvps_squeezed.shape[1] / 6 * 5)

    all_peaks = [adaptive_peak_detection(sig) for sig in bvps_squeezed]

    # get peak milisecond time
    peak_miliseconds = []
    interval = bvps_squeezed.shape[1] - non_overlap_idx

    for row in range(len(all_peaks)):
        for idx in all_peaks[row]:
            if row == 0 or idx >= non_overlap_idx:
                milisecond = round((idx + interval * row)/3 * 100, 2)
                peak_miliseconds.append(milisecond)
    
    # calc diff between peaks
    nni_seq = np.diff(peak_miliseconds)
    return nni_seq


@execution_timer
def hrv_process(nni_seq, histogram_path='data/nni_histogram.png'):
    """
    Compute heart rate variability (HRV) metrics from NN intervals.

    Parameters:
        nni_seq (numpy.ndarray): Sequence of NN intervals.

    Returns:
        dict: Dictionary containing HRV time-domain metrics.
    """
    results = td.time_domain(nni=nni_seq)
    # results['nni_histogram'].savefig(histogram_path)
    result_dict = results.__dict__
    result_dict.pop('nni_histogram', None)
    result_dict

    return result_dict


def convert_np_type(obj):
    if isinstance(obj, (np.int64, np.int32)):  
        return int(obj)  # Convert int64 to Python int
    elif isinstance(obj, (np.float64, np.float32)):
        return float(obj)
    return obj


# def remove_useless_data(data):
#     data.pop('timesES')
#     data.pop('nni_seq')
#     for k, v in data['hrv_results'].items():
#         if k in ['sdnn', 'rmssd', 'pnn50']:
#             data[k] = data['hrv_results'][k]
#     data.pop('hrv_results')
#     return data

def normalize(value, min_val, max_val):
    """Normalize a value to a range between 0 and 1."""
    return (value - min_val) / (max_val - min_val) if max_val > min_val else 0

def calculate_stress_level(sdnn, rmssd, pnn50, min_sdnn=20, max_sdnn=500, 
                           min_rmssd=20, max_rmssd=500, min_pnn50=0, max_pnn50=100):
    """
    Calculate stress level based on SDNN, RMSSD, and PNN50.
    The output is a score between 0 (low stress) and 100 (high stress).
    """
    # Normalize values
    norm_sdnn = normalize(sdnn, min_sdnn, max_sdnn)
    norm_rmssd = normalize(rmssd, min_rmssd, max_rmssd)
    norm_pnn50 = normalize(pnn50, min_pnn50, max_pnn50)
    
    # Weights for each metric
    W1, W2, W3 = 0.40, 0.40, 0.20
    
    # Compute stress score
    stress_score = 100 * (1 - (W1 * norm_sdnn + W2 * norm_rmssd + W3 * norm_pnn50))
    
    # Ensure the score is within bounds (0-100)
    return np.clip(stress_score, 0, 100)

@execution_timer
def overall_process(videoFileName='data/vid.avi'):
    # Step 1: Process video → Extract bvps, timesES, bpmES
    bvps, timesES, bpmES = vhr_process(videoFileName)

    # Step 2: Transform bvps → Get NN intervals (nni_seq)
    nni_seq = bvp_transform(bvps)

    # Step 3: Compute HRV results → Return final HRV data
    hrv_results = hrv_process(nni_seq)

    hrv_results_dict = dict(hrv_results)
    for k, v in hrv_results_dict.items():
        hrv_results_dict[k] = convert_np_type(v)

    bpms_lst = [item.tolist() for item in bpmES]
    sdnn = hrv_results_dict['sdnn']
    rmssd = hrv_results_dict['rmssd']
    pnn50 = hrv_results_dict['pnn50']
    stress_lvl = convert_np_type(calculate_stress_level(sdnn, rmssd, pnn50))
    
    result = {
        "bpms": sum(bpms_lst) / len(bpms_lst),
        "sdnn": sdnn,
        "rmssd": rmssd,
        "pnn50": pnn50,
        "stress_level": stress_lvl
    }
    return orjson.loads(orjson.dumps(result, option=orjson.OPT_INDENT_2))

if __name__ == "__main__":
    # temp = overall_process()
    with open('data/temp_data.json', 'r') as file:
        data = json.load(file)

    # print(remove_useless_data(data))
