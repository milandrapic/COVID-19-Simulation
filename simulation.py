import pygame
import random
import networkx as nx
import matplotlib.pyplot as plt
from enum import Enum
import pydot
from networkx.drawing.nx_pydot import graphviz_layout
# import os
# os.environ["SDL_VIDEODRIVER"] = "dummy"


G=nx.DiGraph(name='G')
P=nx.Graph(name='P')
random.seed(534543642221)#378
# constants
WIDTH, HEIGHT = 900,900
WIN = pygame.display.set_mode([WIDTH, HEIGHT])
WHITE = (255,255,255)
FPS = 100
NODES = 99
NODE_SIZE = 20
INITIAL_INFECTIONS = 1
RECOVERY_TIME = 750
IMMUNITY = 0.95
TS = 300
class Vulnerability(Enum):
    LOW = [(10,15),(0.97,1), (500,100), (0,255,0)]
    MEDIUM = [(15,35),(0.93,0.97), (750,150), (0,128,255)]
    HIGH = [(35,40),(0.9,0.93), (1000,300),(255,128,0)]

def get_vulnerability(i):
#     p = random.normalvariate(0.5, 0.125)
    p = random.random()
#     if(p<0.333333):
#         return Vulnerability.LOW
#     elif(p<0.666666):
#         return Vulnerability.MEDIUM
#     else:
#         return Vulnerability.HIGH
    if(i<33):
        return Vulnerability.MEDIUM
    elif(i<66):
        return Vulnerability.LOW
    else:
        return Vulnerability.HIGH


class Node(pygame.sprite.Sprite):
    def __init__(self, pos_x,pos_y,id):
        super().__init__()
        self.id = id
        self.vulnerability = get_vulnerability(self.id)
        self.width = random.randint(self.vulnerability.value[0][0],self.vulnerability.value[0][0])
        self.image = pygame.Surface([self.width, self.width])
        self.image.fill(self.vulnerability.value[3])
        # self.image.fill((0,0,255))
        self.rect = self.image.get_rect()
        self.rect.center = [pos_x, pos_y]
        self.destination = (random.randint(0,WIDTH),random.randint(0,HEIGHT))
        self.reached_x = False
        self.reached_y = False
        self.infected = False
        self.recovered = False
        self.days_infected = -1
        self.immunity = random.uniform(self.vulnerability.value[1][0],self.vulnerability.value[1][1])
        # self.recovery_time = RECOVERY_TIME
        self.recovery_time = random.randint(self.vulnerability.value[2][0]-self.vulnerability.value[2][1],self.vulnerability.value[2][0]+self.vulnerability.value[2][1])
        # print(self.vulnerability)
        # print(self.immunity)
        # print(self.recovery_time)
        # if self.width in range(31,40):
        #     self.immunity = random.uniform(0.90,0.933)
        # if self.width in range(21,31):
        #     self.immunity = random.uniform(0.933,0.966)
        # if self.width in range(11,21):
        #     self.immunity = random.uniform(0.966,0.99)
        #     if self.width in range(5,11):
        #         self.immunity = random.uniform(0.99,0.9975)
        # self.radius = width/2
        # self.image.set_alpha(120)
        # pygame.draw.circle(self.image, (0,255,0), (self.radius,self.radius), 2)
    
    def infect(self, received_from):
        self.infected = True
        self.image.fill((255,0,0))
        # pygame.draw.circle(self.image, (0,255,0), (self.radius,self.radius), 2)
        if received_from == None:
            G.add_node(self.id, data = self)
        else:
            if not G.has_node(received_from.id):
                G.add_node(received_from.id, data = received_from)
            if not G.has_node(self.id):
                G.add_node(self.id, data = self)
            G.add_edge(received_from.id,self.id)
            P[received_from.id][self.id]['color'] = 'red'
    
    def recover(self):
        self.infected = False
        self.recovered = True
        self.image.fill((0,0,0))
        self.immunity = 2
        # pygame.draw.circle(self.image, (0,255,0), (self.radius,self.radius), 2)
        

pygame.init()

all_nodes = []

def main():
    
    # variable initialization
    t = 0
    nodes = []
    node_group = pygame.sprite.Group()
    infected_nodes = []
    recovered_nodes = []
    i_nodes = []
    r0 = []
    infections_ts = []
    for i in range(NODES):
        obj = Node(random.randint(0,WIDTH),random.randint(0,HEIGHT),i)
        if i < INITIAL_INFECTIONS:
            obj.infect(None)
            infected_nodes.append(obj)
            i_nodes.append(obj.id)
        node_group.add(obj)
        nodes.append(obj)
#         print(len(nodes))
    
    running = True
    clock = pygame.time.Clock()
    all_nodes = nodes
    # running loop
    
    def save_g(time):
        color_map = []
        for node in G:       
            node = G.nodes[node]['data']
            if node.recovered:
                color_map.append('green')
            else:
                color_map.append('red')
        # pos = graphviz_layout(G, prog="twopi")
        plt.figure(figsize=(10,10))
        print(time)
        plt.title('t = '+str(t)+' | R0 = ' + str(round(get_R0(),3)))
#         nx.draw(G,pos, node_color=color_map, with_labels = True)
        nx.draw(G, node_color=color_map, with_labels = True)
#         nx.draw(G,pos, node_color=color_map)
        plt.savefig('images/propagation'+str(int(time))+'.png')
        plt.clf()
        
    def r0_graph():
        print(r0)
        ts = [x for x, y in r0]
        data = [y for x, y in r0]
        (ax1, ax2) = plt.subplots(ncols=1, figsize=(10, 10))
        plt.plot(ts,data)
        plt.title("R0 values")
        ax2.set_xlabel('Time Stamp')
        ax2.set_ylabel('R0')
        plt.savefig("images/r0.png")
        plt.show()
    def infections_graph():
        print(infections_ts)
        ts = [x for x, y in infections_ts]
        data = [y for x, y in infections_ts]
        (ax1, ax2) = plt.subplots(ncols=1, figsize=(10, 10))
        plt.plot(ts,data)
        plt.title("Infections Over Time")
        ax2.set_xlabel('Time Stamp')
        ax2.set_ylabel('Infections')
        plt.savefig("images/infections.png")
        plt.show()
    
    while running:
        if len(infected_nodes) == 0:
            save_g(t)
            r0_graph()
            infections_graph()
            running = False
            pygame.quit()
            post_quit()
            exit()
            
        if (t % TS) == 0:
#             print(t)
            save_g(t)
        if (t % 100) == 0:
#             print(t)
            r0.append((t,round(get_R0(),3)))
            infections_ts.append((t,len(infected_nodes)))
        t+=1
        # event loop
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                post_quit()
                exit()
        
        def proximity_add_edge(n1,n2):
            if n1.id==n2.id:
                return
            if not P.has_edge(n1.id,n2.id):
                if not P.has_node(n1.id):
                    P.add_node(n1.id, data = n1)
                if not P.has_node(n2.id):
                    P.add_node(n2.id, data = n2)
                P.add_edge(n1.id,n2.id)
                P[n1.id][n2.id]['weight'] = 1
                P[n1.id][n2.id]['color'] = 'grey'
                
            elif P.has_edge(n1.id,n2.id):
                P[n1.id][n2.id]['weight'] += 1
                


        
        # collisions and infections
        to_infect = []
        
        for node in nodes:
            collisions = pygame.sprite.spritecollide(node, node_group, False)
            if len(collisions) > 1:
                for i in range(len(collisions)):
                    proximity_add_edge(node,collisions[i])
                    # add edge to proximity graph
        
        for infected in infected_nodes:
            collisions = pygame.sprite.spritecollide(infected, node_group, False)
            if len(collisions) > 1:
                for i in range(len(collisions)):
                    # add edge to proximity graph
                    if (not collisions[i].infected and not collisions[i].recovered) and random.random() >= collisions[i].immunity:
                        to_infect.append((infected,collisions[i]))
        

                    


        for n in to_infect:
            n[1].infect(n[0])
            infected_nodes.append(n[1])
            i_nodes.append(n[1].id)
        # print(i_nodes)

        # node recovery
        for n in infected_nodes:
            if n.days_infected >= n.recovery_time:
                n.recover()
                infected_nodes.remove(n)
                recovered_nodes.append(n)
            else:
                n.days_infected += 1

        # graphics
        WIN.fill(WHITE)
        for n in node_group:
            if n.rect.center[0] != n.destination[0] and n.reached_x==False:
                n.rect.right += (n.destination[0]-n.rect.center[0])/abs(n.destination[0]-n.rect.center[0])
            else:
                n.reached_x = True
            if n.rect.center[1] != n.destination[1] and n.reached_y==False:
                n.rect.bottom += (n.destination[1]-n.rect.center[1])/abs(n.destination[1]-n.rect.center[1])
            else:
                n.reached_y = True
            if n.reached_x and n.reached_y:
                n.destination = (random.randint(0,WIDTH),random.randint(0,HEIGHT))
                n.reached_x = n.destination[0] == n.rect.center[0]
                n.reached_y = n.destination[1] == n.rect.center[1]

        node_group.draw(WIN)
        pygame.display.flip()
        clock.tick(FPS)

def post_quit():
    draw_G()
    draw_P()
    r0 = get_R0()
    print_vulnerabilities(G)
    print_vulnerabilities(P)
    print('R0 = ' + str(round(r0,2)))
    cd = clustering_degree()
    print('Average Degree for High Vulnerability: ' + str(avg_degree(cd['h'])))
    print('Average Clustering for High Vulnerability: ' + str(avg_clustering(cd['h'])))
    print('Average Degree for Medium Vulnerability: ' + str(avg_degree(cd['m'])))
    print('Average Clustering for Medium Vulnerability: ' + str(avg_clustering(cd['m'])))
    print('Average Degree for Low Vulnerability: ' + str(avg_degree(cd['l'])))
    print('Average Clustering for Low Vulnerability: ' + str(avg_clustering(cd['l'])))
    print(G.number_of_nodes())
    print(G.number_of_edges())
    print(P.number_of_nodes())
    print(P.number_of_edges())
    print("Global Clustering for gcer1: "+str(round(nx.average_clustering(G),3)))
    print("Global Clustering for gcer1: "+str(round(nx.average_clustering(P),3)))
    print((G.number_of_edges())/G.number_of_nodes())
    print((2*P.number_of_edges())/99)


def print_vulnerabilities(G):
    h = 0
    m = 0
    l=0

    for n in G:
#         print(G.nodes[n]['data'].vulnerability)
        if G.nodes[n]['data'].vulnerability == Vulnerability.HIGH:
            h += 1
        elif G.nodes[n]['data'].vulnerability == Vulnerability.MEDIUM:
            m+= 1
        else:
            l += 1
    g_name = ' for infected nodes:'
    if G.name == 'P':
        g_name = ' for all nodes in model: '
    print('Vulnerabilities' + g_name)
    print('number of high vulnerability nodes: ' + str(h))
    print('number of medium vulnerability nodes: ' + str(m))
    print('number of low vulnerability nodes: ' + str(l))
    print('\n')
    

def avg_clustering(a):
    i = 0
    c = 0
    for n in a:
        n = n[0]
        i += 1
        c += n
    if i == 0:
        return -1
    return round(c/i,4)

def avg_degree(a):
    i = 0
    d = 0
    for n in a:
        n = n[1]
        if n < 0:
            continue
        i += 1
        d += n
    if i == 0:
        return -1
    return round(d/i,4)


def draw_G():
    color_map = []
    for node in G:       
        node = G.nodes[node]['data']
        if node.vulnerability == Vulnerability.HIGH:
            color_map.append('orange')
        elif node.vulnerability == Vulnerability.MEDIUM:
            color_map.append('#0080FF')
        else:
            color_map.append('green')
    # pos = graphviz_layout(G, prog="twopi")
    plt.figure(figsize=(10,10))
    # nx.draw(G,pos, node_color=color_map, with_labels = True)
    nx.draw(G, node_color=color_map, with_labels = True)
    plt.savefig("images/propagation.png")
    plt.show()

def draw_P():
    color_map = []
    for node in P:       
        node = P.nodes[node]['data']
        if node.vulnerability == Vulnerability.HIGH:
            color_map.append('orange')
        elif node.vulnerability == Vulnerability.MEDIUM:
            color_map.append('#0080FF')
        else:
            color_map.append('green')
    colors = [P[u][v]['color'] for u,v in P.edges()]
    plt.figure(figsize=(12,12))
    nx.draw(P, node_color=color_map, edge_color=colors, with_labels = True)
    plt.savefig("images/proximity.png")
    plt.show()

# def get_R0():
#     ln = 0 
#     e = 0
#     nii = 0
#     for n in G.nodes:
#         if G.out_degree(n) == 0 and G.nodes[n]['data'].infected :
#             nii+=1
#             ln+=1
#         elif G.nodes[n]['data'].infected:
#             nii+=1
#             e += G.out_degree(n)
#     if ((nii - ln)) ==0:
#         return 0
# #     return G.number_of_edges()/(G.number_of_nodes())
# #     return G.number_of_edges()/(G.number_of_nodes() - ln)
#     print('e: ' + str(e))
#     print('nii: ' + str(nii))
#     print('ln: ' + str(ln))
#     print('e/(nii - ln): ' +str(round(e/(nii - ln),3)))
#     return e/(nii - ln)

def get_R0():
    ln = 0 
    e = 0
    nii = 0
    for n in G.nodes:
        if float(G.nodes[n]['data'].days_infected/G.nodes[n]['data'].recovery_time)<0.5 and G.nodes[n]['data'].infected:
            nii+=1
            ln+=1
#         else:
        elif G.nodes[n]['data'].infected:
            nii+=1
            e += G.out_degree(n)
    if ((nii - ln)) ==0:
        return 0
#     return G.number_of_edges()/(G.number_of_nodes())
#     return G.number_of_edges()/(G.number_of_nodes() - ln)
    print('e: ' + str(e))
    print('nii: ' + str(nii))
    print('ln: ' + str(ln))
    print('e/(nii - ln): ' +str(round(e/(nii - ln),3)))
    return e/(nii - ln)

def clustering_degree():
    h = []
    m = []
    l = []
    cluster = nx.clustering(P)
#     print(cluster)
    for node in P:       
        node = P.nodes[node]['data']
        c = cluster[node.id]
        d = -1
        try:
            d = G.out_degree(node.id)
        except:
            d = -1

        if node.vulnerability == Vulnerability.HIGH:
            h.append((c,d))
        elif node.vulnerability == Vulnerability.MEDIUM:
            m.append((c,d))
        else:
            l.append((c,d))
    print('High Vulnerability Proximity Clustering & Propagation Degree:')
    for n in h:
        print('clustering: ' + str(n[0]) + ' | degree: ' + str(n[1]))
    print('Medium Vulnerability Proximity Clustering & Propagation Degree:')
    for n in m:
        print('clustering: ' + str(n[0]) + ' | degree: ' + str(n[1]))
    print('Low Vulnerability Proximity Clustering & Propagation Degree:')
    for n in l:
        print('clustering: ' + str(n[0]) + ' | degree: ' + str(n[1]))
    return {'h':h,'m':m,'l':l}

# if __name__ == "__main__":
#     main()
main()