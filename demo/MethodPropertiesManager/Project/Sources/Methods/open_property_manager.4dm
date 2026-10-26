//%attributes = {"shared":true,"preemptive":"indifferent"}
#DECLARE($params : Object)
var $title : Text
var $window; $i; $left; $top; $right; $bottom : Integer

Case of 
	: (Get database parameter:C643(Is host database writable:K37:103)=0)
		ALERT:C41(MPM_text("MPM_HostProtectedError"))
	: (Is compiled mode:C492(*) & (Application type:C494#4D Local mode:K5:1))
		ALERT:C41(MPM_text("MPM_CompiledLocalError"))
		return 
	: (Is compiled mode:C492(*))
		ALERT:C41(MPM_text("MPM_CompiledError"))
		return 
	: (Application type:C494#4D Local mode:K5:1)
		ALERT:C41(MPM_text("MPM_LocalError"))
		return 
End case 

$title:=MPM_text("MPM_WindowTitle")
If (Count parameters:C259=0)
	ARRAY LONGINT:C221($windows; 0)
	WINDOW LIST:C442($windows)
	For ($i; 1; Size of array:C274($windows))
		$window:=$windows{$i}
		If ((Window process:C446($window)=1) & (Get window title:C450($window)=$title))
			GET WINDOW RECT:C443($left; $top; $right; $bottom; $window)
			CALL FORM:C1391($window; Formula:C1597(SET WINDOW RECT:C444($left; $top; $right; $bottom; $window)))
			return 
		End if 
	End for 
	CALL WORKER:C1389(1; Current method name:C684; New object:C1471)
Else 
	// Preserve the host application's menu bar when used as a component.
	$window:=Open form window:C675("method_properties_manager"; Plain form window:K39:10; Horizontally centered:K39:1; Vertically centered:K39:4)
	SET WINDOW TITLE:C213($title; $window)
	DIALOG:C40("method_properties_manager"; $params; *)
End if 