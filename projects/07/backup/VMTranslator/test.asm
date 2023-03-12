@256
D=A
@R0
M=D

@300
D=A
@R1
M=D

@400
D=A
@R2
M=D

@3000
D=A
@R3
M=D

@3010
D=A
@R4
M=D


// push constant 10
@10 //生成一个整数
D=A
@R0
A=M
M=D
@R0
M=M+1 //放在栈顶，栈指针增加

// push constant 11
@10
D=A
@R0
A=M
M=D
@R0
M=M+1

//sub
@R0
M=M-1
A=M
D=M //取出栈顶的值

@R5
M=D //放入临时变量

@R0
M=M-1
A=M
D=M //取出栈顶的值

@R5
D=D-M //和临时变量里的值相减
@TRUE
D;JEQ //D==0

@R0
A=M
M=0 //fasle 把0写入栈顶
@R0
M=M+1
@FALSE
0;JMP

(TRUE)
@R0
A=M
M=-1 //true 把-1写入栈顶
@R0
M=M+1 
(FALSE)

//add
@R0
M=M-1
A=M
D=M //取出栈顶的值

@R5
M=D //放入临时变量

@R0
M=M-1
A=M
D=M //取出栈顶的值

@R5
D=D+M //和临时变量里的值相加

@R0
A=M
M=D
@R0
M=M+1 //写入栈顶

// push constant 1
@11
D=A
@R0
A=M
M=D
@R0
M=M+1


// pop local 0
@0
D=A
@R1
D=M+D //获取local的地址，base+0

//地址放在临时变量里
@R5 //临时变量段的第一个
M=D

@R0
M=M-1 //栈指针要-1
A=M
D=M //取出栈顶的值

@R5
A=M
M=D //把值放入


// push constant 11
@11
D=A
@R0
A=M
M=D
@R0
M=M+1

// push constant 22
@22
D=A
@R0
A=M
M=D
@R0
M=M+1

// push constant 33
@33
D=A
@R0
A=M
M=D
@R0
M=M+1

// pop argument 2
@2
D=A
@R2
D=M+D //获取 argument 的地址 base+2

//地址放在临时变量里
@R5 //临时变量段的第一个
M=D

@R0
M=M-1 //栈指针要-1
A=M
D=M //取出栈中的值
@R5
A=M
M=D //把值放入


// pop temp 6
@R0
M=M-1 //栈指针要-1
A=M
D=M //取出栈中的值

@R11 //temp 段是从地址5开始的，所以是 base+6
M=D

// push temp 6
@R11 //temp 段是从地址5开始的，所以是 base+6
D=M
@R0
A=M
M=D
@R0
M=M+1 //写入栈顶

// pop static 8
@R0
M=M-1 //栈顶指针要-1
A=M
D=M //取出栈中的值
@test.8 //static 段是从地址16开始的，所以static会按照出现的顺序映射，第一个出现的会放在16，依此类推。因此这里边i和static段地址的顺序不是对应的
M=D

// push argument 2
@2
D=A
@R2
A=M+D
D=M //取出 argument 2 的值
@R0
A=M
M=D
@R0
M=M+1 //写入栈顶

// push pointer 0 (0取R3 1取R4)
@R3
D=M //取出R3的值
@R0
A=M
M=D
@R0
M=M+1 //写入栈顶

// pop pointer 1
@R0
M=M-1 //栈指针要-1
A=M
D=M //取出栈顶
@R4
M=D //写入R4的值
