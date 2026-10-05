from rigid import Seg, check, loads
def model():
    A = Seg('A', (0, 2), (0, 0, 0), {(12,2,2):'g',(10,2,3):'g',(11,2,3):'g',(12,2,3):'g',(12,1,3):'g'}, 'slime')
    B = Seg('B', (1, 3), (0, 0, 0), {(11,0,2):'g',(12,0,2):'g',(13,0,2):'g',(11,0,3):'g',(11,1,2):'g',
                                     (13,0,1):('O',4),(11,1,1):('O',4)}, 'slime')
    X1 = Seg('X1', (2, 3), (0,0,0), {(11,1,3):'P'}, rider=True, fire=0)
    X2 = Seg('X2', (0, 1), (0,0,0), {(10,2,2):'P'}, rider=True, fire=2)
    Y1 = Seg('Y1', (2, 3), (0,0,0), {(13,1,2):'S'}, rider=True, fire=0)
    Y2 = Seg('Y2', (0, 1), (0,0,0), {(12,0,3):'S'}, rider=True, fire=2)
    return [A, B, X1, X2, Y1, Y2]
if __name__ == '__main__':
    s = model(); print(check(s)); print('load', loads(s))
