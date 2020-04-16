import numpy as np
x=np.array([3,5])
y=np.array([4,2])
# 两个向量
Lx=np.sqrt(x.dot(x))
Ly=np.sqrt(y.dot(y))
#相当于勾股定理，求得斜线的长度
cos_angle=x.dot(y)/(Lx*Ly)
#求得cos_sita的值再反过来计算，绝对长度乘以cos角度为矢量长度，初中知识。。
print(cos_angle)
angle=np.degrees(np.arccos(cos_angle))
# angle2=angle*360/2/np.pi
#变为角度
print(angle)
#x.dot(y) =  y=∑(ai*bi)
print(np.cos(30))
print(np.cos(-30))



