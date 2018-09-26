import pandas as pd
from xlsxwriter.utility import xl_rowcol_to_cell
from hockey.utils import CATEGORIES

df = pd.read_csv('hockey/list.csv')

# Create a Pandas Excel writer using XlsxWriter as the engine.
writer = pd.ExcelWriter('hockey/sandbox.xlsx', engine='xlsxwriter', options={'nan_inf_to_errors': True})

# Convert the dataframe to an XlsxWriter Excel object.
df.to_excel(excel_writer=writer, sheet_name='draft', index=False)

workbook  = writer.book
worksheet = writer.sheets['draft']

# find area to format
first = df.columns.get_loc('goals')
first_column = xl_rowcol_to_cell(1, first)[0]
last = df.columns.get_loc('shutouts')
last_column = xl_rowcol_to_cell(1, 17)[0]
first_row = 2
last_row = df.shape[0] + 1
area = f'{first_column}{first_row}:{last_column}{last_row}'

# add formatting
percent_format = workbook.add_format({'num_format': '0.0%'})
worksheet.set_column(f'{area}', None, percent_format)
worksheet.conditional_format(f'{area}', {'type': '3_color_scale'})

# convert to table
df.columns.get_loc(df.columns[-1])
xl_rowcol_to_cell(0, 17)
worksheet.add_table('A1:R301')

data = [[i for i in row] for row in df.itertuples()]
header = [{'header': c} for c in df.columns]
worksheet.add_table('A1:R301', {'data': data, 'columns': header})

# Close the Pandas Excel writer and output the Excel file.
writer.save()
