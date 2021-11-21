import argparse

from join_graph import *

def printTree(node, level=0):
    if node is not None:
        printTree(node.left, level + 1)
        if node.isLeaf():
            assert(1 == len(node.relations))
            print("\t" * level + node.relations[0].name)
        else:    
            print("\t" * level + "JO(" + str(node.estOutCard) +")")
        printTree(node.right, level + 1)

def parseArgs():
    parser = argparse.ArgumentParser()
    parser.add_argument('--query', required=True)
    return parser.parse_args()

if __name__ == "__main__":
    args = parseArgs()
    joinGraph = JoinGraph("tests/" + args.query + ".in")
    joinOrder = joinGraph.getBestJoinOrder()
    printTree(joinOrder)