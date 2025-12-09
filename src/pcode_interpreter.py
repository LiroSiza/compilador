class PCodeInterpreter:
    def __init__(self, pcode_instructions, symbol_table):
        self.instructions = pcode_instructions
        self.symbol_table = symbol_table
        self.stack = []
        self.memory = {}  # Address -> value
        self.pc = 0  # Program counter
        self.input_buffer = []
        self.output_buffer = []
        self.labels = {}  # Label -> instruction index
        self.waiting_for_input = False
        self.finished = False

        # Build label map - scan all instructions for labels
        for i, (instr, _) in enumerate(self.instructions):
            parts = instr.split()
            if len(parts) >= 2 and parts[0] == 'lab':
                label = parts[1]
                self.labels[label] = i

    def reset(self):
        """Reset the interpreter state"""
        self.stack = []
        self.memory = {}
        self.pc = 0
        self.output_buffer = []
        self.waiting_for_input = False
        self.finished = False

    def step(self):
        """Execute one instruction. Returns True if waiting for input, False if finished."""
        if self.finished or self.pc >= len(self.instructions):
            self.finished = True
            return False
            
        if self.waiting_for_input:
            return True
            
        instr, _ = self.instructions[self.pc]
        
        if instr.split()[0] == 'cin':
            self.waiting_for_input = True
            return True
            
        self.execute_instruction(instr)
        self.pc += 1
        return False

    def provide_input(self, value):
        """Provide input value when waiting for cin"""
        if not self.waiting_for_input:
            return False
            
        # Convert input value
        try:
            value = int(value)
        except ValueError:
            try:
                value = float(value)
            except ValueError:
                pass  # Keep as string
                
        self.stack.append(value)
        self.waiting_for_input = False
        self.pc += 1  # Move past the cin instruction
        return True

    def get_pending_output(self):
        """Get any output that has been generated since last call"""
        output = ''.join(self.output_buffer)
        self.output_buffer = []
        return output

    def is_finished(self):
        """Check if execution is complete"""
        return self.finished

    def execute(self):
        """Execute the P-code instructions"""
        self.stack = []
        self.memory = {}
        self.pc = 0
        self.output_buffer = []

        while self.pc < len(self.instructions):
            instr, _ = self.instructions[self.pc]
            self.execute_instruction(instr)
            self.pc += 1

        return self.get_output()

    def execute_instruction(self, instr):
        """Execute a single P-code instruction"""
        parts = instr.split()
        opcode = parts[0]

        if opcode == 'lab':  # Label - do nothing
            pass
        elif opcode == 'ldc':  # Load constant
            value = float(parts[1]) if '.' in parts[1] else int(parts[1])
            self.stack.append(value)
        elif opcode == 'lds':  # Load string constant
            # Join all parts after 'lds' to reconstruct the string
            string_value = ' '.join(parts[1:]).strip('"')
            self.stack.append(string_value)
        elif opcode == 'lod':  # Load from memory
            addr = int(parts[1])
            if addr in self.memory:
                self.stack.append(self.memory[addr])
            else:
                self.stack.append(0)  # Default value
        elif opcode == 'sto':  # Store to memory
            addr = int(parts[1])
            if self.stack:
                value = self.stack.pop()
                self.memory[addr] = value
        elif opcode == 'add':
            b = self.stack.pop()
            a = self.stack.pop()
            self.stack.append(a + b)
        elif opcode == 'sub':
            b = self.stack.pop()
            a = self.stack.pop()
            self.stack.append(a - b)
        elif opcode == 'mul':
            b = self.stack.pop()
            a = self.stack.pop()
            self.stack.append(a * b)
        elif opcode == 'div':
            b = self.stack.pop()
            a = self.stack.pop()
            if b != 0:
                self.stack.append(a / b)
            else:
                raise ValueError("Division by zero")
        elif opcode == 'pow':
            b = self.stack.pop()
            a = self.stack.pop()
            self.stack.append(a ** b)
        elif opcode == 'mod':
            b = self.stack.pop()
            a = self.stack.pop()
            self.stack.append(a % b)
        elif opcode == 'equ':
            b = self.stack.pop()
            a = self.stack.pop()
            self.stack.append(1 if a == b else 0)
        elif opcode == 'neq':
            b = self.stack.pop()
            a = self.stack.pop()
            self.stack.append(1 if a != b else 0)
        elif opcode == 'les':
            b = self.stack.pop()
            a = self.stack.pop()
            self.stack.append(1 if a < b else 0)
        elif opcode == 'leq':
            b = self.stack.pop()
            a = self.stack.pop()
            self.stack.append(1 if a <= b else 0)
        elif opcode == 'grt':
            b = self.stack.pop()
            a = self.stack.pop()
            self.stack.append(1 if a > b else 0)
        elif opcode == 'geq':
            b = self.stack.pop()
            a = self.stack.pop()
            self.stack.append(1 if a >= b else 0)
        elif opcode == 'and':
            b = self.stack.pop()
            a = self.stack.pop()
            self.stack.append(1 if a and b else 0)
        elif opcode == 'or':
            b = self.stack.pop()
            a = self.stack.pop()
            self.stack.append(1 if a or b else 0)
        elif opcode == 'not':
            a = self.stack.pop()
            self.stack.append(1 if not a else 0)
        elif opcode == 'neg':
            a = self.stack.pop()
            self.stack.append(-a)
        elif opcode == 'ujp':  # Unconditional jump
            label = parts[1]
            if label in self.labels:
                self.pc = self.labels[label] - 1  # -1 because pc will be incremented
        elif opcode == 'fjp':  # False jump
            label = parts[1]
            condition = self.stack.pop()
            if not condition:
                if label in self.labels:
                    self.pc = self.labels[label] - 1
        elif opcode == 'cin':
            if self.input_buffer:
                value = self.input_buffer.pop(0)
                # Try to convert to int or float
                try:
                    value = int(value)
                except ValueError:
                    try:
                        value = float(value)
                    except ValueError:
                        pass  # Keep as string
                self.stack.append(value)
            else:
                raise ValueError("No input available")
        elif opcode == 'cout':
            if self.stack:
                value = self.stack.pop()
                self.output_buffer.append(str(value) + '\n')
        # Add more opcodes as needed