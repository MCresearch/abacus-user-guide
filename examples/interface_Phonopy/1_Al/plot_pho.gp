set terminal pngcairo size 1920, 1080 font 'Arial, 36'   ## 格式，大小和字体
set output "Al-FCC_plot.png"  ###输出的文件名

set ylabel 'Frequency (THz)'

set ytics 2
unset key

x1 = 0.13115990
x2 = 0.17753200
x3 = 0.31664810
xmax = 0.43023590
ymin = 0
ymax = 12

set xrange [0:xmax]
set yrange [ymin:ymax]
set xtics ("{/Symbol G}" 0, "X" x1, "K" x2, "{/Symbol G}" x3, "L" xmax)
set arrow 1 nohead from x1,ymin to x1,ymax lt 2
set arrow 2 nohead from x2,ymin to x2,ymax lt 2
set arrow 3 nohead from x3,ymin to x3,ymax lt 2

plot 'pho.dat' using 1:($2) w l lw 3