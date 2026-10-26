C_OBJECT:C1216($mod_obj)
C_TEXT:C284($method_name; $path)

$mod_obj:=New object:C1471()

// Store in $mod_obj the property that needs to be set
$mod_obj.preemptive:="indifferent"

// update each selected method with the property stored in $mod_obj
For each ($method_name; Form:C1466.selected_methods)
	$path:=METHOD Get path:C1164(Path project method:K72:1; $method_name)
	METHOD SET ATTRIBUTES:C1335($path; $mod_obj; *)
End for each 

// update the display after the change
Form:C1466.method_names:=update_display(Form:C1466.property_read.keys[Form:C1466.property_read.index]; Form:C1466.all_methods)