import csv, sys, collections, os
r = list(csv.DictReader(open(sys.argv[1]))); n = int(sys.argv[2]) if len(sys.argv) > 2 else 15
r.sort(key=lambda x: -int(x['distance']))
for x in r[:n]: print(os.path.basename(x['file'].replace(chr(92), '/')), x['distance'], x['movement_failures'], x['first_failure_tick'], x['first_failure_kind'][:50], x['max_successful_action'])
print(sorted(collections.Counter(int(x['distance'])//10*10 for x in r).items()))
