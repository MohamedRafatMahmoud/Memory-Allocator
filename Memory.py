import tkinter as tk
from tkinter import scrolledtext

# ------------------------------
# Memory Management Logic
# ------------------------------

class MemoryBlock:
    def __init__(self, start, size, process=None):
        self.start = start
        self.size = size
        self.process = process

    def end(self):
        return self.start + self.size - 1

    def is_free(self):
        return self.process is None

    def __repr__(self):
        status = "Free" if self.is_free() else f"Process {self.process}"
        return f"[{self.start} - {self.end()}] : {status}"

class MemoryManager:
    def __init__(self, size):
        self.size = size
        self.memory = [MemoryBlock(0, size)]

    def stat(self):
        return [str(block) for block in self.memory]

    def rq(self, process, size, strategy):
        candidates = [b for b in self.memory if b.is_free() and b.size >= size]
        if not candidates:
            return f"Cannot allocate {size} bytes for process {process} (Not enough space)"

        block = None
        if strategy == 'F':
            block = candidates[0]
        elif strategy == 'B':
            block = min(candidates, key=lambda b: b.size)
        elif strategy == 'W':
            block = max(candidates, key=lambda b: b.size)
        else:
            return "Invalid strategy (use F, B, or W)"

        idx = self.memory.index(block)
        new_block = MemoryBlock(block.start, size, process)
        remaining_size = block.size - size

        if remaining_size > 0:
            self.memory[idx] = new_block
            self.memory.insert(idx + 1, MemoryBlock(block.start + size, remaining_size))
        else:
            self.memory[idx] = new_block

        return f"Allocated {size} bytes to process {process} using {strategy} strategy"

    def rl(self, process):
        found = False
        for block in self.memory:
            if block.process == process:
                block.process = None
                found = True
        if found:
            self.merge_free_blocks()
            return f"Released memory allocated to process {process}"
        else:
            return f"No process named {process} found"

    def merge_free_blocks(self):
        i = 0
        while i < len(self.memory) - 1:
            if self.memory[i].is_free() and self.memory[i + 1].is_free():
                self.memory[i].size += self.memory[i + 1].size
                del self.memory[i + 1]
            else:
                i += 1

    def compact(self):
        new_memory = []
        current_start = 0
        for block in self.memory:
            if not block.is_free():
                new_memory.append(MemoryBlock(current_start, block.size, block.process))
                current_start += block.size

        free_size = self.size - current_start
        if free_size > 0:
            new_memory.append(MemoryBlock(current_start, free_size))

        self.memory = new_memory
        return "Memory compacted."


# ------------------------------
# GUI Interface using Tkinter
# ------------------------------

class AllocatorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Contiguous Memory Allocator")
        self.manager = MemoryManager(100000)

        self.cmd_label = tk.Label(root, text="Enter Command:")
        self.cmd_label.pack()

        self.cmd_entry = tk.Entry(root, width=50)
        self.cmd_entry.pack()
        self.cmd_entry.bind("<Return>", self.handle_command)

        btn_frame = tk.Frame(root)
        btn_frame.pack()

        tk.Button(btn_frame, text="STAT", command=lambda: self.run_cmd("STAT")).pack(side=tk.LEFT)
        tk.Button(btn_frame, text="C", command=lambda: self.run_cmd("C")).pack(side=tk.LEFT)
        tk.Button(btn_frame, text="Exit", command=root.quit).pack(side=tk.LEFT)

        self.output = scrolledtext.ScrolledText(root, width=60, height=20)
        self.output.pack()

        self.print_output("Memory Allocator Initialized with 100000")

    def handle_command(self, event=None):
        cmd = self.cmd_entry.get().strip()
        self.cmd_entry.delete(0, tk.END)
        self.run_cmd(cmd)

    def print_output(self, text):
        self.output.insert(tk.END, text + "\n")
        self.output.see(tk.END)

    def run_cmd(self, cmd):
        if not cmd:
            return

        self.print_output(f"> {cmd}")

        try:
            if cmd.upper() == "STAT":
                self.print_output("Memory Status:")
                for block in self.manager.stat():
                    self.print_output(block)
            elif cmd.upper() == "C":
                result = self.manager.compact()
                self.print_output(result)
            elif cmd.upper().startswith("RQ"):
                _, process, size, strat = cmd.split()
                result = self.manager.rq(process, int(size), strat.upper())
                self.print_output(result)
            elif cmd.upper().startswith("RL"):
                _, process = cmd.split()
                result = self.manager.rl(process)
                self.print_output(result)
            elif cmd.upper() == "X":
                self.root.quit()
            else:
                self.print_output("Unknown command.")
        except Exception as e:
            self.print_output(f"Error: {str(e)}")


# ------------------------------
# Run App
# ------------------------------

if __name__ == "__main__":
    root = tk.Tk()
    app = AllocatorGUI(root)
    root.mainloop()
