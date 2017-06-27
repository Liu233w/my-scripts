;;; 自动点击
$f5::
loop{
click
sleep, 200
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
