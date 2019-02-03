import webbrowser as wb

try: 
	from googlesearch import search 
except ImportError: 
	print("No module named 'google' found") 

# to search 
query = "datasheet " + "bc547"

for j in search(query, tld="co.uk", num=1, stop=1, pause=2): 
    print(j) 
    wb.open_new_tab(j)