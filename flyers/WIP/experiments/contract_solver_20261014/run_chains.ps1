# Batch of chain (tentacle) designs from words alone (design_sat.py --chain). Sequential; logs in designs/chain_*.log
$b = 'flyers/WIP/experiments/contract_solver_20261014'
$jobs = @(
    @('chain_n2_4', 'mmww', 4, 12, 'm2:3,m1:2,m1:2'),
    @('chain_2bps_3', 'mmwww', 3, 10, 'm2:3,m1:2,m1:2'),
    @('chain_n3_3', 'mmwwm', 3, 14, 'm2:4,m2:2,m1:2'),
    @('chain_n4_3', 'mmmmww', 3, 16, 'm3:4,m2:2,m1:2')
)
foreach ($j in $jobs) {
    $name, $w, $len, $L, $box = $j
    python "$b/design_sat.py" "$b/designs/sat_$name" --words $w --chain $len --L $L --box $box --tl 600 --workers 8 *> "$b/designs/$name.log"
}
