import sys
import math

TYPE_MONSTRE = 0
TYPE_MY_HERO = 1
TYPE_OP_HERO = 2

TARGET_TIME_MAX = 10

def debug(txt):
    print(txt, file=sys.stderr, flush=True)
class Vector:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class Pos:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __str__(self):
        return self.x+" "+self.y

    # retourne la distance entre deux points
    def __sub__(self, p2):
        hypo = pow(p2.x-self.x,2)+pow(p2.y-self.y,2)
        return math.sqrt(hypo)

class Entity:
    def __init__(self, id, type, pos, shield_life, is_controlled, health, vector, near_base, threat_for):
        self.id = id

        #0: pour un monstre
        #1: pour un de vos héros
        #2: pour un héros de l'adversaire
        self.type = type

        self.pos = pos

        if self.pos.x<5000:
            calcPosX = int(math.asin(math.pi/4)*1600*(self.id+1))
            calcPosY = int(math.asin(math.pi/4)*1600*(4-self.id-1))
        else:
            calcPosX = pos.x
            calcPosY = pos.y
        self.initPos = Pos(calcPosX, calcPosY)
        self.shieldLife=shield_life
        self.isControlled=is_controlled
        self.health=health
        self.maxHealth = health
        self.nearBase=near_base
        self.vecteur = vector
        self.threatFor=threat_for

        self.targeted = False
        self.target =None
        self.targetTime = TARGET_TIME_MAX

    def update(self, type, pos, shield_life, is_controlled, health, vector, near_base, threat_for):
        #0: pour un monstre
        #1: pour un de vos héros
        #2: pour un héros de l'adversaire
        self.type = type

        self.pos = pos
        self.shieldLife=shield_life
        self.isControlled=is_controlled
        self.health=health
        self.nearBase=near_base
        self.vecteur = vector
        self.threatFor=threat_for

    def __str__(self):
        return f"ID : {self.id} TYPE : {self.type} health : {self.health}"

# base_x: The corner of the map representing your base
base_x, base_y = [int(i) for i in input().split()]
heroes_per_player = int(input())  # Always 3
myHeroes = {}
opHeroes = {}
monstres = {}
# game loop
while True:
    for i in range(2):
        # health: Your base health
        # mana: Ignore in the first league; Spend ten mana to cast a spell
        health, mana = [int(j) for j in input().split()]
    entity_count = int(input())  # Amount of heros and monsters you can see
    for i in range(entity_count):
        # _id: Unique identifier
        # _type: 0=monster, 1=your hero, 2=opponent hero
        # x: Position of this entity
        # shield_life: Ignore for this league; Count down until shield spell fades
        # is_controlled: Ignore for this league; Equals 1 when this entity is under a control spell
        # health: Remaining health of this monster
        # vx: Trajectory of this monster
        # near_base: 0=monster with no target yet, 1=monster targeting a base
        # threat_for: Given this monster's trajectory, is it a threat to 1=your base, 2=your opponent's base, 0=neither
        _id, _type, x, y, shield_life, is_controlled, health, vx, vy, near_base, threat_for = [int(j) for j in input().split()]
        if _type == TYPE_MY_HERO:
            if _id in myHeroes:
                myHeroes[_id].update( _type, Pos(x, y), shield_life, is_controlled, health, Vector(vx, vy), near_base, threat_for)
            else:
                myHeroes[_id]=Entity(_id, _type, Pos(x, y), shield_life, is_controlled, health, Vector(vx, vy), near_base, threat_for)
                #entities[_id].targeted = False
        if _type == TYPE_MONSTRE:
            if _id in monstres:
                monstres[_id].update( _type, Pos(x, y), shield_life, is_controlled, health, Vector(vx, vy), near_base, threat_for)
            else:
                monstres[_id]=Entity(_id, _type, Pos(x, y), shield_life, is_controlled, health, Vector(vx, vy), near_base, threat_for)
    '''
    for id, entity in myHeroes.items():
        print(str(id)+" "+str(entity), file=sys.stderr, flush=True)
    '''
    for id, entity in monstres.items():
        print(str(id)+" "+str(entity)+" "+str(entity.pos.x)+" "+str(entity.pos.y), file=sys.stderr, flush=True)
    
    for id, hero in myHeroes.items():
        #debug(str(hero))

        # par défaut attendre
        action = "WAIT"#f"MOVE {base_x} {base_y}"

        # si le héro a une cible
        if hero.target != None:
            debug(hero.target)
            target = monstres[hero.target]
            if target.health>0:
                action = f"MOVE {target.pos.x} {target.pos.y}"
                target.targeted = True
                if target.health<target.maxHealth:
                    if hero.targetTime > target.health:
                        hero.targetTime = target.health
                    else:
                        hero.targetTime-=2
                    if hero.targetTime<=0:
                        target.health = 0
                        hero.target = None
                        
            else:
                hero.target = None
            print(f"Hero {hero.id} cible {hero.target}, vie {target.health} ", file=sys.stderr, flush=True)
        else:
            print(f"Hero {hero.id} sans cible ", file=sys.stderr, flush=True)

        # si le héro n'a aucune cible, cherche à affecter une cible
        if "WAIT" in action:
            for id, entity in monstres.items():               
                if entity.targeted == False:
                    # si le monstre cherche à attaquer ma base
                    if entity.nearBase==1 and  entity.threatFor==1:
                        id_near = None
                        distance_min = None
                        for _, hero_near in myHeroes.items():
                            # si le héro n'a aucune cible
                            if hero_near.target == None:
                                if id_near == None:
                                    id_near = hero_near.id
                                    distance_min = hero_near.pos - entity.pos
                                else:
                                    if hero_near.pos - entity.pos < distance_min:
                                        id_near = hero_near.id
                                        distance_min = hero_near.pos - entity.pos

                        # si c'est le héro actuel le plus proche, lui affecte le monstre
                        if id_near == hero.id:                            
                            hero.target=id
                            entity.targeted = True
                            hero.targetTime = entity.maxHealth
                            action = f"MOVE {entity.pos.x} {entity.pos.y}"
        
        if hero.target == None :
            action = f"MOVE {hero.initPos.x} {hero.initPos.y}"

        # Write an action using print
        # To debug: print("Debug messages...", file=sys.stderr, flush=True)


        # In the first league: MOVE <x> <y> | WAIT; In later leagues: | SPELL <spellParams>;
        print(action)
