import math

for rpm in range(65,90,4):
    mult = float(rpm+5)/float(rpm-5)
    cogs = [11]
    for i in range(1,12):
        cogs.append(math.floor(cogs[i-1]*mult))
    print(f'cadnece range {rpm-5}-{rpm+5}: cogs:{cogs}')