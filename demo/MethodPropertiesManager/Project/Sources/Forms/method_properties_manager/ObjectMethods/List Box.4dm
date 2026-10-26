
Case of 
	: (Form event code:C388=On Double Clicked:K2:5)
		If (Form:C1466.selected_methods.length=1)
			METHOD OPEN PATH:C1213(Form:C1466.selected_methods[0]; 1; *)
		End if 
	: (Form event code:C388=On Header Click:K2:40)
		
		Case of 
			: (Form:C1466.column_sort=0)
				
				Form:C1466.method_names:=Form:C1466.method_names.orderBy(ck descending:K85:8)
				Form:C1466.column_sort:=1
			: (Form:C1466.column_sort=1)
				Form:C1466.method_names:=Form:C1466.method_names.orderBy(ck ascending:K85:9)
				Form:C1466.column_sort:=2
			: (Form:C1466.column_sort=2)
				Form:C1466.method_names:=Form:C1466.method_names.orderBy(ck descending:K85:8)
				Form:C1466.column_sort:=1
		End case 
End case 