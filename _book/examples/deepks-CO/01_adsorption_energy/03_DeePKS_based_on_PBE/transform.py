import torch
import torch.nn as nn
from torch.nn import functional as F
from deepks.model import CorrNet
import sys
pth_dir=sys.argv[1]
ptg_dir=sys.argv[2]
mp = CorrNet.load(pth_dir+"model.pth")
mp.compile_save(ptg_dir+"model.ptg")