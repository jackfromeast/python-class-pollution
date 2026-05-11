import re

def parse_markdown_table(md_path):
  with open(md_path, 'r') as f:
    lines = [line.rstrip('\n') for line in f]

  rows = []
  i = 0
  while i < len(lines):
    # Find the start of an entry
    if lines[i].startswith('### '):
      code = lines[i][4:].strip()
      row = {
        'Code': code,
        'Type': '',
        'Origin': '',
        'Order': '',
        'Dunder': '',
        'Method': '',
        'Other': '',
        'Instances': '',
        'Packages': '',
        'Spec': ''
      }
      i += 1
      # Parse fields
      while i < len(lines) and not lines[i].startswith('### '):
        line = lines[i].strip()
        if line.startswith('- Type:'):
          row['Type'] = line.split(':', 1)[1].strip()
        elif line.startswith('- Origin:'):
          row['Origin'] = line.split(':', 1)[1].strip()
        elif line.startswith('- Order:'):
          row['Order'] = line.split(':', 1)[1].replace('-order', '').strip()
        elif line.startswith('- Apply:'):
          raw_apply = line.split(':', 1)[1].strip()
          row['Apply'] = map_apply(raw_apply)
        elif line.startswith('- Dunder:'):
          row['Dunder'] = line.split(':', 1)[1].strip()
        elif line.startswith('- Method:'):
          row['Method'] = line.split(':', 1)[1].strip()
        elif line.startswith('- Other:'):
          row['Other'] = line.split(':', 1)[1].strip()
        elif line.startswith('- Instances:'):
          row['Instances'] = line.split(':', 1)[1].strip()
        elif line.startswith('- Packages:'):
          row['Packages'] = line.split(':', 1)[1].strip()
        elif line.startswith('- [http'):
          # Spec is a markdown link, extract the URL
          match = re.search(r'\[(http[^\]]+)\]', line)
          if match:
            # row['Spec'] = match.group(1)
            row['Spec'] =  "N/A"
        i += 1
      # Append in the order for your table
      rows.append([
        row['Code'],
        row['Type'],
        row['Apply'],
        row['Origin'],
        row['Order'],
        row['Dunder'],
        row['Method'],
        row['Other'],
        row['Instances'],
        row['Packages'],
        row['Spec']
      ])
    else:
      i += 1
  return rows

def latex_symbol(val):
  if val.lower() == 'yes' or val.lower() == 'y':
    return '\\fullcircle'
  elif val.lower() == 'partial' or val.lower() == 'p':
    return '\\partialcircle'
  elif val.lower() == 'n':
    return '\\Circle'
  else:
    return '\\fullcircle' if val == '●' else '\\partialcircle' if val == '◐' else val

def map_apply(val):
  # Replace Obj/Map/Seq or combinations with O/M/S
  val = val.replace('Obj', 'O')
  val = val.replace('Map', 'M')
  val = val.replace('Seq', 'S')
  return val


def generate_latex_table(rows):
  latex = []
  latex.append('\\newcounter{rownumget}')
  latex.append('\\newcommand{\\rownumber}{\\stepcounter{rownumget}\\scriptsize{\\#\\arabic{rownumget}}}')
  latex.append('\\newcommand{\\fullcircle}{\\CIRCLE}')
  latex.append('\\newcommand{\\partialcircle}{\\LEFTcircle}')
  latex.append('')
  latex.append('\\begin{table*}[!t]')
  latex.append('  \\centering')
  latex.append('  \\scriptsize')
  latex.append('  \\rowcolors{1}{white}{gray!15}')
  latex.append('  \\caption{Systemization of reflected get operations in Python from builtins and standard libraries.}')
  latex.append('  \\begin{tabular}{ll|c@{\\hskip 6pt}c@{\\hskip 6pt}c@{\\hskip 6pt}c|ccc|cc|c}')
  latex.append('    \\toprule')
  latex.append('    \\multicolumn{2}{c|}{} & ')
  latex.append('    \\multicolumn{4}{c|}{\\includesvg[height=0.20cm]{assets/icons/star.svg} \\textbf{Features}} & ')
  latex.append('    \\multicolumn{3}{c|}{\\includesvg[height=0.22cm]{assets/icons/setting.svg} \\textbf{Capabilities}} & ')
  latex.append('    \\multicolumn{2}{c|}{\\includesvg[height=0.22cm]{assets/icons/connection.svg} \\textbf{Prevalence}} & ')
  latex.append('    \\multicolumn{1}{c}{} \\\\')
  latex.append('    \\cmidrule(lr){3-6} \\cmidrule(lr){7-9} \\cmidrule(lr){10-11}')
  latex.append('    & \\includesvg[height=0.23cm]{assets/icons/python.svg} \\textbf{Code} & \\textbf{Type} & \\textbf{Apply} & \\textbf{Origin} & \\textbf{Order} & ')
  latex.append('    \\textbf{Dunder} & \\textbf{Method} & \\textbf{Other} & ')
  latex.append('    \\textbf{\\# Inst.} & \\textbf{\\# Pack.} & \\includesvg[height=0.22cm]{assets/icons/constraint.svg} \\textbf{Spec.} \\\\')
  latex.append('    \\midrule')

  # Find the index for the first 'Item' and first 'Attr/Item'
  first_item_idx = None
  first_attritem_idx = None
  for idx, row in enumerate(rows):
      typ = row[1].strip().lower()
      if first_item_idx is None and typ == 'item':
          first_item_idx = idx
      if first_attritem_idx is None and typ == 'attr/item':
          first_attritem_idx = idx
      if first_item_idx is not None and first_attritem_idx is not None:
          break

  for idx, row in enumerate(rows):
    # Add rownumber macro as the first column
    code_latex = row[0].replace('_', r'\_').replace('{', r'\{').replace('}', r'\}')
    code = f'\\scriptsize{{\\texttt{{{code_latex}}}}}'
    features = ' & '.join([f'\\scriptsize{{{f}}}' for f in row[1:5]])
    capabilities = ' & '.join(latex_symbol(x) for x in row[5:8])
    prevalence = ' & '.join(row[8:10])
    spec = f'[{row[10]}]'
    latex.append(f'    \\rownumber & {code} & {features} & {capabilities} & {prevalence} & {spec} \\\\')
    # Insert double midrule after the last "Item" row before the first "Attr/Item"
    if first_item_idx is not None and idx == first_item_idx - 1:
      latex.append('    \\midrule')
    elif first_attritem_idx is not None and idx == first_attritem_idx - 1:
      latex.append('    \\midrule')

  latex.append('    \\bottomrule')
  latex.append('  \\end{tabular}')
  latex.append("""  \caption*{\scriptsize \textbf{Legend:} 
    O: Object; M: Mapping; S: Sequence; 
    \fullcircle: Fully Supported; 
    \partialcircle: Conditionally Supported (\#6 and \#7 apply for class objects with \texttt{\_\_dict\_\_});
    \Circle: Not Supported.}""")  
  latex.append('  \\label{tab:get-table}')
  latex.append('\\end{table*}')
  return '\n'.join(latex)

if __name__ == '__main__':
  rows = parse_markdown_table('/home/jackfromeast/Desktop/python-class-pollution/scripts/paper/get_ops_table/get.md')
  latex = generate_latex_table(rows)
  with open('/home/jackfromeast/Desktop/python-class-pollution/scripts/paper/get_ops_table/get_table.tex', 'w') as f:
    f.write(latex)