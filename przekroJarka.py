from math import sqrt, pi, atan, sin, cos

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
        wyn.append(f"{p} {LP.rzutuj(wykaz_pkt[p]) - LP.rzutuj(wykaz_pkt[os]):.2f} {wykaz_pkt[p].h}")
    with open(f"dane\\{hektometr}.txt", 'w') as plik:
        plik.write(' '.join(wyn))


print("miłego dnia. (enter żeby wyjść)")
input()