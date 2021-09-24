#MaxThreadsPerHotkey 2

$ESC::pause

;;; 自动点击
$space::
loop{
click
sleep, 50
}Until Not GetKeyState("space", "P")
return

Toggle := false
^z::
Toggle := !Toggle
if (Toggle) {
  Loop
  {
      Click
      Sleep 100
  } Until !Toggle
}
Return
