import struct
import yaml
import sys


def extract_signed_field(value, shift, size):
    mask = (1 << size) - 1
    field = (value >> shift) & mask
    return field

def extract_minus_field(value, shift, size):
    mask = (1 << size) - 1
    field = (value >> shift) & mask
    if str(bin((field & (1 << (size - 2)))))[2] == "1":
        field = -(field & (~(1 << size - 2)))

    return field


def interpret(binary_file, result_file, memory_range):
    with open("output.bin", "rb") as f:
        data = f.read()

    memory = [0] * 1024
    program_counter = 0
    log_data = []

    while program_counter < len(data):
        size = 5 if data[program_counter] & 0x1F == 18 else 4 if data[program_counter] & 0x1F == 2 else 3
        instruction = int.from_bytes(data[program_counter:program_counter + size], "little")
        program_counter += size

        A = instruction & 0x1F
        if (A == 18):
            B = extract_minus_field(instruction, 5, 28 if A == 18 else 19 if A == 2 else 3)
        else:
            B = extract_signed_field(instruction, 5, 28 if A == 18 else 19 if A == 2 else 3)
        C = extract_signed_field(instruction, 33 if A == 18 else 24 if A == 2 else 8, 3)
        D = (instruction >> 11) & 0x7FF if A in {10, 1} else None

        if A == 18:
            memory[C] = B
        elif A == 2:
            memory[C] = memory[memory[B]]
        elif A == 10:
            memory[memory[C] + D] = memory[B]
        elif A == 1:
            memory[B] = -memory[memory[C] + D]

        log_data.append({
            "A": A,
            "B": B,
            "C": C,
            "D": D,
            "memory_snapshot": memory[:11],
        })

    result = {"memory": memory[memory_range[0]:memory_range[1]], "log": log_data}
    with open(result_file, "w") as f:
        yaml.dump(result, f, default_flow_style=False)


if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Usage: python interpreter.py <binary_file> <result_file> <range_start> <range_end>")
        sys.exit(1)

    binary_file = sys.argv[1]
    result_file = sys.argv[2]
    range_start = int(sys.argv[3])
    range_end = int(sys.argv[4])
    interpret(binary_file, result_file, (range_start, range_end))
