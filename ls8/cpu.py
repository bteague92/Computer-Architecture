"""CPU functionality."""

import sys

HLT = 0b00000001
LDI = 0b10000010
PRN = 0b01000111
MUL = 0b10100010
POP = 0b01000110
PUSH = 0b01000101
CALL = 0b01010000
RET = 0b00010001
ADD = 0b10100000

CMP = 0b10100111
JMP = 0b01010100
JEQ = 0b01010101
JNE = 0b01010110

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256
        self.reg = [0] * 8
        self.pc = 0
        self.running = True
        self.branchtable = {}
        self.stack_pointer = 0xf4
        self.reg[7] = self.stack_pointer

        # Flags
        self.E = None
        self.L = None
        self.G = None

        # Instructions
        self.branchtable[HLT] = self.handleHLT
        self.branchtable[LDI] = self.handleLDI
        self.branchtable[PRN] = self.handlePRN
        self.branchtable[MUL] = self.handleMUL
        self.branchtable[PUSH] = self.handlePUSH
        self.branchtable[POP] = self.handlePOP
        self.branchtable[ADD] = self.handleADD
        self.branchtable[RET] = self.handleRET
        self.branchtable[CALL] = self.handleCALL

        # Sprint Challenge
        self.branchtable[CMP] = self.handleCMP
        self.branchtable[JMP] = self.handleJMP
        self.branchtable[JEQ] = self.handleJEQ
        self.branchtable[JNE] = self.handleJNE



    def ram_read(self, i):
        return self.ram[i]

    def ram_write(self, i, MDR):
        self.ram[i] = MDR

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        # elif op == "SUB": etc
        else:
            raise Exception("Unsupported ALU operation")

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

    def handleHLT(self, a=None, b=None):
        # print("HLT")
        # exit
        self.running = False

    def handleLDI(self, a, b):
        # print("LDI")
        # set specified register to specified value
        self.reg[a] = b
        self.pc += 3

    def handlePRN(self, a, b=None):
        # print("PRN")
        # print value from specified register
        print(self.reg[a])
        self.pc += 2

    def handleMUL(self, a, b):
        # print("MUL")
        self.reg[a] = self.reg[a] * self.reg[b]
        self.pc += 3

    def handlePUSH(self, a, b=None):
        # print("PUSH")
        # decrement stack pointer
        self.stack_pointer -= 1
        self.stack_pointer &= 0xff  # keep in range of 00-FF

        # get register number and value stored at specified reg number
        reg_num = self.ram[self.pc + 1]
        val = self.reg[reg_num]

        # store value in ram
        self.ram[self.stack_pointer] = val
        self.pc += 2

    def handlePOP(self, a, b=None):
        # print("POP")
        # get value from ram
        address = self.stack_pointer
        val = self.ram[address]

        # store at given register
        reg_num = self.ram[self.pc + 1]
        self.reg[reg_num] = val

        # increment stack pointer and program counter
        self.stack_pointer += 1
        self.stack_pointer &= 0xff  # keep in range of 00-FF

        self.pc += 2

    def handleADD(self, a, b):
        # print("ADD")
        result = self.reg[a] + self.reg[b]
        self.reg[a] = result
        self.pc += 3

    def handleRET(self, a, b):
        # print("RET")
        # pop from stack
        val = self.ram[self.stack_pointer]
        # set pc back to previous
        self.pc = val
        # increment stack pointer
        self.stack_pointer += 1

    def handleCALL(self, a, b):
        # print("CALL")
        # return counter, save to stack
        rc = self.pc + 2
        self.stack_pointer -= 1
        self.ram[self.stack_pointer] = rc

        self.pc = self.reg[a]


    # Sprint Challenge
    

    def handleJMP(self, a, b):
        # print("JMP")
        self.pc = self.reg[a]

    def handleJEQ(self, a, b):
        # print("JEQ")
        if self.E == 1:
            self.handleJMP(a, b)
        else:
            self.pc += 2

    def handleJNE(self, a, b):
        # print("JNE")
        if self.E == 0:
            self.handleJMP(a, b)
        else:
            self.pc += 2

    def handleCMP(self, a, b):
        # print("CMP")

        if self.reg[a] == self.reg[b]:
            self.E = 1
        else:
            self.E = 0

        if self.reg[a] < self.reg[b]:
            self.L = 1
        else:
            self.L = 0

        if self.reg[a] > self.reg[b]:
            self.G = 1
        else:
            self.G = 0

        self.pc += 3


    def load(self):
        """Load a program into memory."""

        address = 0
        file = sys.argv[1]

        if len(sys.argv) != 2:
            print("usage: comp.py filename")
            sys.exit(1)

        try:
            with open(sys.argv[1]) as f:
                for line in f:
                    try:
                        line = line.split("#", 1)[0]
                        line = int(line, 2)
                        self.ram[address] = line
                        address += 1
                    except ValueError:
                        pass

        except FileNotFoundError:
            print(f"Couldn't find file {sys.argv[1]}")
            sys.exit(1)

        # For now, we've just hardcoded a program:

        # program = [
        #     # From print8.ls8
        #     0b10000010, # LDI R0,8
        #     0b00000000,
        #     0b00001000,
        #     0b01000111, # PRN R0
        #     0b00000000,
        #     0b00000001, # HLT
        # ]
        #
        # for instruction in program:
        #     self.ram[address] = instruction
        #     address += 1
        # print(self.ram)

    def run(self):
        """Run the CPU."""
        while self.running:
            IR = self.ram_read(self.pc)
            
            a = self.ram_read(self.pc + 1)
            b = self.ram_read(self.pc + 2)

            if IR not in self.branchtable:
                print(f'Unknown: {IR} at {self.pc}')
                self.running = False
            else:
                f = self.branchtable[IR]
                f(a, b)