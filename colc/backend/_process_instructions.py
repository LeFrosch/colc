from ._instruction import InstructionBuffer


def process_instructions(buffer: InstructionBuffer) -> bytes:
    builder = bytearray()

    for i, instr in enumerate(buffer.instructions):
        builder.append(instr.opcode)

        if not instr.opcode.is_jmp:
            builder.append(instr.argument_value)
        else:
            label = instr.argument_label
            index = buffer.labels.get(label)
            assert index is not None

            builder.append(abs(i - index))

    return builder
