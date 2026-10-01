import csv,sys,re
rows=list(csv.DictReader(open(sys.argv[1])))
rows.sort(key=lambda r:(r['clean']!='true',int(r['max_successful_action'])))
for r in rows[:int(sys.argv[2])]:print(re.split(r'[\/]',r['file'])[-1],r['distance'],r['max_successful_action'],r['clean'],r['end_blocks'])
