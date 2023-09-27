import tabula

# Read the PDF file and extract all tables
tables = tabula.read_pdf(
    "CapePMX-Report-310723.pdf",
    pages="1",
    multiple_tables=False,
    guess=False,
    area=[343.231, 85.531, 576.025, 258.081],
)

# Iterate over the tables and examine their structures
for i in range(len(tables)):
    tables[i].to_csv(f"all_pages_table{i}.csv")
