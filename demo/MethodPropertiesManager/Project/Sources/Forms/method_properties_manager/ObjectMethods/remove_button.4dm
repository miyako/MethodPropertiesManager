C_OBJECT:C1216($mod_obj)
C_TEXT:C284($method_name; $path)

$mod_obj:=New object:C1471()

// Store in $mod_obj the property that needs to be set
Case of 
	: (Form:C1466.property_write.keys[Form:C1466.property_write.index]="Preemptive Capable")
		$mod_obj.preemptive:="indifferent"
	: (Form:C1466.property_write.keys[Form:C1466.property_write.index]="Preemptive Incapable")
		$mod_obj.preemptive:="indifferent"
	: (Form:C1466.property_write.keys[Form:C1466.property_write.index]="Preemptive Indifferent")
		$mod_obj.preemptive:="indifferent"
	: (Form:C1466.property_write.keys[Form:C1466.property_write.index]="Invisible")
		$mod_obj.invisible:=False:C215
	: (Form:C1466.property_write.keys[Form:C1466.property_write.index]="Published Web")
		$mod_obj.publishedWeb:=False:C215
	: (Form:C1466.property_write.keys[Form:C1466.property_write.index]="Published SOAP")
		$mod_obj.publishedSoap:=False:C215
	: (Form:C1466.property_write.keys[Form:C1466.property_write.index]="Published WSDL")
		$mod_obj.publishedWsdl:=False:C215
	: (Form:C1466.property_write.keys[Form:C1466.property_write.index]="Shared")
		$mod_obj.shared:=False:C215
	: (Form:C1466.property_write.keys[Form:C1466.property_write.index]="Published SQL")
		$mod_obj.publishedSql:=False:C215
	: (Form:C1466.property_write.keys[Form:C1466.property_write.index]="Executed on Server")
		$mod_obj.executedOnServer:=False:C215
End case 

// update each selected method with the property stored in $mod_obj
For each ($method_name; Form:C1466.selected_methods)
	$path:=METHOD Get path:C1164(Path project method:K72:1; $method_name)
	METHOD SET ATTRIBUTES:C1335($path; $mod_obj; *)
End for each 

// update the display after the change
Form:C1466.method_names:=update_display(Form:C1466.property_read.keys[Form:C1466.property_read.index]; Form:C1466.all_methods)
