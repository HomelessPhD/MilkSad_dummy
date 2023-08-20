
file = open('privkeys_0.txt', 'r')
lines_0 = file.readlines()
file.close()

file = open('privkeys_1.txt', 'r')
lines_1 = file.readlines()
file.close()

file = open('privkeys_2.txt', 'r')
lines_2 = file.readlines()
file.close()

file = open('privkeys_3.txt', 'r')
lines_3 = file.readlines()
file.close()

print(len(set(lines_0)  & set(lines_1)))

print(len(set(lines_0)  & set(lines_2)))

print(len(set(lines_0)  & set(lines_3)))

print(len(set(lines_1)  & set(lines_2)))

print(len(set(lines_1)  & set(lines_3)))

print(len(set(lines_2)  & set(lines_3)))

print(max([len(lines_0),len(lines_1),len(lines_2),len(lines_3)]))


print(len(lines_0), len(set(lines_0)))
print(len(lines_1), len(set(lines_1)))
print(len(lines_2), len(set(lines_2)))
print(len(lines_3), len(set(lines_3)))

