"""Export a power-rider solution pkl (pbuild.save) to .flyer.  usage: python export_pkl.py PKL OUT.flyer L"""
import sys, pickle, pathlib
from pbuild import *
import rigid
from psat import to_rigid
D = pickle.load(open(sys.argv[1], 'rb'))
rigid.to_flyer(to_rigid(D['sol']), int(sys.argv[3])).save(sys.argv[2])
print('saved', sys.argv[2])
