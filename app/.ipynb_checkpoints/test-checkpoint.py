from pyVHR.analysis.pipeline import Pipeline
import numpy as np

wsize = 6                  # window size in seconds
roi_approach = 'holistic'  # use holistic approach instead of patches
bpm_est = 'clustering'     # BPM final estimate if patches choose 'medians' or 'clustering'
method = 'cupy_CHROM'       # one of the methods implemented in pyVHR
videoFileName = './data/vid.avi'

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

# 保存结果到文件
import numpy as np
import os

# 生成输出文件名（基于输入视频文件名）
base_name = os.path.splitext(videoFileName)[0]
output_file = f"{base_name}_results.npz"

# 将结果保存为压缩的numpy文件
np.savez(output_file, 
         bvps=bvps, 
         timesES=timesES, 
         bpmES=bpmES)

print(f"数据已成功保存至：{output_file}")
print("文件包含以下数组：")
print("- bvps: 脉搏信号波形数据")
print("- timesES: 对应时间戳")
print("- bpmES: 估计的心率值")
