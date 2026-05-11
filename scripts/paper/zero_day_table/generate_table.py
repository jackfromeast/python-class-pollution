import pandas as pd

def format_stars(stars):
    try:
        stars = int(stars)
        if stars >= 1000:
            return f"{stars/1000:.1f}K"
        return str(stars)
    except:
        return str(stars)

# Read the CSV with two header rows
df = pd.read_csv("The Python World-Class Pollution - All-in-one - 0528.csv", header=[0, 1])
df.columns = ['_'.join([str(a).strip(), str(b).strip()]).strip('_') for a, b in df.columns]

cols_mapping = {
    "Application": 0,
    "Stars": 1,
    "URL": 2,
    "Codeql": 3,
    "Confirmed (Function-level)": 4,
    "Func Name (Path)": 5,
    "FP Reason": 6,
    "Types_Get": 7,
    "Types_Set": 8,
    "Input_Triggering": 9,
    "Input_Remote": 10,
    "Input_Local": 11,
    "Status": 12,
    "Comment": 13,
}

rows = []
for row in df.itertuples(index=False):
    app = row[cols_mapping["Application"]]
    if not isinstance(app, str) or app.strip() == "":
        continue
    
    comment = row[cols_mapping["Comment"]]
    if not (isinstance(comment, str) and "Selected." in comment):
      continue
    
    stars = format_stars(row[cols_mapping["Stars"]])
    version = "-"
    input_type = row[cols_mapping["Input_Triggering"]] if pd.notna(row[cols_mapping["Input_Triggering"]]) else "-"
    get_primitive = row[cols_mapping["Types_Get"]] if pd.notna(row[cols_mapping["Types_Get"]]) else "-"
    set_primitive = row[cols_mapping["Types_Set"]] if pd.notna(row[cols_mapping["Types_Set"]]) else "-"
    num_targets = "-"
    exploit_target = "-"
    consequence = "-"
    status = row[cols_mapping["Status"]] if pd.notna(row[cols_mapping["Status"]]) else "-"
    latex_row = f"{app} & {stars} & {version} & {input_type} & {get_primitive} & {set_primitive} & {num_targets} & {exploit_target} & {consequence} & {status} \\\\"
    rows.append(latex_row)

for row in rows:
    print(row)