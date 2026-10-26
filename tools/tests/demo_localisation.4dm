// Run with tools/tool4d.py demo/MethodPropertiesManager tools/tests/demo_localisation.4dm.
var $language; $id; $text : Text
var $read; $write; $result; $languageResult : Object
var $ids; $methods; $filtered; $englishKeys : Collection
var $i : Integer

$ids:=New collection("MPM_WindowTitle"; "MPM_FilterLabel"; "MPM_EditLabel"; "MPM_Methods"; "MPM_Count"; "MPM_Apply"; "MPM_Remove"; "MPM_Capable"; "MPM_Incapable"; "MPM_Indifferent"; "MPM_CompiledError"; "MPM_LocalError"; "MPM_CompiledLocalError")
$methods:=New collection("MPM_choices"; "open_property_manager")
$result:=New object("success"; True; "languages"; New collection)

For each ($language; New collection("en"; "ja"))
	SET DATABASE LOCALIZATION($language; *)
	ASSERT(OK=1; "Language resources must be selectable")
	For each ($id; $ids)
		$text:=MPM_text($id)
		ASSERT(OK=1; "Missing XLIFF ID: "+$id)
		ASSERT(Length($text)>0; "Empty XLIFF target: "+$id)
	End for each
	$read:=MPM_choices(False)
	$write:=MPM_choices(True)
	ASSERT($read.keys.length=11; "Read filter count")
	ASSERT($write.keys.length=9; "Write choice count")
	ASSERT($read.keys.length=$read.values.length; "Read keys and labels must align")
	ASSERT($write.keys.length=$write.values.length; "Write keys and labels must align")
	ASSERT(($read.index=0) & ($write.index=0); "Any must be selected initially")
	ASSERT($read.keys[$read.index]="Any"; "Read initial stable key")
	ASSERT($write.keys[$write.index]="Any"; "Write initial stable key")
	ASSERT($write.keys[5]="Preemptive"; "Preemptive controls use the stable key")
	For ($i; 0; $read.keys.length-1)
		$text:=MPM_text("MPM_Choice"+Replace string($read.keys[$i]; " "; ""))
		ASSERT(OK=1; "Missing read choice translation")
		ASSERT(($text=$read.values[$i]) & (Length($text)>0); "Read choice translation")
	End for
	For ($i; 0; $write.keys.length-1)
		$text:=MPM_text("MPM_Choice"+Replace string($write.keys[$i]; " "; ""))
		ASSERT(OK=1; "Missing write choice translation")
		ASSERT(($text=$write.values[$i]) & (Length($text)>0); "Write choice translation")
	End for
	If ($language="en")
		$englishKeys:=$read.keys
		ASSERT($read.values[0]="Any"; "English Any")
		ASSERT(MPM_text("MPM_WindowTitle")="Method Properties Manager"; "English title")
	Else
		ASSERT(JSON Stringify($read.keys)=JSON Stringify($englishKeys); "Language must not change property keys")
		ASSERT($read.values[0]="すべて"; "Japanese Any")
		ASSERT(MPM_text("MPM_WindowTitle")="メソッドプロパティマネージャー"; "Japanese title")
		ASSERT(MPM_text("MPM_Apply")="適用"; "Japanese Apply")
		ASSERT(MPM_text("MPM_Remove")="解除"; "Japanese Remove")
		ASSERT(Position(Char(13); MPM_text("MPM_EditLabel"))>0; "Japanese multiline label keeps CR")
	End if
	$filtered:=update_display("Any"; $methods)
	ASSERT($filtered.length=2; "Any returns the supplied methods")
	$filtered:=update_display("Invisible"; $methods)
	ASSERT(($filtered.length=1) & ($filtered[0]="MPM_choices"); "Invisible filter uses supplied methods")
	$filtered:=update_display("Shared"; $methods)
	ASSERT(($filtered.length=1) & ($filtered[0]="open_property_manager"); "Shared filter is language independent")
	$languageResult:=New object("language"; $language; "readLabels"; $read.values; "writeLabels"; $write.values)
	$result.languages.push($languageResult)
End for each

File("/PACKAGE/agent-test.txt").setText(JSON Stringify($result; *))
QUIT 4D
