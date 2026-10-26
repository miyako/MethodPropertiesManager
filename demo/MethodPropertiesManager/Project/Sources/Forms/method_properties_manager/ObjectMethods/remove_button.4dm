C_OBJECT:C1216($mod_obj)
C_TEXT:C284($method_name; $path)

$mod_obj:=New object:C1471()

// Store in $mod_obj the property that needs to be set
Case of 
	: (Form:C1466.property_write.currentValue="Preemptive Capable")
		$mod_obj.preemptive:="indifferent"
	: (Form:C1466.property_write.currentValue="Preemptive Incapable")
		$mod_obj.preemptive:="indifferent"
	: (Form:C1466.property_write.currentValue="Preemptive Indifferent")
		$mod_obj.preemptive:="indifferent"
	: (Form:C1466.property_write.currentValue="Invisible")
		$mod_obj.invisible:=False:C215
	: (Form:C1466.property_write.currentValue="Published Web")
		$mod_obj.publishedWeb:=False:C215
	: (Form:C1466.property_write.currentValue="Published SOAP")
		$mod_obj.publishedSoap:=False:C215
	: (Form:C1466.property_write.currentValue="Published WSDL")
		$mod_obj.publishedWsdl:=False:C215
	: (Form:C1466.property_write.currentValue="Shared")
		$mod_obj.shared:=False:C215
	: (Form:C1466.property_write.currentValue="Published SQL")
		$mod_obj.publishedSql:=False:C215
	: (Form:C1466.property_write.currentValue="Executed on Server")
		$mod_obj.executedOnServer:=False:C215
End case 

// update each selected method with the property stored in $mod_obj
For each ($method_name; Form:C1466.selected_methods)
	$path:=METHOD Get path:C1164(Path project method:K72:1; $method_name)
	METHOD SET ATTRIBUTES:C1335($path; $mod_obj; *)
End for each 

// update the display after the change
Form:C1466.method_names:=update_display(Form:C1466.property_read.currentValue; Form:C1466.all_methods)
