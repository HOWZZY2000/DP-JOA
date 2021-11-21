## DP-JOA
Join optimization is the process of optimizing the joining, or combining, of two or more tables in a database.  
Here is a join optimization algorithm (JOA) being implemented to find the lowest estimated cost join plan   
for a natural chain join query using dynamic programming (DP).

## Join Constraint
Consider Relations: R0 ⋈ R1 ⋈ R2 whose cardinality is 5, 10, 15 respectively:  
<img src="https://github.com/HOWZZY2000/DP-JOA/blob/master/Readme_Pic/join-tree1.png" width="200" height="200">
### Fullness
Each relation should appear once.
### Cartesian Product-free
No join of two relations that don't share a common column. So the following graph is invalid:  
<img src="https://github.com/HOWZZY2000/DP-JOA/blob/master/Readme_Pic/join-tree2.png" width="200" height="200"> 
### Left Relation Join 
In order for the join be evaluated using HashJoin algorithm later, the relation with smaller cardinalities is on the left.
So the following graph is invalid:  
<img src="https://github.com/HOWZZY2000/DP-JOA/blob/master/Readme_Pic/join-tree3.png" width="200" height="200" >

## Usage

```bash
$ python main.py --query sample
```
For this sample example, there are three relationships, each one with cardinality of 5, 10, 15, 
and R1 has foreign key to R2, R2 has the foreign key to R3. It prints a the lowest cost join tree graph:
~~~ bash
                R0
        JO(5)
                R1
JO(5)
        R2

~~~
Where it indicates a join of R0 and R1 first, with an estimated cardinality of 5, then join it with R2 with a total cardinality of 5.
