from thunno2 import interpreter, commands, helpers


def process_input_flags(flags, inputs):

    if 'W' in flags:
        inputs = [inputs]
    else:
        inputs = inputs.splitlines()

    if 'E' not in flags:
        new_input = []
        for inp in inputs:
            try:
                new_input.append(eval(inp))
            except:
                new_input.append(inp)
        inputs = new_input[:]

    for flag in flags:
        if flag == 'Z':
            commands.ctx.stack.push(0)
        elif flag == 'T':
            commands.ctx.stack.push(10)
        elif flag == 'H':
            commands.ctx.stack.push(100)

    if 'B' in flags:
        new_input = []
        for inp in inputs:
            if isinstance(inp, str):
                new_input.append([ord(c) for c in inp])
            else:
                new_input.append(inp)
        inputs = new_input[:]

    if '+' in flags:
        new_input = []
        for inp in inputs:
            if isinstance(inp, (int, float)):
                new_input.append(inp + flags.count('+'))
            else:
                new_input.append(inp)
        inputs = new_input[:]

    if '-' in flags:
        new_input = []
        for inp in inputs:
            if isinstance(inp, (int, float)):
                new_input.append(inp - flags.count('-'))
            else:
                new_input.append(inp)
        inputs = new_input[:]

    return inputs


def process_output_flags(flags):

    for flag in flags:

        if 'J' == flag:
            commands.ctx.stack.push(helpers.empty_join(next(commands.ctx.stack.rmv(1))))

        if 'j' == flag:
            commands.ctx.stack.push(helpers.empty_join(list(commands.ctx.stack)))

        if 'N' == flag:
            commands.ctx.stack.push(helpers.newline_join(next(commands.ctx.stack.rmv(1))))

        if 'n' == flag:
            commands.ctx.stack.push(helpers.newline_join(list(commands.ctx.stack)))

        if 'Ṡ' == flag:
            commands.ctx.stack.push(helpers.space_join(next(commands.ctx.stack.rmv(1))))

        if 'ṡ' == flag:
            commands.ctx.stack.push(helpers.space_join(list(commands.ctx.stack)))

        if 'S' == flag:
            commands.ctx.stack.push(commands.commands['S']()[0])

        if 's' == flag:
            commands.ctx.stack.push(helpers.it_sum(commands.ctx.stack))

        if 'L' == flag:
            commands.ctx.stack.push(commands.commands['l']()[0])

        if 'l' == flag:
            commands.ctx.stack.push(len(commands.ctx.stack))

    if (commands.ctx.implicit_print or ('O' in flags)) and not ('o' in flags):
        print(next(commands.ctx.stack.rmv(1)))


def run(flags, code, inputs):
    inputs = process_input_flags(flags, inputs)
    commands.ctx.og_input_list = inputs.copy()
    commands.ctx.other_il = inputs.copy()
    interpreter.run(code, n=0, iteration_index=0)
    process_output_flags(flags)