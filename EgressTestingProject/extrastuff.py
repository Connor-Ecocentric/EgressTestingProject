import pandas as pd
import os
cwd = dir_path = os.path.dirname(os.path.realpath(__file__))
path = (cwd + "\\SDTest_result_logs")


for filename in os.listdir(path):
    fullfile = (os.path.join(path, filename))
    with open(fullfile) as f:
        content = f.readlines()
        print content
