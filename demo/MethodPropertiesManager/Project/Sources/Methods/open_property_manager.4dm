//%attributes = {"shared":true,"preemptive":"indifferent"}
#DECLARE($params : Object)
var $title : Text
var $window; $i; $left; $top; $right; $bottom : Integer

Case of
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
If (Count parameters=0)
	ARRAY LONGINT($windows; 0)
	WINDOW LIST($windows)
	For ($i; 1; Size of array($windows))
		$window:=$windows{$i}
		If ((Window process($window)=1) & (Get window title($window)=$title))
			GET WINDOW RECT($left; $top; $right; $bottom; $window)
			CALL FORM($window; Formula(SET WINDOW RECT($left; $top; $right; $bottom; $window)))
			return
		End if
	End for
	CALL WORKER(1; Current method name; New object)
Else
	// Preserve the host application's menu bar when used as a component.
	$window:=Open form window:C675("method_properties_manager"; Plain form window; Horizontally centered; Vertically centered)
	SET WINDOW TITLE:C213($title; $window)
	DIALOG:C40("method_properties_manager"; $params; *)
End if