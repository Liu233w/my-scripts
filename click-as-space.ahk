toggle := 1
^z::
toggle := !toggle
return

#if toggle
lbutton::space
space::lbutton
