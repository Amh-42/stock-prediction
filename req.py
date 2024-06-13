with open('requirements.txt') as f:
    lines = f.readlines()
with open('requirements.txt', 'w') as f:
    for line in lines:
        f.write(line.split('==')[0] + '\n')