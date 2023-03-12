// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Fill.asm

// Runs an infinite loop that listens to the keyboard input.
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel;
// the screen should remain fully black as long as the key is pressed. 
// When no key is pressed, the program clears the screen, i.e. writes
// "white" in every pixel;
// the screen should remain fully clear as long as no key is pressed.

// Put your code here.


// n=(256*512)/16
// n=8192
// while:
//      @KBD
//      k_addr=A
//      k_vale=M
//      if k_value == 0:
//              white
//              for(i=0;i<n;i++):
//                  addr[screen+i]=0
//      else:
//              black
//              for(i=0;i<n;i++):
//                  addr[screen+i]=-1

(LOOP)
    @KBD
    D=M
    @R1
    M=-1
    @RENDER
    D;JNE
    @R1
    M=0
    @RENDER
    D;JEQ
    @LOOP
    0;JMP

(RENDER)
    @i
    M=0
    (LOOP1)
        @i
        D=M
        @8191
        D=A-D
        @LOOP
        D;JEQ
        ///
        @SCREEN
        D=A
        @i
        D=D+M
        @R2
        M=D
        @R1
        D=M
        @R2
        A=M
        M=D
        ///
        @i
        M=M+1
        @LOOP1
        0;JMP