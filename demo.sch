v 20080127 1
C 40000 40000 0 0 0 title-B.sym
C 40700 49000 1 0 0 vsin-1.sym
{
T 41400 49650 5 10 1 1 0 0 1
refdes=V1
T 41400 49850 5 10 0 0 0 0 1
device=vsin
T 41400 50050 5 10 0 0 0 0 1
footprint=none
T 41400 49450 5 10 1 1 0 0 1
value=generator(1)
}
C 40700 47000 1 0 0 vpulse-1.sym
{
T 41400 47650 5 10 1 1 0 0 1
refdes=V2
T 41400 47850 5 10 0 0 0 0 1
device=vpulse
T 41400 48050 5 10 0 0 0 0 1
footprint=none
T 41400 47450 5 10 1 1 0 0 1
value=pulse 0 10 10n 10n 100n 5u 10u
}
C 40900 48700 1 0 0 gnd-1.sym
C 40900 46700 1 0 0 gnd-1.sym
C 41100 50100 1 0 0 output-1.sym
{
T 41200 50400 5 10 0 0 0 0 1
device=OUTPUT
T 42000 50100 5 10 0 0 0 0 1
netname=sin
}
C 41200 48100 1 0 0 output-1.sym
{
T 41300 48400 5 10 0 0 0 0 1
device=OUTPUT
T 42100 48100 5 10 0 0 0 0 1
netname=squ
}
C 45500 49300 1 90 0 capacitor-1.sym
{
T 44800 49500 5 10 0 0 90 0 1
device=CAPACITOR
T 45600 49700 5 10 1 1 0 0 1
refdes=C1
T 44600 49500 5 10 0 0 90 0 1
symversion=0.1
T 45600 49500 5 10 1 1 0 0 1
value=1.0n
}
C 44400 50100 1 0 0 resistor-2.sym
{
T 44800 50450 5 10 0 0 0 0 1
device=RESISTOR
T 44600 50600 5 10 1 1 0 0 1
refdes=R1
T 44600 50400 5 10 1 1 0 0 1
value=10k
}
C 45200 49000 1 0 0 gnd-1.sym
C 43500 50100 1 0 0 input-1.sym
{
T 43500 50400 5 10 0 0 0 0 1
device=INPUT
T 43300 49600 5 10 0 0 0 0 1
netname=squ
}
C 45400 50100 1 0 0 output-1.sym
{
T 45500 50400 5 10 0 0 0 0 1
device=OUTPUT
T 46200 50100 5 10 0 0 0 0 1
netname=out
}
C 40500 45800 1 0 0 gnucap-directive-1.sym
{
T 40600 46000 5 10 0 1 0 0 1
device=directive
T 40600 46100 5 10 1 1 0 0 1
refdes=A1
T 40600 45800 5 10 1 1 0 0 1
value=.print tran v(squ)
}
C 40500 43900 1 0 0 gnucap-directive-1.sym
{
T 40600 44100 5 10 0 1 0 0 1
device=directive
T 40600 44200 5 10 1 1 0 0 1
refdes=A4
T 40600 43900 5 10 1 1 0 0 1
value=.tran 0 100u 100n > tran.dat
}
C 40500 45200 1 0 0 gnucap-directive-1.sym
{
T 40600 45400 5 10 0 1 0 0 1
device=directive
T 40600 45500 5 10 1 1 0 0 1
refdes=A2
T 40600 45200 5 10 1 1 0 0 1
value=.print ac v(out)
}
C 40500 44500 1 0 0 gnucap-directive-1.sym
{
T 40600 44700 5 10 0 1 0 0 1
device=directive
T 40600 44800 5 10 1 1 0 0 1
refdes=A3
T 40600 44500 5 10 1 1 0 0 1
value=.ac 1k 10meg 10k decade 100 > ac.dat
}
N 41000 48200 41200 48200 4
{
T 42100 48200 5 10 1 0 0 0 1
netname=squ
}
N 41000 50200 41100 50200 4
{
T 42000 50200 5 10 1 0 0 0 1
netname=sin
}
N 44300 50200 44400 50200 4
{
T 43500 49900 5 10 1 0 0 0 1
netname=sin
}
N 45300 50200 45400 50200 4
{
T 46300 50200 5 10 1 0 0 0 1
netname=out
}
T 50100 40100 9 10 1 0 0 0 1
1
T 51600 40100 9 10 1 0 0 0 1
1
T 54000 40400 9 10 1 0 0 0 1
1
T 54000 40100 9 10 1 0 0 0 1
Arnaud Gardelein
T 50000 40400 9 10 1 0 0 0 1
demo.sch
T 51700 41000 9 10 1 0 0 0 1
Demonstration scheme for oscopy
