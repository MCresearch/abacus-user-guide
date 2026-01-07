import matplotlib.pyplot as plt
import matplotlib
import numpy as np
import sys
from mpl_toolkits.axes_grid1 import ImageGrid

dirs=[sys.argv[1],sys.argv[2],sys.argv[3]]
Hs=[]
for i in range(3):
    n_line=0
    for line in open(dirs[i]+"/OUT.ABACUS/hks1_nao.txt"):
        line=np.array(list(map(float,line.split())),dtype=float)
        if n_line == 0:
            H=np.zeros([int(line[0]),int(line[0])],dtype=float)
            # Hs.append(H)
            H[n_line]=line[1:]
        else:
            H[n_line][n_line:]=line
            #print(line1-line2)
        n_line+=1
    for i in range(n_line):
        for j in range(i):
            H[i][j]=H[j][i]
    Hs.append(H)

diff=[(0,1),(0,2)]
Hnames=[sys.argv[4],sys.argv[5],sys.argv[6]]
diff_H=[]
names=[]
# Calculate the difference of Hamiltonians
for i in range(2):
    diff_H.append(Hs[diff[i][0]]-Hs[diff[i][1]])# per element
    names.append(r"$H_{{{0}}}-H_{{{1}}}$".format(Hnames[diff[i][0]],Hnames[diff[i][1]]))

mins=[abs(diff_H[i].min()) for i in range(2)]
maxs=[diff_H[i].max() for i in range(2)]
maxnum=max(mins+maxs)#add two array into a big-size array


# Set up figure and image grid
fig = plt.figure(figsize=(9.75, 4))

grid = ImageGrid(fig, 111,          # as in plt.subplot(111)
                 nrows_ncols=(1,2),
                 axes_pad=0.25,
                 share_all=True,
                 cbar_location="right",
                 cbar_mode="single",
                 cbar_size="7%",
                 cbar_pad=0.15,
                 )
nlocal=len(diff_H[i][0])
step=5
if len(sys.argv) > 7:
    step=int(sys.argv[7])
for i,ax in enumerate(grid):
    im=ax.matshow(diff_H[i],cmap="RdYlBu",vmin=-maxnum,vmax=maxnum)
    ax.set_title(names[i],y=1.05,fontsize=16)  
    ax.set_xticks(np.arange(0,nlocal,step),np.arange(1,nlocal+1,step))
    ax.set_yticks(np.arange(0,nlocal,step),np.arange(1,nlocal+1,step))
    ax.tick_params(axis="x", bottom=True, top=False, labelbottom=True, labeltop=False)
    ax.set_xlabel("Index of NAO",fontsize=14)
    ax.set_ylabel("Index of NAO",fontsize=14)

ax.cax.colorbar(im)
plt.savefig("diff_H_total",bbox_inches='tight',dpi=500)

