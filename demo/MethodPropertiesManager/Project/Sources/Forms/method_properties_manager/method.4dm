Case of 
	: (Form event code:C388=On Load:K2:1)
		
		// initialize Form.all_methods and Form.method_names to have all methods
		ARRAY TEXT:C222($names_arr; 0)
		Form:C1466.method_names:=New collection:C1472()
		
		METHOD GET NAMES:C1166($names_arr; *)
		ARRAY TO COLLECTION:C1563(Form:C1466.method_names; $names_arr)
		Form:C1466.method_names:=Form:C1466.method_names.orderBy(ck ascending:K85:9)
		Form:C1466.all_methods:=Form:C1466.method_names
		
		// initialize the values for the drop down menu that manages the display
		Form:C1466.property_read:=New object:C1471()
		Form:C1466.property_read.values:=New collection:C1472("Any"; "Invisible"; "Shared"; "Published Web"; "Executed on Server"; "Preemptive Capable"; \
			"Preemptive Incapable"; "Preemptive Indifferent"; "Published SOAP"; "Published WSDL"; "Published SQL")
		Form:C1466.property_read.index:=-1
		Form:C1466.property_read.currentValue:="Any"
		
		// initialize the values for the drop down menu that manages editing properties
		Form:C1466.property_write:=New object:C1471()
		Form:C1466.property_write.values:=New collection:C1472("Any"; "Invisible"; "Shared"; "Published Web"; "Executed on Server"; "Preemptive"; "Published SOAP"; "Published WSDL"; "Published SQL")
		Form:C1466.property_write.index:=-1
		Form:C1466.property_write.currentValue:="Any"
		
		Form:C1466.column_sort:=0
End case 