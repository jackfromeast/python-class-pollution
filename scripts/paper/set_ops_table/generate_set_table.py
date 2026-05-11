import re

def abbrev_type(val):
    if val.lower().startswith('attr'):
        return 'A'
    elif val.lower().startswith('item'):
        return 'I'
    elif val.lower() == 'attribute/item':
        return 'A/I'
    return val

def abbrev_origin(val):
    if val.lower().startswith('builtins'):
        return 'B'
    elif val.lower().startswith('operator'):
        return 'O'
    return val

def abbrev_apply(val):
    val = val.replace("Object", "O")
    val = val.replace("Map", "M")
    val = val.replace("Seq", "S")
    # Remove spaces around slashes for consistency
    val = val.replace(" / ", "/").replace(" /", "/").replace("/ ", "/")
    return val

def parse_markdown_table(md_path):
    with open(md_path, 'r') as f:
        lines = [line.rstrip('\n') for line in f]

    rows = []
    i = 0
    while i < len(lines):
        if lines[i].startswith('### '):
            code = lines[i][4:].strip()
            row = {
                'Code': code,
                'Type': '',
                'Apply': '',
                'Origin': '',
                'Instances': '',
                'Packages': '',
                'Spec': ''
            }
            i += 1
            while i < len(lines) and not lines[i].startswith('### '):
                line = lines[i].strip()
                if line.startswith('- Type:'):
                    row['Type'] = abbrev_type(line.split(':', 1)[1].strip())
                elif line.startswith('- Apply:'):
                    row['Apply'] = abbrev_apply(line.split(':', 1)[1].strip())
                elif line.startswith('- Origin:'):
                    row['Origin'] = abbrev_origin(line.split(':', 1)[1].strip())
                elif line.startswith('- Instances:'):
                    row['Instances'] = line.split(':', 1)[1].strip()
                elif line.startswith('- Packages:'):
                    row['Packages'] = line.split(':', 1)[1].strip()
                elif line.startswith('- [http'):
                    row['Spec'] = "N/A"
                i += 1
            rows.append([
                row['Code'],
                row['Type'],
                row['Apply'],
                row['Origin'],
                row['Instances'],
                row['Packages'],
                row['Spec']
            ])
        else:
            i += 1
    return rows

def generate_latex_table(rows):
    latex = []
    latex.append('\\newcounter{rownumset}')
    latex.append('\\newcommand{\\rownumberset}{\\stepcounter{rownumset}\\scriptsize{\\#\\arabic{rownumset}}}')
    latex.append('')
    latex.append('{\\setlength{\\tabcolsep}{2.5pt}')
    latex.append('\\begin{table}[!t]')
    latex.append('  \\centering')
    latex.append('  \\scriptsize')
    latex.append('  \\rowcolors{2}{gray!15}{white}')
    latex.append('  \\caption{Systemization of reflected set operations in Python from builtins and standard libraries.}')
    latex.append('  \\begin{tabular}{l|c@{\\hskip 1.5pt}c@{\\hskip 1.8pt}c|cc|c}')
    latex.append('    \\toprule')
    latex.append('    \\multicolumn{1}{c|}{} & ')
    latex.append('    \\multicolumn{3}{c|}{\\textbf{Features}} & ')
    latex.append('    \\multicolumn{2}{c|}{\\textbf{Prevalence}} & ')
    latex.append('    \\multicolumn{1}{c}{} \\\\')
    latex.append('    \\cmidrule(lr){2-4} \\cmidrule(lr){5-6}')
    latex.append('    \\includesvg[height=0.23cm]{assets/icons/python.svg} \\textbf{Code} & \\rotatebox{90}{\\textbf{Type}} & \\rotatebox{90}{\\textbf{Apply}} & \\rotatebox{90}{\\textbf{Origin}} & \\rotatebox{90}{\\textbf{\\# Inst.}} & \\rotatebox{90}{\\textbf{\\# Pack.}} & \\rotatebox{90}{\\textbf{Spec.}} \\\\')
    latex.append('    \\midrule')
    for row in rows:
        code_latex = row[0].replace('_', r'\_').replace('{', r'\{').replace('}', r'\}')
        code = f'\\scriptsize{{\\texttt{{{code_latex}}}}}'
        features = ' & '.join([
            f'\\scriptsize{{{row[1]}}}',
            f'\\scriptsize{{{abbrev_apply(row[2])}}}',
            f'\\scriptsize{{{row[3]}}}'
        ])
        prevalence = ' & '.join(row[4:6])
        spec = f'[{row[6]}]'
        latex.append(f'    {code} & {features} & {prevalence} & {spec} \\\\')
    latex.append('    \\bottomrule')
    latex.append('  \\end{tabular}')
    latex.append('  \\caption*{\\scriptsize \\textbf{Legend:} A: Attribute; I: Item; O: Object; M: Mapping; S: Sequence; B: Builtin; O: Operator.}')
    latex.append('  \\label{tab:set-table}')
    latex.append('\\end{table}}')
    return '\n'.join(latex)

if __name__ == '__main__':
    rows = parse_markdown_table('/home/jackfromeast/Desktop/python-class-pollution/scripts/paper/set_ops_table/set.md')
    latex = generate_latex_table(rows)
    with open('/home/jackfromeast/Desktop/python-class-pollution/scripts/paper/set_ops_table/set_table.tex', 'w') as f:
        f.write(latex)