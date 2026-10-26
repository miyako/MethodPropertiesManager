//%attributes = {"invisible":true}
#DECLARE($id : Text)->$text : Text
$text:=Localized string:C991($id)
ASSERT(OK=1; "Missing localisation resource: "+$id)
