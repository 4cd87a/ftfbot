import hashlib
hashs = []
end = 0
for i in range(100000):
    hash = hashlib.sha1('{}'.format(i).encode()).hexdigest()[:7]
    for j in range(i):
        if hashs[j]==hash:
            print("Faaaaaaaaaaaalse")
            end = 1
            break
    if end: break
    hashs.append(hash)
    print("{} was checked".format(i))

print('end')