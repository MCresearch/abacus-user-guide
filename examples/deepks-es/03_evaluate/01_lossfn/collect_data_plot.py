import numpy as np
import pandas as pd
import argparse
import os
import sys
import matplotlib.pyplot as plt

parser = argparse.ArgumentParser(description="provide number of iterations and work directory.")

parser.add_argument("work_dir", type=str, help="directory containing iter")
parser.add_argument("niter", type=int, help="number of iter.xx")
parser.add_argument("ymax", type=float, help = "max ylim of the plot")
parser.add_argument("plot_name", type=str, help = "output plot name")
parser.add_argument("keywords", nargs='+', type=str, help="keywords of painting items")

args = parser.parse_args()

niter = args.niter
ymax=args.ymax
work_dir = args.work_dir
plot_name = args.plot_name
keywords = args.keywords

conv_rate_list = np.zeros((niter, 2))
train_loss_map={}

# print(args.work_dir)
for iter in range(args.niter):
    iter_dir = os.path.join(args.work_dir,"iter", "iter.%s"%(str(iter).zfill(2)))
    scf_dir = os.path.join(iter_dir, "00.scf")
    train_dir = os.path.join(iter_dir, "01.train")

    # # read in log.data
    # with open(os.path.join(scf_dir, "log.data")) as fp:
    #     lines = fp.readlines()
    # conv_rate_list[iter][0] = float(lines[2].split("\t")[1])
    # conv_rate_list[iter][1] = float(lines[11].split("\t")[1])

    # read in log.train
    file = os.path.join(train_dir, "log.train")
    data = pd.read_csv(file, sep='\s+', skiprows=5, header=None)
    with open(file) as fp:
        lines = fp.readlines()
    info_line = lines[4]
    column_names=info_line.split()[1:]
    data.columns = column_names

    train_loss_map[iter]=data

fig, ax = plt.subplots()

column_names=train_loss_map[0].columns
for column in column_names:
    # if any(column.startswith(keyword) for keyword in keywords):
    if any(keyword in column for keyword in keywords):
        n_epochs=0
        epochs=[]
        losses=[]
        new_iters=[0]
        for iter in train_loss_map.keys():
            data=train_loss_map[iter]
            iter_epochs=data['epoch'].iloc[-1]
            data=data[data[column]!=0]#删去为0的行，此时表示没采样到该数据
            losses+=list(data[column])
            epochs+=list(data['epoch']+n_epochs)
            n_epochs+=iter_epochs
            new_iters.append(n_epochs)
        ax.plot(epochs,losses,label=column)

xtick_labels=[]
for i,new_iter in enumerate(new_iters):
    # print(new_iter)
    ax.axvline(new_iter, color='black', linestyle='--')  # 绘制竖线，线型为虚线
    xtick_labels.append(f"0{i}")
    # ax.text(new_iter, -0.1, f"iter.0{i}", color='red',transform=ax.transAxes)  # 在竖线上方添加标识文字，颜色为红色

ax.set_xticks(new_iters)
ax.set_xticklabels(xtick_labels)

plt.legend()
plt.title(" ".join(keywords))
plt.ylim([0,ymax])
# plt.xlabel("iter")
#plt.ylabel("energy(eV)")
plt.savefig(plot_name+".png", bbox_inches='tight')