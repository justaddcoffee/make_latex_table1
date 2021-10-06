#!/usr/bin/env python

from collections import OrderedDict
from tabulate import tabulate
import argparse
import os

def parse_input_file(input_file: str,
                     split_column_number: int = 63,
                     skip_lines: list = [0, 132]) -> (OrderedDict, list):
    """Parse input file

    :param input_file: file to parse
    :param split_column_number: column number where the second column starts
    :param skip_lines: list of 0-based lines to skip
    :return:
    """
    with open(input_file, 'r') as f:
        line_count = 0
        parsed_data = OrderedDict()  # order not preserved :(
        ordered_keys = []
        for line in f:
            if line.strip() == "" or line_count in skip_lines:
                line_count = line_count + 1
                continue

            col1, col2 = (line[:split_column_number].strip(),
                          line[split_column_number:-1].strip())

            if not col1:
                if last_col1:
                    col1 = last_col1
                else:
                    raise RuntimeError("can't find previous col1 to use!")

            if col2:
                parsed_data.setdefault(col1, []).append(col2)

            if col1 not in ordered_keys:
                ordered_keys.append(col1)
            last_col1 = col1
            line_count = line_count + 1

    return(parsed_data, ordered_keys)


def split_into_labels_and_vals(these_values: list):
    half = len(these_values)//2
    return these_values[:half], these_values[half:]


def make_latex_table(parsed_data: OrderedDict, ordered_keys: list, tablefmt) -> str:
    """Make LaTeX table from parsed data
    :param parsed_data: parsed data from parse_input_file
    :param ordered_keys: list of keys in order that they should appear in table
    :return: str with LaTeX table
    """
    table = []
    for this_key in ordered_keys:
        this_chunk = parsed_data[this_key]
        if not this_chunk:
            print(f"empty chunk for {this_key}!")
        elif len(this_chunk) == 1:
            table.append([this_key, this_chunk[0]])
        else:
            if len(this_chunk) % 2:
                raise RuntimeError(f"Got an odd number of values for key {this_key}")
            table.append([this_key, ""])  # header for this chunk of data
            labels, values = split_into_labels_and_vals(this_chunk)
            new_rows = [["\t"+labels[i], values[i]] for i in range(len(labels))]
            table.extend(new_rows)

    return(tabulate(table, tablefmt=tablefmt))


if __name__ == '__main__':
    print('')
    table_one_file = 'table one.txt'

    parser = argparse.ArgumentParser(description='make latex table')
    parser.add_argument('-i', '--input', type=str, help='input file', required=True)
    parser.add_argument('-o', '--output', type=str, help='output file', required=True)
    parser.add_argument('-f', '--format', type=str, default="latex_longtable",
                        help='output format (latex_longtable)')
    parser.add_argument('--prepend', type=str, help='tex file to prepend')
    parser.add_argument('--append', type=str, help='tex file to append')

    parser.add_argument('--split_column_number', type=str, default=63,
                        help='column number where the second column starts')
    parser.add_argument('--skip_lines', type=str, default=[0, 132],
                        help='list of 0-based lines to skip')
    args = vars(parser.parse_args())

    for this_arg in ['input', 'prepend', 'append']:
        if args[this_arg] and not os.path.exists(args[this_arg]):
            args[this_arg] = os.path.join(os.getcwd(), args[this_arg])

    parsed_data, ordered_keys = parse_input_file(args['input'],
                                                 split_column_number=args['split_column_number'],
                                                 skip_lines=args['skip_lines'])

    latex_table = make_latex_table(parsed_data, ordered_keys,
                                   tablefmt=args['format'])
    with open(args['output'], 'wt') as out:
        if args['prepend']:
            prepend = open(args['prepend'], 'rt')
            prepend_stuff = "".join(prepend.readlines())
            out.write(prepend_stuff)

        out.write(latex_table)

        if args['append']:
            append = open(args['append'], 'rt')
            append_stuff = "".join(append.readlines())
            out.write(append_stuff)

