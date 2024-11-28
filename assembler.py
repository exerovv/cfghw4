import struct
import yaml
import sys

COMMANDS = {
    "LOAD_CONST": 18,
    "READ_MEM": 2,
    "WRITE_MEM": 10,
    "UNARY_MINUS": 1,
}


def instruction_to_bytes(instruction, size):
    """Преобразование инструкции в массив байтов."""
    raw_bytes = struct.pack("<Q", instruction)[:size]
    return [f"0x{b:02X}" for b in raw_bytes]


def assemble(input_file, output_file, log_file):
    with open(input_file, "r") as f:
        lines = f.readlines()

    binary_data = bytearray()
    log_data = []

    for line in lines:
        parts = line.strip().split()
        command = parts[0]
        A = COMMANDS[command]
        B = int(parts[1])
        minus = "minus" if B < 0 else "plus"
        C = int(parts[2])
        D = int(parts[3]) if len(parts) > 3 else 0

        if (minus == "plus"):

            if command == "LOAD_CONST":
                instruction = (A & 0x1F) | ((B & 0xFFFFFF) << 5) | ((C & 0x7) << 33)
                size = 5
            elif command == "READ_MEM":
                instruction = (A & 0x1F) | ((B & 0x7FFFFF) << 5) | ((C & 0x7) << 24)
                size = 4
            elif command == "WRITE_MEM":
                instruction = (A & 0x1F) | ((B & 0x7) << 5) | ((C & 0x7) << 8) | ((D & 0x7FF) << 11)
                size = 3
            elif command == "UNARY_MINUS":
                instruction = (A & 0x1F) | ((B & 0x7) << 5) | ((C & 0x7) << 8) | ((D & 0x7FF) << 11)
                size = 3
            else:
                raise ValueError(f"Unknown command: {command}")
        else:
            B = abs(B)
            if command == "LOAD_CONST":
                instruction = (A & 0x1F) | (0x80000000 | (B & 0xFFFFFFF) << 5) | ((C & 0x7) << 33)
                print(bin(instruction))
                size = 5
            elif command == "READ_MEM":
                instruction = (A & 0x1F) | ((B & 0x7FFFFF) << 5) | ((C & 0x7) << 24)
                size = 4
            elif command == "WRITE_MEM":
                instruction = (A & 0x1F) | ((B & 0x7) << 5) | ((C & 0x7) << 8) | ((D & 0x7FF) << 11)
                size = 3
            elif command == "UNARY_MINUS":
                instruction = (A & 0x1F) | ((B & 0x7) << 5) | ((C & 0x7) << 8) | ((D & 0x7FF) << 11)
                size = 3
            else:
                raise ValueError(f"Unknown command: {command}")

        binary_data.extend(struct.pack("<Q", instruction)[:size])
        log_data.append({
            "command": command,
            "A": A,
            "B": B,
            "C": C,
            "D": D if len(parts) > 3 else None,
            "bytes": instruction_to_bytes(instruction, size),
        })

    with open(output_file, "wb") as f:
        f.write(binary_data)

    with open(log_file, "w") as f:
        yaml.dump(log_data, f, default_flow_style=False)


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python assembler.py <input_file> <output_file> <log_file>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]
    log_file = sys.argv[3]
    assemble(input_file, output_file, log_file)
