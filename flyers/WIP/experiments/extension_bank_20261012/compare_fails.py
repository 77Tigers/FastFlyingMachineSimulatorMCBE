import json,glob,subprocess,os,sys
exe=os.path.abspath('target/release/contract-search.exe')
ex='flyers/WIP/experiments/extension_bank_20261012'
rc='flyers/WIP/experiments/extension_contract_20261011/prescribed_fixture/rear_cap'
c=json.load(open(rc+'/mixed_before_natural_contract.json'))
agree=0;n=0
for f in sorted(glob.glob(ex+'/fail_probe/fails/fail_*.flyer'), key=lambda s:int(s.split('_')[-1][:-6])):
    i=os.path.basename(f)[:-6]
    c['flyer']='fails/'+os.path.basename(f)
    c['prescribed_script']='../../extension_contract_20261011/prescribed_fixture/rear_cap/mixed_drive.txt'
    cp=ex+'/fail_probe/'+i+'_contract.json'
    json.dump(c,open(cp,'w'))
    r=subprocess.run(['python','tools/extension_contract.py',cp],capture_output=True,text=True)
    py='PASS' if ': PASS' in r.stdout else 'FAIL'
    r2=subprocess.run([exe,cp,'0','1','x','--eval-only','--order','before'],capture_output=True,text=True)
    rs='PASS' if '"pass":true' in r2.stdout else 'FAIL'
    n+=1; agree+= py==rs
    print(i,'py',py,'rust',rs,'|',r.stdout.strip().split('—')[-1][:90],'|',r2.stdout.strip().split('first_failure')[-1][:90])
print('agree',agree,'/',n)
