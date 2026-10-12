# Phase-shift 3-bps contact experiment

`model.py` uses the existing `satflyer5.FlyerSAT` API with NS=5 and the words
A=`mmwwm`, B=`mmmww`, C=`wwmmm`. It declares `ext_0/ext_1/ext_4` for A and
`ext_0/ext_1/ext_2` for B; C's moves must have actual piston causes. It limits
the roles to A:P2, B:P3+S3, C:R+2×O3, with no C pistons. The two C contact
glues are fixed at `(3,0,0)` and `(3,1,0)`; P2, P3 and S3 are pinned at
`(0,0,0)`, `(0,1,0)` and `(4,1,0)`.

The exact model with ordinary movement-collision checks is infeasible for
that seed. A targeted relaxation of only the `move` constraints gives this
candidate (all coordinates are slot-0 world coordinates):

```text
A slime: (-1,0,0)g (0,0,0)P2
B honey: (0,1,-1)g (1,1,-1)g (2,0,-1)g (2,1,-1)g
         (3,0,-1)g (3,1,-1)g (3,2,-1)g (4,1,-1)g
         (0,1,0)P3 (4,1,0)S3
C slime: (2,0,1)R (2,2,0)O3 (3,0,0)g (3,0,1)g
         (3,1,0)g (3,2,0)g (4,2,0)g (5,2,0)g (6,2,0)O3
```

The model's causes are C pushed by A/P2 at slot 2, C pushed by B/P3 at slot
3, then C pulled by B/S3 at slot 4. The redstone neighbor powers P2 only at
slot 2. The downward-facing observers directly power P3 and S3 at slot 3;
after C advances at slot 3, their faces shift one cell forward and miss those
pistons at slot 4. This uses two separate observer sources. The conditional
same-contact-plane layout places the B pistons four X cells apart; that
four-cell separation is not universal if the push and pull use different C
sites.

The relaxed solution's reported loads by segment/stroke are A=2, B=10, and
C=10 at slot 2 then 9 at slots 3 and 4. In particular, B's slot-2 input and
C's slot-2 output occur in the same model slot. There is exactly one
occupied-destination race in the candidate: B/P3 moves `(2,1,0)` to
`(3,1,0)` while that cell is still occupied by C glue, which A/P2 is also
pushing from `(3,1,0)` to `(4,1,0)`. `satflyer5` rejects this because it
doesn't model a within-slot order for the external drive and the piston
push. The relaxed result therefore depends on the real tick schedule applying
the P2 push before B's external stroke. No ordinary exact-model witness or
real Flyer trace was established here; treat this as geometry only, not a
feasibility result. It also leaves all external-stroke delivery and lifecycle
checks to the drive adapter.
