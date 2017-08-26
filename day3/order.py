defualtvalue=3
N=30
list1=[]
a=[0 for x in range(int(1+30/8))]

with open ("G:/pythonStduy/day2/a.cfg","rt") as fp:
    for temp in fp.readlines():
        row = temp.split(",")
        for r in row:
            list1.append(int(r))

def clrvalue(i):
    a[i>>defualtvalue] &= ~(1<<(i & (2**defualtvalue-1)))

def setvalue(i):
    a[i>>defualtvalue] |= (1<<(i & (2**defualtvalue-1)))

def getvalue(i):
    return a[i>>defualtvalue] & (1<<(i & (2**defualtvalue-1)))

for i in range(N):
    clrvalue(i)
for i in list1:
    setvalue(i)
for i in range(N):
    if (getvalue(i)):
        print (i)

    
