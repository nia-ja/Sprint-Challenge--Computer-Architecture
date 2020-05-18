"""CPU functionality."""

import sys

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256 #ram 00-FF (256 bytes of memory)
        self.reg = [0] * 8 #registers
        self.pc = 0 #program counter/current instruction
        self.sp = 7 #location of stack pointer in registers
        self.FL = [0] * 8
        self.less = 0
        self.greater = 1
        self.equal = 2
        self.reg[self.sp] = 0xF4 #initialize stack pointer
        self.branchtable = {} #cpu instruction set and their methods
        self.branchtable[0b10000010] = self.LDI
        self.branchtable[0b01000111] = self.PRN

        self.branchtable[0b10100010] = self.MUL
        self.branchtable[0b10100000] = self.ADD
        self.branchtable[0b10100001] = self.SUB

        self.branchtable[0b00000001] = self.HLT
        self.branchtable[0b01000101] = self.PUSH
        self.branchtable[0b01000110] = self.POP
        self.branchtable[0b01010000] = self.CALL
        self.branchtable[0b00010001] = self.RET

        self.branchtable[0b10100111] = self.CMP
        self.branchtable[0b01010100] = self.JMP
        self.branchtable[0b01010101] = self.JEQ
        self.branchtable[0b01010110] = self.JNE
        self.running = False #interrupt status

    def load(self, program):
        """Load a program into memory."""
        #strip out all function instructions
        instructions = []
        for line in program:
            line = line.strip()
            # ignore everything after a #, since that's a comment
            instruction = line.split('#')[0]
            # print(instruction)
            if instruction == '':
                continue
            # convert the binary strings to integer values to store in RAM
            # int(x, base)
            # x - a number or string to be converted to integer object
            # base - Number format. Default value: 10
            instructions.append(int(instruction, 2))
            # print(instructions)
        # if there's no instructions -> halt
        if not len(instructions):
            self.halted = True
        #insert instructions into ram
        address = 0

        for instruction in instructions:
            self.ram[address] = instruction
            address += 1

    ## Add method ram_read() and ram_write() that access the RAM inside the CPU object
    ## ram_read() should accept the address to read and return the value stored there
    def ram_read(self, MAR): #memory address register
         return self.ram[MAR] # the Memory Address Register (MAR) - contains the address that is being read or written to.

    ## ram_write() should accept a value to write, and the address to write it to
    def ram_write(self, MAR, MDR):
        self.ram[MAR] = MDR # the Memory Data Register (MDR) - contains the data that was read or the data to write
        
    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        elif op == 'SUB':
            self.reg[reg_a] -= self.reg[reg_b]
        elif op == 'MUL':
            self.reg[reg_a] *= self.reg[reg_b]
        else:
            raise Exception("Unsupported ALU operation")
    
    # instructions from run()
    def LDI(self):
        self.reg[self.ram_read(self.pc+1)] = self.ram_read(self.pc+2)
        self.pc += 3

    def PRN(self):
        print(self.reg[self.ram_read(self.pc+1)])
        self.pc += 2

    def HLT(self):
        self.running = False

    def MUL(self):
        reg_a = self.ram_read(self.pc+1)
        reg_b = self.ram_read(self.pc+2)
        self.alu('MUL', reg_a, reg_b)
        self.pc += 3

    def SUB(self):
        reg_a = self.ram_read(self.pc + 1)
        reg_b = self.ram_read(self.pc + 2)
        self.alu("SUB", reg_a, reg_b)
        self.pc += 3

    def PUSH(self, MDR=None):
         # Values themselves should be saved in the portion of RAM that is allocated for the stack
        self.reg[self.sp] -= 1
        data = MDR if MDR else self.reg[self.ram[self.pc+1]] # Memory Data Register - contains the data that was read or the data to write
        self.ram_write(self.reg[self.sp], data)
        self.pc += 2

    def POP(self):
        self.reg[self.ram_read(self.pc+1)] = self.ram_read(self.reg[self.sp])
        self.pc += 2
        self.reg[self.sp] += 1
    
    def ADD(self):
        reg_a = self.ram_read(self.pc + 1)
        reg_b = self.ram_read(self.pc + 2)
        self.alu("ADD", reg_a, reg_b)
        self.pc += 3
    
    def CALL(self):
        self.PUSH(self.pc+2)
        self.pc = self.reg[self.ram_read(self.pc-1)]

    def RET(self):
        self.pc = self.ram_read(self.reg[self.sp])
        self.reg[self.sp] += 1

    # Methods for SC solution
    def CMP(self):
        # Compare values in two registers
        reg_a = self.ram_read(self.pc + 1)
        reg_b = self.ram_read(self.pc + 2)

        # If equal, set equal flag to 1, else - to 0
        if self.reg[reg_a] == self.reg[reg_b]:
            self.FL[self.equal] = 1
        else:
            self.FL[self.equal] = 0
        # If reg_a less than reg_b, set less flag to 1, else - to 0
        if self.reg[reg_a] < self.reg[reg_b]:
            self.FL[self.less] = 1
        else:
            self.FL[self.less] = 0
        # If reg_a greater than reg_b, set greater flag to 1, else - to 0
        if self.reg[reg_a] > self.reg[reg_b]:
            self.FL[self.greater] = 1
        else:
            self.FL[self.greater] = 0
        
        # update counter
        self.pc += 3

    def JMP(self):
        # jump to the address stored in given register
        jump = self.ram_read(self.pc + 1)
        # Set the `PC` to the address stored in the given register.
        self.pc = self.reg[jump]
    def JEQ(self):
        # check if equal flag is true (== 1)
        #  -> jump
        if self.FL[self.equal] == 1:
            self.pc = self.reg[self.ram_read(self.pc + 1)]
        else:
            # update counter
            self.pc += 2

    def JNE(self):
        # check if equal flag is false (==0)
        # -> jump
        if self.FL[self.equal] == 0:
            self.pc = self.reg[self.ram_read(self.pc + 1)]
        else:
            # update counter
            self.pc += 2

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()
    
    def run(self):
        """Run the CPU."""
        self.running = True   
        while self.running:
            IR = self.ram[self.pc]
            self.branchtable[IR]()