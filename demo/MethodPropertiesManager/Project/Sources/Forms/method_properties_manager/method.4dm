Case of 
	: (Form event code:C388=On Load:K2:1)
		
		// initialize Form.all_methods and Form.method_names to have all methods
		ARRAY TEXT:C222($names_arr; 0)
		Form:C1466.method_names:=New collection:C1472()
		
		METHOD GET NAMES:C1166($names_arr; *)
		ARRAY TO COLLECTION:C1563(Form:C1466.method_names; $names_arr)
		Form:C1466.method_names:=Form:C1466.method_names.orderBy(ck ascending:K85:9)
		Form:C1466.all_methods:=Form:C1466.method_names
		
		Form:C1466.property_read:=MPM_choices(False:C215)
		Form:C1466.property_write:=MPM_choices(True:C214)
		
		Form:C1466.column_sort:=0
End case 