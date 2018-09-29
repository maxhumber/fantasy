import pandas as pd
from xlsxwriter.utility import xl_rowcol_to_cell
from hockey.utils import CATEGORIES

df = pd.read_csv('hockey/draft/list.csv')

# Create a Pandas Excel writer using XlsxWriter as the engine.
writer = pd.ExcelWriter('hockey/draft/list.xlsx', engine='xlsxwriter', options={'nan_inf_to_errors': True})

# Convert the dataframe to an XlsxWriter Excel object.
df.to_excel(excel_writer=writer, sheet_name='draft', index=False)

workbook  = writer.book
worksheet = writer.sheets['draft']

# find area to format
first = df.columns.get_loc(CATEGORIES[0])
first_column = xl_rowcol_to_cell(1, first)[0]
last = df.columns.get_loc(CATEGORIES[-1])
last_column = xl_rowcol_to_cell(1, last)[0]
first_row = 2
last_row = df.shape[0] + 1
area = f'{first_column}{first_row}:{last_column}{last_row}'

# add formatting
percent_format = workbook.add_format({'num_format': '0.0%'})
worksheet.set_column(f'{area}', None, percent_format)
worksheet.conditional_format(f'{area}', {'type': '3_color_scale'})

# convert to table
df = df.fillna('')
last_column = xl_rowcol_to_cell(0, len(df.columns)-1)[0]
data = [[i for i in row] for row in df.itertuples(index=False)]
header = [{'header': c} for c in df.columns]
worksheet.add_table(
    f'A1:{last_column}{last_row}',
    {'data': data, 'columns': header,
    'style': 'Table Style Light 1'}
)

# Close the Pandas Excel writer and output the Excel file.
writer.save()
