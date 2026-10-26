//%attributes = {"invisible":true}
C_COLLECTION:C1488($0; $2; $all_methods; $updated_col)
C_TEXT:C284($1; $property; $method_name; $path)
C_BOOLEAN:C305($show_invisible; $show_preemptive_capable; $show_preemptive_incapable; $show_preemptive_indifferent; $show_published_web; $show_published_soap; $show_published_wsdl\
; $show_shared; $show_published_sql; $show_execute_on_server)
C_OBJECT:C1216($atr_o)

$property:=$1
$all_methods:=$2

// If the user has selected "Any" display all methods
If ($property="Any")
	$updated_col:=$all_methods
	
	// Otherwise go through each method and see if it has a property that matches what the user selected
Else 
	$updated_col:=New collection:C1472()
	$atr_o:=New object:C1471()
	
	For each ($method_name; $all_methods)
		
		// Get the properties of the method and store it in $atr_o
		$path:=METHOD Get path:C1164(Path project method:K72:1; $method_name)
		METHOD GET ATTRIBUTES:C1334($path; $atr_o; *)
		
		
		// If there is a match add it to the collection on methods to be displayed
		$show_invisible:=(($property="Invisible") & ($atr_o.invisible))
		$show_preemptive_capable:=(($property="Preemptive Capable") & ($atr_o.preemptive="capable"))
		$show_preemptive_incapable:=(($property="Preemptive Incapable") & ($atr_o.preemptive="incapable"))
		$show_preemptive_indifferent:=(($property="Preemptive Indifferent") & ($atr_o.preemptive="indifferent"))
		$show_published_web:=(($property="Published Web") & ($atr_o.publishedWeb))
		$show_published_soap:=(($property="Published Soap") & ($atr_o.publishedSoap))
		$show_published_wsdl:=(($property="Published WSDL") & ($atr_o.publishedWsdl))
		$show_shared:=(($property="Shared") & ($atr_o.shared))
		$show_published_sql:=(($property="Published SQL") & ($atr_o.publishedSql))
		$show_execute_on_server:=(($property="Executed On Server") & ($atr_o.executedOnServer))
		
		If ($show_invisible | $show_preemptive_capable | $show_preemptive_incapable | $show_preemptive_indifferent | $show_published_web\
			 | $show_published_soap | $show_published_wsdl | $show_shared | $show_published_sql | $show_execute_on_server)
			$updated_col.push($method_name)
		End if 
		
	End for each 
End if 

$0:=$updated_col