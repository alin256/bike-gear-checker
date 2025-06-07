import math

from cassetes_constants import cassettes
eps_change_up = 0.0
unavailable_set = set()
max_cassete_size = 9
# unavailable_set = set([9, 29, 31, 33, 35, 37, 38, 39, 41, 43, 45, 47, 48, 49, 51])

for rpm in range(65,90,5):
    mult = float(rpm+5)/float(rpm-5)+eps_change_up
    cogs = [11]
    for i in range(1,13):
        next_cog = (math.floor(cogs[i-1]*mult))
        while next_cog in unavailable_set:
            next_cog += 1
        cogs.append(next_cog)
        if next_cog >= 34:
            break

    print(f'cadnece range  {rpm-5}-{rpm+5}: {len(cogs)}x cogs:{cogs}')

    max_match = 0
    best_cassete = "n/a"
    for cassette in cassettes:
        cassete_cogs = cassettes[cassette]
        if len(cassete_cogs) > max_cassete_size:
            continue
        match = len(cassete_cogs)
        for i in range(min(len(cassete_cogs), len(cogs))):
            if cassete_cogs[i] != cogs[i]:
                match = i
                break
        if match > max_match:
            max_match = match
            best_cassete = cassette

    print(f'best match set {rpm - 5}-{rpm + 5}: {len(cassettes[best_cassete])}x cogs:{cassettes[best_cassete]} ')
    print(f'{best_cassete}, match {max_match}\n')
