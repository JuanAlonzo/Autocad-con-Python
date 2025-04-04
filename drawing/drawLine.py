from pyautocad import Autocad, APoint

acad = Autocad()
acad.prompt("Hello! Autocad from Python\n")

p1 = APoint(274104.2979, 8671860.4027)  # Coordinates from pole 1
p2 = APoint(274204.2979, 8671960.4027)  # Coordinates from end

acad.model.AddLine(p1, p2)
