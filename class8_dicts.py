# These are dictionary setups that control the look, feel, and functionality of the class8 view screens
from CCC_system_setup import companydata
co = companydata()

genre = 'Trucking'
jobcode = co[10] + genre[0]
Trucking_genre = {'table': 'Orders',
                  'genre_tables': ['Orders', 'Interchange', 'Customers', 'Services'],
                  'genre_tables_on': ['on', 'off', 'off', 'off'],
                  'quick_buttons': ['New', 'Mod', 'Inv', 'Rec'],
                  'table_filters': [{'Date Filter': ['Last 60 Days', 'Last 120 Days', 'Last 180 Days', 'Show All']},
                                    {'Pay Filter': ['Uninvoiced', 'Unrecorded', 'Unpaid', 'Show All']},
                                    {'Haul Filter': ['Not Started', 'In-Progress', 'Incomplete', 'Completed',
                                                     'Show All']},
                                    {'Color Filter': ['Haul', 'Invoice', 'Both']}],
                  'task_boxes': [{'Add Items': ['New Job', 'New Customer', 'New Services', 'New from Copy',
                                                'Upload Source', 'Upload Proof', 'Make Manifest']},
                                 {'Edit Items': ['Edit', 'Match', 'Accept', 'Haul+1', 'Haul-1', 'Haul Done', 'Inv+1',
                                                 'Inv-1', 'Inv Emailed', 'Set Col To']},
                                 {'Money Items': ['Inv Edit', 'Quote Edit', 'Package Send', 'Rec Payment',
                                                  'Rec by Acct']},
                                 {'View Docs': ['Source', 'Proof', 'Manifest', 'Interchange', 'Invoice',
                                                'Paid Invoice']},
                                 {'Undo': ['Delete Item', 'Undo Invoice', 'Undo Payment']},
                                 {'Tasks': ['Street Turn', 'Unpulled Containers', 'Assign Drivers', 'Driver Hours',
                                            'Driver Payroll', 'Truck Logs', 'Text Output']}],
                  'container_types': ['40\' GP 9\'6\"', '40\' RS 9\'6\"', '40\' GP 8\'6\"', '40\' RS 8\'6\"',
                                      '20\' GP 8\'6\"', '20\' VH 8\'6\"', '45\' GP 9\'6\"', '45\' VH 9\'6\"',
                                      '53\' Dry', 'LCL', 'RORO']
                  }

Orders_setup = {'table': 'Orders',
                'filter': None,
                'filterval': None,
                'entry data': [['Jo', 'JO', '', jobcode, 'text', 0, 'ok'],
                               ['Order', 'Order', 'Customer Ref No.', 'text', 'text', 0, 'ok'],
                               ['Shipper', 'Shipper', 'Select Customer', 'select', 'customerdata', 0, 'ok'],
                               ['Booking', 'Release', 'Release', 'text', 'text', 0, 'ok'],
                               ['Container', 'Container', 'Container', 'text', 'concheck', 0, 'ok'],
                               ['Type', 'ConType', 'Container Type', 'select', 'container_types', 0, 'ok'],
                               ['Chassis', 'Chassis', '', '', 'text', 0, 'ok'],
                               ['Amount', 'Amount', 'Base Charge', 'text', 'float', 0, 'ok'],
                               ['Company', 'Load At', 'Load At', 'multitext', 'dropblock1', 0, 'Shipper'],
                               ['Date', 'Load Date', 'Load Date', 'date', 'date', 0, 'ok'],
                               ['Company2', 'Deliver To', 'Deliver To', 'multitext', 'dropblock2', 0, 'Shipper'],
                               ['Date2', 'Del Date', 'Del Date', 'date', 'date', 0, 'ok'],
                               ['Commodity', 'Commodity', 'Commodity', 'text', 'text', 0, 'ok'],
                               ['Packing', 'Packing', 'Packing', 'text', 'text', 0, 'ok'],
                               ['Seal', 'Seal', 'Seal', 'text', 'text', 0, 'ok'],
                               ['Pickup', 'Pickup', 'Pickup No.', 'text', 'text', 0, 'ok'],
                               ['Description', 'Description', 'Special Instructions', 'multitext', 'text', 0, 'ok']],
                'colorfilter': ['Hstat'],
                'side data': [{'customerdata': ['People', 'Ptype', 'Trucking', 'Company']},
                              {'dropblock1': ['Orders', 'Shipper', 'get_Shipper', 'Company']},
                              {'dropblock2': ['Orders', 'Shipper', 'get_Shipper', 'Company2']}],
                'jscript': 'dtTrucking'}

Interchange_setup = {'table': 'Interchange',
                     'filter': None,
                     'filterval': None,
                     'headcols': ['Jo', 'Company', 'Date', 'Time', 'Release', 'Container', 'ConType', 'GrossWt',
                                  'Chassis', 'TruckNumber', 'Driver', 'Status'],
                     'colorfilter': ['Status'],
                     'jscript': 'dtHorizontalVerticalExample2'}

Customers_setup = {'table': 'People',
                   'filter': 'Ptype',
                   'filterval': 'Trucking',
                   'headcols': ['Company', 'Addr1', 'Addr2', 'Email', 'Telephone', 'Associate1', 'Associate2'],
                   'colorfilter': None,
                   'jscript': 'dtHorizontalVerticalExample3'}

Services_setup = {'table': 'Services',
                  'filter': None,
                  'filterval': None,
                  'headcols': ['Service', 'Price'],
                  'colorfilter': None,
                  'jscript': 'dtHorizontalVerticalExample4'}