from math import sqrt, pi, atan, sin, cos

from ezdxf.enums import TextEntityAlignment
import ezdxf

#from ezdxf.enums import TextEntityAlignment

# potrzebne definicjie funkcji i obiektów
def obl_az(P, K):
    dx = K.x - P.x
    dy = K.y - P.y

    if dx > 0:
        if dy > 0:
            return atan(dy/dx)
        elif dy == 0:
            return 0
        else:
            return atan(dy/dx) + 2 * pi
    elif dx == 0:
        if dy > 0:
            return pi/2
        elif dy < 0:
            return 1.5 * pi
        else:
            return None
    else:
        if dy > 0:
            return atan(dy/dx) + pi
        elif dy == 0:
            return pi
        else:
            return atan(dy/dx) + pi

class Punkt:
    def __init__(self, nr, x, y, h = None):
        self.nr = nr
        self.x = x
        self.y = y
        self.h = h if h != None else None

    def odl_do(self, other):
        return sqrt((self.x - other.x)**2 + (self.y - other.y)**2)


    def __sub__(self, other):
        return Punkt(None, self.x - other.x, self.y - other.y, self.h - other.h)

    def __repr__(self):
        if self.nr == None:
            return(f"[dx dy dh] : [{self.x:.3f} {self.y:.3f} {self.h:.3f}]")
        else:
            return(f"[nr x y h] : [{str(self.nr)} {self.x:.3f} {self.y:.3f} {self.h:.3f}]")  

    def __str__(self):
        if self.nr == None:
            return(f"[dx dy dh] : [{self.x:.3f} {self.y:.3f} {self.h:.3f}]")
        else:
            return(f"[nr x y h] : [{str(self.nr)} {self.x:.3f} {self.y:.3f} {self.h:.3f}]")   

class LiniaPomiarowa:
    def __init__(self, P: Punkt, K: Punkt) -> None:
        self.P = P
        self.K = K
        self.dx = self.K.x - self.P.x
        self.dy = self.K.y - self.P.y
    

        self.az = obl_az(self.P, self.K)
        self.dl = sqrt((self.P.x - self.K.x)**2 + (self.K.y-self.P.y)**2)
    
    
    def rzutuj (self, pkt: Punkt):
        dx = pkt.x - self.P.x
        dy = pkt.y - self.P.y
        b = dy * sin(self.az) + dx * cos(self.az)    
        
        return b

#import wykazu wzpółrzędnych
with open('wykaz.txt') as plik:
    wykaz = {int(linia.strip().split()[0]) : (round(float(linia.strip().split()[1]), 3), round(float(linia.strip().split()[2]), 3), round(float(linia.strip().split()[3]),3)) for linia in plik.readlines()}

    wykaz_pkt = {ki : Punkt(ki, *valju) for ki, valju in wykaz.items()}

hektometr = True

while hektometr:
#podaj hektometr
    hektometr = input('Podaj hektometr, albo [K] jak KONIEC: ')
    if hektometr.lower() == 'k':
        break
    #podaj punkty kluczowe
    inpiut = input('Podaj numery punktów: skrajnego lewego, skrajnego prawego, osiowego \nrozdzielone spacjami: ').strip().split()
    inpiut = [int(i) for i in inpiut]

    os = inpiut[-1]
    reverse = False
    if inpiut[0] > inpiut[1]:
        reverse = True

    lista = sorted([i for i in range(min(inpiut), max(inpiut)+1)], reverse = reverse)


    LP = LiniaPomiarowa(wykaz_pkt[lista[0]],wykaz_pkt[lista[-1]])
    wyn = []
    wyn.append(hektometr)
    wyn.append('1')
    for p in lista:
        try:
            wyn.append(f"{p} {LP.rzutuj(wykaz_pkt[p]) - LP.rzutuj(wykaz_pkt[os]):.2f} {wykaz_pkt[p].h}")
        except KeyError:
            continue
    with open(f"dane\\{hektometr}.txt", 'w') as plik:
        plik.write(' '.join(wyn))

    wysokosci = []
    for p in lista:
        wysokosci.append(wykaz_pkt[p].h)

    #print(wysokosci)

    h_lim = min(wysokosci)//1-1
    for i, h in enumerate(wysokosci):
        wysokosci[i] = round(h - h_lim,2)

    h_u_lim = max(wysokosci)//1 +2

    biezace = []
    for p in lista:
        biezace.append(LP.rzutuj(wykaz_pkt[p]) - LP.rzutuj(wykaz_pkt[os]))

#opracowanie DXF'a

    d_d = [biezace[i+1] - biezace[i] for i, _ in  enumerate(biezace[1:])]
    #print(d_d)
    d_h = [wysokosci[i+1] - wysokosci[i] for i, _ in  enumerate(wysokosci[1:])]
    #print(d_h)
    spadki = [round(d_h[i] / d_d[i] * 100,1) for i, _ in enumerate (d_d)]
    #print(spadki)
    x_opisu =  [(biezace[i+1] + biezace[i])/2 for i, _ in  enumerate(biezace[1:])]


    doc = ezdxf.new('R12', setup=True)
    
    doc.layers.add(name = "punkty")
    doc.layers.add(name = "profil")
    doc.layers.add(name = "opisy")
    doc.layers.add(name = "ramki")
    doc.layers.add(name = "linie pomocnicze", linetype= 'DASHED2')
    doc.layers.add(name = "biezace")
    doc.layers.add(name = "wysokosci")
    doc.layers.add(name = "spadki")

    prz = list(zip(biezace,wysokosci))
    msp = doc.modelspace()
    km = '0'
    if len(hektometr) > 3:
        km, m = int(hektometr[:-3]), int(hektometr[-3:])
    else:
        km = 0
        m = int(hektometr)
    msp.add_polyline2d(list(zip(biezace,wysokosci)),dxfattribs = {'layer' : 'profil'})

    msp.add_text(f"{km:0d}+{m:0>3d}", height = 0.5, dxfattribs = {'layer' : 'opisy', 'style': 'OpenSans-Italic'}).set_placement((0,h_u_lim),align=TextEntityAlignment.MIDDLE_CENTER)

    for p in list(zip(biezace,wysokosci)):
        msp.add_line(p,(p[0],0),dxfattribs = {'layer' : 'linie pomocnicze'})
        msp.add_text(f"{p[0]:+.2f} ", height = 0.15, rotation=90, dxfattribs = {'layer' : 'biezace', 'style': 'OpenSans-Italic'}).set_placement((p[0],0),align=TextEntityAlignment.MIDDLE_RIGHT)
        msp.add_text(f"{p[1]+h_lim:.2f} ", height = 0.15, rotation=90,dxfattribs = {'layer' : 'wysokosci', 'style': 'OpenSans-Italic'}).set_placement((p[0],-1),align=TextEntityAlignment.MIDDLE_RIGHT)

    for dupa in zip(lista,prz):
        msp.add_text(f"{dupa[0]}",height = 0.2, dxfattribs = {'layer' : 'punkty', 'style': 'OpenSans-Italic'}).set_placement(dupa[1], align=TextEntityAlignment.BOTTOM_CENTER)

    for i, p in enumerate(prz[:-1]):
        msp.add_line((prz[i][0],0), (prz[i+1][0],0),dxfattribs = {'layer' : 'ramki'})
        msp.add_line((prz[i][0],-1), (prz[i+1][0],-1),dxfattribs = {'layer' : 'ramki'})
        msp.add_line((prz[i][0],-2), (prz[i+1][0],-2),dxfattribs = {'layer' : 'ramki'})

    msp.add_text(f"{h_lim}",height = 0.3, dxfattribs = {'layer' : 'opisy', 'style': 'OpenSans-Italic'}).set_placement((-18,0),align=TextEntityAlignment.BOTTOM_LEFT)
    msp.add_text(f"{h_lim}",height = 0.3, dxfattribs = {'layer' : 'opisy', 'style': 'OpenSans-Italic'}).set_placement((+18,0),align=TextEntityAlignment.BOTTOM_RIGHT)

    for i, x in enumerate(x_opisu):
        msp.add_text(f"{spadki[i]:+0.1f}%", height = 0.18 ,rotation = 0 if spadki[i] == 0 else 20 if spadki[i] > 0 else -20, dxfattribs = {'layer' : 'spadki', 'style': 'OpenSans-Italic'}).set_placement((x,-2.5), align=TextEntityAlignment.MIDDLE_CENTER)

    for w in [0,-1,-2,-3]:
        msp.add_line((-26,w),(18,w),dxfattribs = {'layer' : 'ramki'})
    for r in [-26,-18,18]:
        msp.add_line((r,0),(r,-3),dxfattribs = {'layer' : 'ramki'})
    for i, content in enumerate(["Odsunięcie od osi","Rzędna punktu","Nachylenie odcinka w %"]):
        msp.add_text(f"{content}", height = 0.35, dxfattribs = {'layer' : 'opisy', 'style': 'OpenSans-Italic'}).set_placement((-25.75,-0.5-i),align=TextEntityAlignment.MIDDLE_LEFT)

    doc.saveas(f"DXF\\{hektometr}.dxf")

print("miłego dnia. (enter żeby wyjść)")
input()