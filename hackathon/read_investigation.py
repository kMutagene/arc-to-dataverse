from fsspreadsheet import workbook
from fsspreadsheet.xlsx import Xlsx
from arctrl.xlsx import XlsxController
from arctrl.json import JsonController

# load investigation xlsx file
book = Xlsx.from_xlsx_file(r'C:\Users\schne\Downloads\ArcPrototype\isa.investigation.xlsx')

# convert xlsx file into Investigation object
inv = XlsxController.Investigation().from_fs_workbook(book)

inv.Title

# convert investigation object to ro-crate string
inv_ro_crate = JsonController.Investigation().to_rocrate_json_string(inv)
