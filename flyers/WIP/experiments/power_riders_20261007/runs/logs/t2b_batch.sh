cd /c/Users/Ruben/OneDrive/Documents/FastFlyerPlayground/flyers/WIP/experiments/power_riders_20261007
run() { echo "## $*"; python front_pr.py "$@" 2>&1 | grep -E "^\{|^built|Infeasible|Traceback|Error|FOUND|saved|max load" ; }
for w in mwwm wmwm mwmw mmww wwmm wmmw; do run 7 --w $w --k4 nb1 --k5 nb1 --v box --f free --tl 180 --tag t2b_vbox_ffree_$w; done
for p in mmww,wwmm mwwm,wmwm mwmw,wmwm mwwm,mwmw mmww,wmmw wwmm,wmmw mwwm,mmww mwwm,wwmm wmwm,mmww wmwm,wwmm; do run 7 --w $p --k4 nb1 --k5 nb1 --nw 2 --tl 180 --tag t2b_nw2_$p; done
echo BATCH DONE
