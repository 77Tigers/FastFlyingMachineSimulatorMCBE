#!/bin/bash
# usage: screen.sh DIR  -> prints file distance/ext_fail/move_fail for each c*.flyer (limit stored in file)
B=/c/Users/Ruben/OneDrive/Documents/FastFlyerPlayground/target/release
for f in "$1"/c*.flyer; do
 r=$($B/fastflyer-research measure "$f" 1000 10 2>&1 | head -1)
 echo "$f $(echo "$r" | grep -o 'distance=[0-9-]*\|extension_failures=[0-9]*\|movement_failures=[0-9]*\|first_failure_tick=[^ ]*' | tr '\n' ' ')"
done
