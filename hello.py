# 202001, 홍길동, 94, 88, 76
f1 = open('input1.dat', 'r')
line = f1.readline().rstrip()         
parts = line.split(',')                
student_id = parts[0]
name       = parts[1].strip()         
kor        = int(parts[2])
eng        = int(parts[3])
math       = int(parts[4])
print(student_id, name, kor, eng, math)
f1.close()


# 202001 홍길동 94 88 76
f2 = open('input2.dat', 'r')
parts = f2.readline().split()         
student_id, name, kor, eng, math = parts[0], parts[1], int(parts[2]), int(parts[3]), int(parts[4])
print(student_id, name, kor, eng, math)
f2.close()


# 202001
# 홍길동
# 94
# 88
# 76
f3 = open('input3.dat', 'r')
student_id = f3.readline().rstrip()
name       = f3.readline().rstrip()
kor        = int(f3.readline())
eng        = int(f3.readline())
math       = int(f3.readline())
print(student_id, name, kor, eng, math)
f3.close()