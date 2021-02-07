Pause ON
$ESC::pause

;;; 自动点击
$f5::
loop{
click
sleep, 100
}Until Not GetKeyState("f5", "P")
return

$up::
loop{
click right
sleep, 200
}Until Not GetKeyState("f5", "P")
return

KeyDown := false
$f4::
KeyDown := !KeyDown
If KeyDown
	SendInput {click Right down}
Else
	SendInput {click Right up}
Return

Toggle := false
^z::
Toggle := !Toggle
#If Toggle
Loop
{
    Click
    Sleep 100
} Until !Toggle
#If
Return
