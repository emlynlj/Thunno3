from thunno2 import dictionary
from thunno2.commands import *
from thunno2.lexer import tokenise
import string
import copy
import sys

"""The main interpreter. To run a Thunno 2 program, use the run function."""

vars_dict = {
    'x': 1,   # x defaults to 1
    'y': 2,   # y defaults to 2
    'ga': []  # global array defaults to []
}

'''RUN FUNCTION'''


def run(code, *, n, iteration_index):
    # while ctx.index < len(code):
    for chars, desc, info in code:
        if desc == 'command' or desc == 'digraph':
            if info != Void:
                values = info()
                for value in values:
                    ctx.stack.push(value)
        elif desc in (
            'number', 'string', 'one character', 'two characters', 'three characters', 'list'
        ):
            ctx.stack.push(info)
        elif desc == 'lowercase alphabetic compression':
            base255_number = decompress(info, '“')
            decompressed_string = to_custom_base_string(' ' + string.ascii_lowercase, base255_number)
            ctx.stack.push(decompressed_string)
        elif desc == 'title case alphabetic compression':
            base255_number = decompress(info, '”')
            decompressed_string = to_custom_base_string(' ' + string.ascii_lowercase, base255_number)
            ctx.stack.push(decompressed_string.title())
        elif desc == 'lowercase dictionary compression':
            lst = []
            i = 0
            while i < len(info):
                c = info[i]
                if c in dictionary.dictionary_codepage:
                    try:
                        i += 1
                        lst.append(dictionary.dictionary_decompress_string(c + info[i]))
                    except:
                        pass
                elif c == '\\':
                    try:
                        i += 1
                        lst.append(info[i])
                    except:
                        lst.append('\\')
                else:
                    lst.append(c)
                i += 1
            ctx.stack.push(''.join(lst))
        elif desc == 'title case dictionary compression':
            lst = []
            i = 0
            while i < len(info):
                c = info[i]
                if c in dictionary.dictionary_codepage:
                    try:
                        i += 1
                        lst.append(dictionary.dictionary_decompress_string(c + info[i]).title())
                    except:
                        pass
                elif c == '\\':
                    try:
                        i += 1
                        lst.append(info[i])
                    except:
                        lst.append('\\')
                else:
                    lst.append(c)
                i += 1
            ctx.stack.push(''.join(lst))
        elif desc == 'compressed number' or desc == 'small compressed number':
            base255_number = decompress(info, '»')
            ctx.stack.push(base255_number)
        elif desc == 'compressed list':
            base255_number = decompress(info, '¿')
            decompressed_string = to_custom_base_string('][0123456789-.,', base255_number)
            try:
                e = eval(decompressed_string)
                if isinstance(e, tuple):
                    ctx.stack.push(list(e))
                else:
                    ctx.stack.push(e)
            except:
                ctx.stack.push(decompressed_string)
        elif desc == 'variable get':
            ctx.stack.push(vars_dict.get(info, 0))
        elif desc == 'variable set':
            a = next(ctx.stack.rmv(1))
            vars_dict[info] = a
        elif desc == 'single function map':
            a = next(ctx.stack.rmv(1))
            func = info
            if func != Void:
                x = listify(a)
                r = []
                old_stack = Stack(copy.deepcopy(list(ctx.stack).copy()))
                for i in x:
                    ctx.stack = Stack(copy.deepcopy(list(old_stack).copy()))
                    ctx.stack.push(i)
                    for j in func():
                        r.append(j)
                ctx.stack.push(r)
        elif desc == 'outer product':
            a, b = ctx.stack.rmv(2)
            func = info
            if func != Void:
                x = listify(a)
                r = []
                old_stack = Stack(copy.deepcopy(list(ctx.stack).copy()))
                if isinstance(a, list):
                    if isinstance(b, list):
                        for j in b:
                            r.append([])
                            for i in a:
                                ctx.stack = Stack([i, j] + copy.deepcopy(list(old_stack).copy()))
                                for k in func():
                                    r[-1].append(k)
                    else:
                        for i in a:
                            ctx.stack = Stack([i, b] + copy.deepcopy(list(old_stack).copy()))
                            for k in func():
                                r.append(k)
                else:
                    if isinstance(b, list):
                        for i in b:
                            ctx.stack = Stack([a, i] + copy.deepcopy(list(old_stack).copy()))
                            for k in func():
                                r.append(k)
                    else:
                        ctx.stack.push(b)
                        ctx.stack.push(a)
                        k = func()
                        if k:
                            r = k[-1]
                ctx.stack.push(r)
        elif desc == 'single function filter':
            a = next(ctx.stack.rmv(1))
            func = info
            if func != Void:
                x = listify(a)
                r = []
                old_stack = Stack(copy.deepcopy(list(ctx.stack).copy()))
                for i in x:
                    ctx.stack = Stack(copy.deepcopy(list(old_stack).copy()))
                    ctx.stack.push(i)
                    f = func()
                    if not f:
                        continue
                    if f[-1]:
                        r.append(i)
                ctx.stack.push(r)
        elif desc == 'single function sort by':
            a = next(ctx.stack.rmv(1))
            func = info
            if func != Void:
                x = listify(a)
                sort_by = []
                old_stack = Stack(copy.deepcopy(list(ctx.stack).copy()))
                for i in x:
                    ctx.stack = Stack(copy.deepcopy(list(old_stack).copy()))
                    ctx.stack.push(i)
                    f = func()
                    if not f:
                        sort_by.append((i, i))
                    else:
                        sort_by.append((i, f[-1]))
                try:
                    sorted_list = sorted(sort_by, key=lambda t: t[-1])
                    ctx.stack.push([p for p, q in sorted_list])
                except:
                    ctx.stack.push(x)
        elif desc == 'single function group by':
            a = next(ctx.stack.rmv(1))
            func = info
            if func != Void:
                x = listify(a)
                group_by = []
                old_stack = Stack(copy.deepcopy(list(ctx.stack).copy()))
                for i in x:
                    ctx.stack = Stack(copy.deepcopy(list(old_stack).copy()))
                    ctx.stack.push(i)
                    f = func()
                    if not f:
                        group_by.append((i, i))
                    else:
                        group_by.append((i, f[-1]))
                try:
                    d = []
                    for val, key in group_by:
                        for k, (i, j) in enumerate(d):
                            if key == i:
                                d[k][1].append(val)
                                break
                        else:
                            d.append((key, [val]))
                    ctx.stack.push([q for p, q in d])
                except:
                    ctx.stack.push(x)
        elif desc == 'context variable':
            ctx.stack.push(n)
        elif desc == 'iteration index':
            ctx.stack.push(iteration_index)
        elif desc == 'get x':
            ctx.stack.push(vars_dict.get('x', 1))
        elif desc == 'get y':
            ctx.stack.push(vars_dict.get('y', 2))
        elif desc == 'set x':
            a = next(ctx.stack.rmv(1))
            vars_dict['x'] = a
        elif desc == 'set y':
            a = next(ctx.stack.rmv(1))
            vars_dict['y'] = a
        elif desc == 'set x without popping':
            a = (ctx.stack.copy() + ctx.other_il + [0])[0]
            vars_dict['x'] = a
        elif desc == 'set y without popping':
            a = (ctx.stack.copy() + ctx.other_il + [0])[0]
            vars_dict['y'] = a
        elif desc == 'increment x':
            try:
                vars_dict['x'] = vars_dict.get('x', 1) + 1
            except:
                pass
        elif desc == 'increment y':
            try:
                vars_dict['y'] = vars_dict.get('y', 2) + 1
            except:
                pass
        elif desc == 'get global array':
            ctx.stack.push(vars_dict.get('ga', []))
        elif desc == 'add to global array':
            a = next(ctx.stack.rmv(1))
            ga = vars_dict.get('ga', [])
            if not isinstance(ga, list):
                vars_dict['ga'] = [ga, a]
            vars_dict['ga'] = ga + [a]
        elif desc == 'stack':
            ctx.stack.push(list(ctx.stack).copy())
        elif desc == 'constant':
            ctx.stack.push(info)
        elif desc == 'codepage compression':
            ctx.stack.push(info)
        elif desc == 'quit':
            raise TerminateProgramException()  # This will hopefully get caught and ignored
        elif desc == 'next input':
            if ctx.other_il:
                ctx.stack.push(ctx.other_il[0])
                ctx.other_il = ctx.other_il[1:] + [ctx.other_il[0]]
        elif desc == 'input list':
            ctx.stack.push(ctx.og_input_list)
        elif desc == 'first input':
            try:
                ctx.stack.push(ctx.og_input_list[0])
            except:
                ctx.stack.push(ctx.og_input_list)
        elif desc == 'second input':
            try:
                ctx.stack.push(ctx.og_input_list[1])
            except:
                ctx.stack.push(ctx.og_input_list)
        elif desc == 'third input':
            try:
                ctx.stack.push(ctx.og_input_list[2])
            except:
                ctx.stack.push(ctx.og_input_list)
        elif desc == 'third last input':
            try:
                ctx.stack.push(ctx.og_input_list[-3])
            except:
                ctx.stack.push(ctx.og_input_list)
        elif desc == 'second last input':
            try:
                ctx.stack.push(ctx.og_input_list[-2])
            except:
                ctx.stack.push(ctx.og_input_list)
        elif desc == 'last input':
            try:
                ctx.stack.push(ctx.og_input_list[-1])
            except:
                ctx.stack.push(ctx.og_input_list)
        elif desc == 'print':
            print(next(ctx.stack.rmv(1)))
            ctx.implicit_print = False
        elif desc == 'print without newline':
            print(next(ctx.stack.rmv(1)), end='')
            ctx.implicit_print = False
        elif desc == 'print without popping':
            print((ctx.stack.copy() + ctx.other_il + [0])[0])
        elif desc == 'map':
            a = next(ctx.stack.rmv(1))
            x = listify(a)
            r = []
            old_stack = Stack(copy.deepcopy(list(ctx.stack).copy()))
            for i, j in enumerate(x):
                ctx.stack = Stack([j] + copy.deepcopy(old_stack))
                run(info, n=j, iteration_index=i)
                r.append(next(ctx.stack.rmv(1)))
            ctx.stack.push(r)
        elif desc == 'filter':
            a = next(ctx.stack.rmv(1))
            x = listify(a)
            r = []
            old_stack = Stack(copy.deepcopy(list(ctx.stack).copy()))
            for i, j in enumerate(x):
                ctx.stack = Stack([j] + copy.deepcopy(old_stack))
                run(info, n=j, iteration_index=i)
                z = next(ctx.stack.rmv(1))
                if z:
                    r.append(j)
            ctx.stack.push(r)
        elif desc == 'sort by':
            a = next(ctx.stack.rmv(1))
            x = listify(a)
            r = []
            old_stack = Stack(copy.deepcopy(list(ctx.stack).copy()))
            for i, j in enumerate(x):
                ctx.stack = Stack([j] + copy.deepcopy(old_stack))
                run(info, n=j, iteration_index=i)
                z = next(ctx.stack.rmv(1))
                r.append((j, z))
            try:
                sorted_list = sorted(r, key=lambda t: t[-1])
                ctx.stack.push([p for p, q in sorted_list])
            except:
                ctx.stack.push(x)
        elif desc == 'group by':
            a = next(ctx.stack.rmv(1))
            x = listify(a)
            r = []
            old_stack = Stack(copy.deepcopy(list(ctx.stack).copy()))
            for i, j in enumerate(x):
                ctx.stack = Stack([j] + copy.deepcopy(old_stack))
                run(info, n=j, iteration_index=i)
                z = next(ctx.stack.rmv(1))
                r.append((j, z))
            try:
                d = []
                for val, key in r:
                    for k, (i, j) in enumerate(d):
                        if key == i:
                            d[k][1].append(val)
                            break
                    else:
                        d.append((key, [val]))
                ctx.stack.push([q for p, q in d])
            except:
                ctx.stack.push(x)
        elif desc == 'fixed point':
            r = [Void]
            old_stack = Stack(copy.deepcopy(list(ctx.stack).copy()))
            i = 0
            while True:
                ctx.stack = Stack(copy.deepcopy(old_stack))
                run(info, n=r[-1], iteration_index=i)
                k = (ctx.stack + ctx.other_il + [0])[0]
                print(k)
                r.append(k)
                if r[-1] == r[-2]:
                    break
                i += 1
            ctx.stack.push(r[1:])
        elif desc == 'first n integers':
            a = next(ctx.stack.rmv(1))
            try:
                x = int(a)
            except:
                x = 1
            old_stack = Stack(copy.deepcopy(list(ctx.stack).copy()))
            i = 1
            r = []
            while len(r) < x:
                ctx.stack = Stack(copy.deepcopy(old_stack))
                ctx.stack.push(i)
                run(info, n=i, iteration_index=i-1)
                k = next(ctx.stack.rmv(1))
                if k:
                    r.append(i)
                i += 1
            ctx.stack.push(r)
        elif desc == 'cumulative reduce by':
            a = next(ctx.stack.rmv(1))
            x = listify(a)
            old_stack = Stack(copy.deepcopy(list(ctx.stack).copy()))
            if x:
                r = [x.pop(0)]
                for i, j in enumerate(x):
                    ctx.stack = Stack(copy.deepcopy(old_stack))
                    ctx.stack.push(r[-1])
                    ctx.stack.push(j)
                    run(info, n=j, iteration_index=i)
                    r.append(next(ctx.stack.rmv(1)))
                ctx.stack.push(r)
            else:
                ctx.stack.push([])
        elif desc == 'for loop':
            a = next(ctx.stack.rmv(1))
            x = listify(a)
            for i, j in enumerate(x):
                if not isinstance(a, (int, float)):
                    ctx.stack.push(j)
                run(info, n=j, iteration_index=i)
        elif desc == 'while loop':
            cond, body = info
            i = 0
            while True:
                old_stack = Stack(copy.deepcopy(list(ctx.stack).copy()))
                run(cond, n=0, iteration_index=i)
                z = next(ctx.stack.rmv(1))
                ctx.stack = Stack(copy.deepcopy(old_stack))
                if not z:
                    break
                run(body, n=0, iteration_index=i)
                i += 1
        elif desc == 'if statement':
            if_true, if_false = info
            a = next(ctx.stack.rmv(1))
            if a:
                run(if_true, n=0, iteration_index=1)
            else:
                run(if_false, n=0, iteration_index=0)
        elif desc == 'execute without popping':
            if info != Void:
                values = info(pop=False)
                for value in values:
                    ctx.stack.push(value)
        elif desc == 'pair apply':
            a = next(ctx.stack.rmv(1))
            old_stack = Stack(copy.deepcopy(list(ctx.stack).copy()))
            r = []
            f1, f2 = info
            ctx.stack.push(a)
            k = f1()
            if k:
                r.append(k[-1])
            ctx.stack = Stack(copy.deepcopy(old_stack))
            ctx.stack.push(a)
            k = f2()
            if k:
                r.append(k[-1])
            ctx.stack.push(r)
        elif desc == 'two function map':
            a = next(ctx.stack.rmv(1))
            old_stack = Stack(copy.deepcopy(list(ctx.stack).copy()))
            r = []
            f1, f2 = info
            x = listify(a)
            for i in x:
                ctx.stack = Stack(copy.deepcopy(list(old_stack).copy()))
                ctx.stack.push(i)
                for j in f1():
                    ctx.stack.push(j)
                for k in f2():
                    ctx.stack.push(k)
                r.append(next(ctx.stack.rmv(1)))
            ctx.stack.push(r)
        else:
            if ctx.warnings:
                print('TRACEBACK: [UNRECOGNISED TOKEN]', file=sys.stderr)
                print(f'Got {chars!r} (tokenised to {desc!r})')
    return 0


def test(cod, inp=(), stk=(), warn=True):
    ctx.stack = Stack(stk)
    ctx.og_input_list = list(inp)
    ctx.other_il = list(inp)
    ctx.warnings = warn
    tokenised = tokenise(cod)[1]
    run(tokenised, n=0, iteration_index=0)
    print(ctx.stack)
    if ctx.implicit_print:
        print(ctx.stack[0])