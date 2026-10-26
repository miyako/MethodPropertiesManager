//%attributes = {"invisible":true}
#DECLARE($editing : Boolean) -> $choices : Object
var $key : Text

$choices:=New object
If ($editing)
	$choices.keys:=New collection("Any"; "Invisible"; "Shared"; "Published Web"; "Executed on Server"; "Preemptive"; "Published SOAP"; "Published WSDL"; "Published SQL")
Else
	$choices.keys:=New collection("Any"; "Invisible"; "Shared"; "Published Web"; "Executed on Server"; "Preemptive Capable"; "Preemptive Incapable"; "Preemptive Indifferent"; "Published SOAP"; "Published WSDL"; "Published SQL")
End if
$choices.values:=New collection
For each ($key; $choices.keys)
	$choices.values.push(MPM_text("MPM_Choice"+Replace string($key; " "; "")))
End for each
$choices.index:=0
