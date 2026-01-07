element="Rh"
abacus=$1

cd 00_make_stru
python make_stru.py $element
bash relax_line.sh $element
cd ../

cd 01_relax
cp ../00_make_stru/${element}_slab_relax.STRU ./STRU
bash run.sh 24 $abacus
cd ../

cd 02_make_slab_and_CO
python make_slab_and_CO.py $element
bash relax_line.sh $element
cd ../