
class JoinGraph:
    """
    A class used to represent a join graph

    Fields
    -----------
    relations : [Relation]
        all join relations specified in the input file
    joinConditions : [JoinCondition]
        all join conditions specified in the input file
    """

    relations = None
    joinConditions = None
    
    def __init__(self, path : str) -> None:
        with open(path, "r") as f:
            lines = f.readlines()
            self._load(lines)
    
    def getBestJoinOrder(self):
        """
        Compute the join order with lowest cost.
        Return : JoinPlan
            root of the join tree
        """
        n = len(self.relations)
        # initilize the None part of the matrix
        s = [[None for i in range(j)] for j in range(n)]
        # add single join plans
        for i in range(n):
            s[i].append(JoinPlan(None, None, [self.relations[i]], self.relations[i].cardinality))
        # add consecutive join plans
        for i in range(n-1):
            lt = s[i][i] < s[i+1][i+1]
            s[i].append(JoinPlan(s[i][i] if lt else s[i+1][i+1],
                                 s[i][i] if not lt else s[i+1][i+1],
                                 s[i][i].relations + s[i+1][i+1].relations if lt
                                 else s[i+1][i+1].relations + s[i][i].relations,
                                 self._getCardinality(s[i][i].relations + s[i+1][i+1].relations)))
        for numRels in range(3, n+1):
            iMax = n - numRels + 1
            for i in range(iMax):
                j = numRels - 1 + i
                if j >= n: break
                T = []
                for k in range(i, j):
                    lt = s[i][k] < s[k+1][j]
                    c = self._getCardinality(s[i][k].relations + s[k+1][j].relations if lt
                                             else s[k+1][j].relations + s[i][k].relations)
                    T.append(JoinPlan(s[i][k] if lt else s[k+1][j],
                                      s[i][k] if not lt else s[k+1][j],
                                      s[i][k].relations + s[k+1][j].relations if lt
                                      else s[k+1][j].relations + s[i][k].relations, c))
                T.sort(key = lambda plan: plan.estCost)
                s[i].append(T[0])
        # print('\n'.join(' '.join(map(str, sub)) for sub in s))
        return s[0][n-1]

    def _load(self, lines : list) -> None:
        """
        Inject join relations and conditions
        """
        assert(len(lines) >= 3)
        numRelations = int(lines[0])
        self.relations = [None] * numRelations
        # inject join relations
        cardinalities = lines[1].split(",")
        assert(len(cardinalities) == numRelations)
        relationNameIdxMap = {}
        for i in range(numRelations):
            relationName = "R" + str(i)
            self.relations[i] = Relation(relationName, i, int(cardinalities[i]))
            relationNameIdxMap[relationName] = i
        # inject foreign keys
        foreignRelationNames = lines[2].split(",")
        assert(len(foreignRelationNames) == numRelations - 1)
        self.joinConditions = [None] * (numRelations - 1)
        for i in range(numRelations - 1):
            foreignRelationIdx = relationNameIdxMap[foreignRelationNames[i]]
            if i == foreignRelationIdx:
                self.joinConditions[i] = JoinCondition(self.relations[i+1], self.relations[i])
            elif i + 1 == foreignRelationIdx:
                self.joinConditions[i] = JoinCondition(self.relations[i], self.relations[i+1])
            else:
                assert(False)

    def _getCardinality(self, inRelations : list) -> int:
        """
        Compute cardinality given a list of join relations
        Input: [Relation]
        Output: int
            estimated output cardinality of given join relations
        """
        assert(len(inRelations) >= 2)
        inRelations.sort(key = lambda x : x.idx)
        cardinality = inRelations[0].cardinality
        for i in range(1, len(inRelations)):
            cardinality *= inRelations[i].cardinality
            if inRelations[i - 1].idx + 1 == inRelations[i].idx:
                joinCondition = self.joinConditions[inRelations[i - 1].idx]
                cardinality /= joinCondition.foreignRelation.cardinality
            else:
                print("[Warning] Estimating join relations containing Cartesian Product.")
        return cardinality

    def __str__(self) -> str:
        return "\n".join([str(r) for r in self.relations]) + "\n" + "\n".join([str(j) for j in self.joinConditions])

class Relation:
    """
    A class used to represent base relation table
    
    Fields
    -----------
    name : str
        name of the relation
    idx  : int
        index of the relation generated during injection
    cardinality : int
        cardinality of the relation
    """

    name = None
    idx = None
    cardinality = None

    def __init__(self, name : str, idx : int, cardinality : int) -> None:
        self.name = name
        self.idx = idx
        self.cardinality = cardinality
    
    def __str__(self) -> str:
        """
        Represent relation in the format of name(idx):cardinality
        E.g. A(0):50
        """
        return self.name + "(" + str(self.idx) + "):" + str(self.cardinality)

class JoinCondition:
    """
    A class used to track foreign key for chain joins

    Fields
    -----------
    primaryRelation : Relation
        relation containing primary key
    foreignRelation : Relation
        relation containing foreign key
    """
    
    primaryRelation = None
    foreignRelation = None
    
    def __init__(self, primaryRelation : Relation, foreignRelation : Relation) -> None:
        self.primaryRelation = primaryRelation
        self.foreignRelation = foreignRelation
    def __str__(self) -> str:
        return "Primary Relation: " + str(self.primaryRelation) \
               + "\n" + "Foreign Relation: " + str(self.foreignRelation) + "\n"

class JoinPlan:
    """
    A class used to represent a logical join tree

    Fields
    -----------
    left : JoinPlan
        left child
    right : JoinPlan
        right child
    relations : [Relation]
        join relations matched in the join tree
    estOutCard : int
        estimated output cardinality of the join tree
    estCost : int
        cost of the join tree
    """
    
    left = None
    right = None
    relations = None
    estOutCard = 0
    estCost = 0

    def __init__(self, left, right, relations : list, estOutCard : int) -> None:
        self.left = left
        self.right = right
        self.relations = relations
        self.estOutCard = int(estOutCard)
        if self.isLeaf():
            self.estCost = 0
        else:
            self.estCost = left.estCost + right.estCost + self.estOutCard

    def isLeaf(self) -> bool:
        """
        Check if this is the leaf
        """
        return self.left is None and self.right is None

    def __gt__(self, other):
        return self.estOutCard > other.estOutCard

    def __str__(self) -> str:
        return "relations: " + ",".join([str(r) for r in self.relations]) + \
               " estOutCard: " + str(self.estOutCard) + " estCost: " + str(self.estCost) + "\n"





