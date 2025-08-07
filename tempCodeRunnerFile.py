# (2) 공백 구분 한 줄
f2 = open('input2.dat', 'r')
parts = f2.readline().split()           # split()이 양쪽 공백 및 \n 자동 제거
student_id, name, kor, eng, math = parts[0], parts[1], int(parts[2]), int(parts[3]), int(parts[4])
print(student_id, name, kor, eng, math)
f2.close()
