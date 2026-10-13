# n3_11  N3 `C:wwmmm|S:-|pull@1|T:mmwmw`   status: PASS both orders (80/80 each), BOUNDED recurrence
Source: flyers/bank/pl14/mmwmw_two_pulls.flyer, period at tick 100 (bodytrack ids). Actor = sticky piston in B37 (s1 retract, load 13), pulls B20 (13 cells).
State: extension-trace row 100 with original rng/phase/push_limit; saved file translated (-32,-1,0).
Kept (54 cells incl. 1 arm): B37 (11: carrier, 2 sticky + 3 RB), B20 (13: target), B42 (12: powers B37's sticky pistons, ext0 at s0),
 pistons B39/B40/B41 (push B42, ride B37), and the mutual partner B30 (11: pulls B20 at s3, is pulled by B37's 2nd sticky piston at s1)
 with its pistons B28/B29/B32 (push B37). Removed: B19 (pushes B20 at s0), B26 (pushes B30 at s0/s4), everything else.
Prescribed (removed hardware): b20_in (slime (2,2,9), word mmwmw) +X slot 0, cap 13 (B19); b30_in (honey (4,4,7), word mmwwm) +X at slots 0,4,
 caps 13 and 13 (B26; actual 13,12). Slot 1 of B30 (14) and B20 slots 1,3 (13,13) are endogenous.
Outputs: b20_out mmwmw, b30_out mmwwm, b37_out wwmmm, b42_out mmmww. Recurrence: bounded (bbox envelope), passes 30 cycles.
Fixture whole-action max load = 14 (B37 pushes by B28/B29/B32 with riders). Primitive 13.
Results: check_*.json PASS; samples_before_natural.json, samples_after_natural.json 80/80.
No minimisation attempted (a smaller variant could prescribe B37 s2-4 and B42 s0-2 instead of keeping B30/B28/B29/B32/B39-41).
