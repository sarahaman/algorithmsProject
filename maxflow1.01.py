##############################################
#                        __ _                #
#                       / _| |               #
#  _ __ ___   __ ___  _| |_| | _____      __ #
# | '_ ` _ \ / _` \ \/ /  _| |/ _ \ \ /\ / / #
# | | | | | | (_| |>  <| | | | (_) \ V  V /  #
# |_| |_| |_|\__,_/_/\_\_| |_|\___/ \_/\_/   #
#                                            #
##############################################

import pandas as pd
import numpy as np

def maxFlow(flights, aggType, carriers = False):
    '''
    Main function, takes a dataframe, an aggregation type for flights and a carriers argument
    
    flights: Pandas dataframe of flight flight and airport info
    
    aggType: 'Max' takes the largest available planes for each flight,
                'Sum' takes all available planes to makes flights
                
    carriers: defaults to False, True solves the problem for best carrier
    
    '''
    
    def groupPaths(flights):
        '''
        
        Aggregates dataframe of flights by sum of all available planes
        or the largest available plame, then outputs an edgelist of airport to 
        aiport with passenger limit as the capacity
        
        '''
        if aggType == 'Sum':
            grouped = flights.groupby(['Source','Destination']).agg({'Capacity': ['sum']})
            grouped.columns = ['Total_capacity']
            grouped = grouped.reset_index()
    
            sum_flights = []
        
            for index, row in grouped.iterrows():
                sum_flights.append([row['Source'], row['Destination'], int(row['Total_capacity'])])
            return sum_flights
        
        if aggType == 'Max':
            grouped = flights.groupby(['Source','Destination']).agg({'Capacity': ['max']})
            grouped.columns = ['Total_capacity']
            grouped = grouped.reset_index()
    
            max_flights = []
        
            for index, row in grouped.iterrows():
                max_flights.append([row['Source'], row['Destination'], int(row['Total_capacity'])])
            return max_flights
        else:
            pass
    
    def trimEdgelist(el, sources, sinks):
        '''
        
        Takes an edgelist, a list of source nodes and a list of sink nodes to retain
        
        Trims the edgelist and outputs a new edgelist that contains only edges
        that start with the sources input, or nodes that end with the sinks input
        
        '''
        new_el = []
        
        for i in el:
            if (i[0] in sources) or (i[1] in sinks):
                new_el.append(i)
        
        return new_el

    def superSourceSink(sources, sinks):
        '''
        
        Takes a list of source nodes and a list of sink nodes
        
        Creates a "Super source" node with infinte capacities feeding into each
        of the source nodes.
        
        Creates a "Super sink" node with infinite capacieties being fed into by
        each of the sink nodes
        
        Appends these values to, and outputs, the edgelist
        
        '''
        out = []
        for i in sources:
            out.append(['Super Source',i,np.inf])
        for i in sinks:
            out.append([i,'Super Sink',np.inf])
        
        return out
    
    def createDict(el):
        '''
        
        Creates a dictionary with these constraints:
            
            key: the airport id
            value: unique int to represent the airport
            
        This is for use in an adjacency matrix/graph
        
        '''
        airports = []
        
        for i in el:
            for j in i:
                if (type(j) == str) and j not in airports:
                    airports.append(j)
        
        numbers = list(range(len(airports)))
        airportDict = dict(zip(airports, numbers))
        
        return airportDict
    
    def newEL(el):
        '''
        Duplicates the airport edgelist, but uses the new integer identifiers
        
        '''
        new_el = []
        
        for i in el:
            edge = []
            for j in i:
                if type(j) == str:
                    edge.append(airportDict[j])
                else:
                    edge.append(j)
            new_el.append(edge)     
        
        return new_el
    
    def display(A):
        '''
        
        Creates a zeros matrix, size (number of nodes) by (number of nodes)
        
        Appends the nodes to their locations with their respective capacity values
        
        Prints the solution for most people that can travel from New York to San Francisco
        
        Else, returns the max flow using Ford Fulkerson if solving for the best carrier
        
        '''
        
        A = np.zeros((len(airportDict),len(airportDict)), dtype =float)
        
        for i in newEL(el):
            A[i[0]][i[1]] = i[2]
        
        g = Graph(A)
        
        if (aggType == 'Max') and (carriers == False):
            print("The maximum passengers that can fly from New York to San Francisco utilizing a single plane is: %d " % 
                  g.FordFulkerson(airportDict['Super Source'], airportDict['Super Sink']))
            print()
            
        if (aggType == 'Sum') and (carriers == False):
            print("The maximum passengers that can fly from New York to San Francisco utilizing every availible plane is: %d " % 
                  g.FordFulkerson(airportDict['Super Source'], airportDict['Super Sink']))
            print()
            
        else:
            return g.FordFulkerson(airportDict['Super Source'], airportDict['Super Sink'])
    
    def carriersList(flights):
        '''
        Instantiates a list of each unique airline from the flights dataframe
        
        '''
        return set(list(flights['Airline']))
    
    def trimCarriers(flights, airline):
        '''
        Filters out the fligths that not offered by specified airline
        
        '''
        carrier_flights = flights[flights['Airline'] == airline]
        return carrier_flights
    
        
    ###########################################################################
    
    if carriers == False:
        el= trimEdgelist(groupPaths(flights), ['JFK','LGA','EWR'], ['STC','OAK','STS','SFO'])
        supers= superSourceSink(['JFK','LGA','EWR'], ['STC','OAK','STS','SFO'])
        
        for i in supers:
            el.append(i)
        
        airportDict = createDict(el)
        display(el)
        
    if carriers == True:
        bestAirline = ''
        bestAirlineNumber = 0
        
        for i in carriersList(flights):
            el = trimEdgelist(groupPaths(trimCarriers(flights, i)), ['JFK','LGA','EWR'], ['STC','OAK','STS','SFO'])
            supers= superSourceSink(['JFK','LGA','EWR'], ['STC','OAK','STS','SFO'])
            
            for j in supers:
                el.append(j)
                
            airportDict = createDict(el)
            passengers = display(el)
            
            if passengers > bestAirlineNumber:
                bestAirline = i
                bestAirlineNumber = passengers
                
        if aggType == 'Sum':
            print("The airline with that can transport the most people using all available planes is: "+
                  str(bestAirline))
            print()
            print("The total people that can be transported is: " + str(int(bestAirlineNumber)))
            print()
        if aggType == 'Max':
            print("The airline with that can transport the most people using their largest available planes is: "+
                  str(bestAirline))
            print()
            print("The total people that can be transported is: " + str(int(bestAirlineNumber)))
            print()
            
    
    ###########################################################################

class Graph: 
    
    def __init__(self,graph): 
        '''
        Graph class
   
        Takes a matrix as argument and initiates a graph

        '''
        self.graph = graph
        self. ROW = len(graph) 
          
    def BFS(self,s, t, parent): 
        '''
        Implements breadth first search
        '''
        visited =[False]*(self.ROW) 
           
        queue=[] 
          
        queue.append(s) 
        visited[s] = True
           
        while queue:
  
            u = queue.pop(0) 
          
            for ind, val in enumerate(self.graph[u]): 
                if visited[ind] == False and val > 0 : 
                    queue.append(ind) 
                    visited[ind] = True
                    parent[ind] = u 

        return True if visited[t] else False
              
    def FordFulkerson(self, source, sink): 
        '''
        Implements Ford Fulkerson on a graph, taking the given source and sink,
        
        Returns the maximum flow for the given source to sink pair
        
        '''
        parent = [-1]*(self.ROW) 
  
        max_flow = 0
  
        while self.BFS(source, sink, parent) : 

            path_flow = float("Inf") 
            s = sink
            while(s !=  source): 
                path_flow = min (path_flow, self.graph[parent[s]][s]) 
                s = parent[s] 
  
            max_flow +=  path_flow 

            v = sink 
            while(v !=  source): 
                u = parent[v] 
                self.graph[u][v] -= path_flow 
                self.graph[v][u] += path_flow 
                v = parent[v] 
  
        return max_flow

if __name__ == '__main__':
    
    maxEL = pd.read_csv('path/to/flights_edgelist2.csv')
    
    maxFlow(maxEL, 'Max')
    maxFlow(maxEL, 'Sum')
    maxFlow(maxEL, 'Max', True)
    maxFlow(maxEL, 'Sum', True)