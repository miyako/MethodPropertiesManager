
Case of 
	: (Form event code:C388=On Load:K2:1)
		
		OBJECT SET VISIBLE:C603(*; "apply_button"; True:C214)
		OBJECT SET VISIBLE:C603(*; "remove_button"; True:C214)
		OBJECT SET VISIBLE:C603(*; "capable_button"; False:C215)
		OBJECT SET VISIBLE:C603(*; "incapable_button"; False:C215)
		OBJECT SET VISIBLE:C603(*; "indifferent_button"; False:C215)
		
	: (Form event code:C388=On Data Change:K2:15)
		// If Preemptive is selected make apply and remove invisible and the preemptive options visible
		If (Form:C1466.property_write.keys[Form:C1466.property_write.index]="Preemptive")
			OBJECT SET VISIBLE:C603(*; "apply_button"; False:C215)
			OBJECT SET VISIBLE:C603(*; "remove_button"; False:C215)
			OBJECT SET VISIBLE:C603(*; "capable_button"; True:C214)
			OBJECT SET VISIBLE:C603(*; "incapable_button"; True:C214)
			OBJECT SET VISIBLE:C603(*; "indifferent_button"; True:C214)
			
		Else 
			// Otherwise do the opposite
			OBJECT SET VISIBLE:C603(*; "apply_button"; True:C214)
			OBJECT SET VISIBLE:C603(*; "remove_button"; True:C214)
			OBJECT SET VISIBLE:C603(*; "capable_button"; False:C215)
			OBJECT SET VISIBLE:C603(*; "incapable_button"; False:C215)
			OBJECT SET VISIBLE:C603(*; "indifferent_button"; False:C215)
		End if 
End case 
