//%attributes = {"shared":true,"preemptive":"indifferent"}
Case of 
	: (Not:C34(Is compiled mode:C492(*)) & (Application type:C494=4D Local mode:K5:1))
		C_LONGINT:C283($win_ref)
		
		$win_ref:=Open form window:C675("method_properties_manager")
		
		SET WINDOW TITLE:C213("Method Properties Manager")
		
		DIALOG:C40("method_properties_manager")
		
		CLOSE WINDOW:C154($win_ref)
		
	: (Is compiled mode:C492(*))
		ALERT:C41("Application is compiled. The Method Property Manger Component can only be run in interepted.")
	: (Application type:C494#4D Local mode:K5:1)
		ALERT:C41("Application is not in Local mode. The Method Property Manager Component can only be run in Local mode.")
	: ((Is compiled mode:C492(*)) & (Application type:C494#4D Local mode:K5:1))
		ALERT:C41("Application is in compiled mode and is not in Local mode. The Method Property Manager Component can only be run in interepeted and Local mode projects.")
End case 