cd /c/Users/Ruben/OneDrive/Documents/FastFlyerPlayground/flyers/WIP/experiments/power_riders_20261007
W="mwwm wmwm mwmw mmww wwmm wmmw"
run() { echo "## $*"; python front_pr.py "$@" 2>&1 | grep -E "^\{|^built|Infeasible|Traceback|Error|FOUND|saved|max load" ; }
for w in $W; do run 7 --w $w --k4 nb1 --k5 nb1 --tl 120 --tag t2_nb1_$w; done
for w in $W; do run 7 --w $w --k4 nb1 --k5 nb1 --nw 2 --tl 180 --tag t2_nb1_nw2_$w; done
for w in $W; do run 7 --w $w --k4 nb1 --k5 nb1 --ride 1:V:K5p --tl 120 --tag t2_ride_K5p_$w; done
for w in $W; do run 7 --w $w --k4 nb1 --k5 nb1 --ride 1:V:K5 --tl 120 --tag t2_ride_K5_$w; done
for w in $W; do run 7 --w $w --k4 nb1 --k5 nb1 --ride 1:V:K4p --tl 120 --tag t2_ride_K4p_$w; done
for w in $W; do run 7 --w $w --k4 nb2 --k5 nb2 --tl 240 --tag t2_nb2_$w; done
echo BATCH DONE
