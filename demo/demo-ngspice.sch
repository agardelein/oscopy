v 20091004 2
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
value=AC
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
value=dc 0 pulse -1 1 1n 1n 1n 200n 400n
}
C 40900 48700 1 0 0 gnd-1.sym
C 40900 46700 1 0 0 gnd-1.sym
C 41000 50100 1 0 0 output-1.sym
{
T 41100 50400 5 10 0 0 0 0 1
device=OUTPUT
T 41200 50400 5 10 1 0 0 0 1
net=sin:1
}
C 41000 48100 1 0 0 output-1.sym
{
T 41100 48400 5 10 0 0 0 0 1
device=OUTPUT
T 41000 48400 5 10 1 0 0 0 1
net=squ:1
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
value=10n
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
C 43600 50100 1 0 0 input-1.sym
{
T 43600 50400 5 10 0 0 0 0 1
device=INPUT
T 43600 50400 5 10 1 0 0 0 1
net=sin:1
}
C 45400 50100 1 0 0 output-1.sym
{
T 45500 50400 5 10 0 0 0 0 1
device=OUTPUT
T 46200 50100 5 10 0 0 0 0 1
netname=out
}
C 40500 44500 1 0 0 gnucap-directive-1.sym
{
T 40600 44700 5 10 0 1 0 0 1
device=directive
T 40600 44800 5 10 1 1 0 0 1
refdes=A3
T 40600 44500 5 10 1 1 0 0 1
value=.ac dec 100 1k 10meg > ac.dat
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
C 53800 42500 1 0 0 vdc-1.sym
{
T 54500 43150 5 10 1 1 0 0 1
refdes=V4
T 54500 42950 5 10 1 1 0 0 1
value=50
}
C 50000 42500 1 0 0 vpulse-1.sym
{
T 50700 43150 5 10 1 1 0 0 1
refdes=V3
T 50700 42950 5 10 1 1 0 0 1
value=dc 0 pulse 0 10 10n 10n 10n 1u 10u
}
C 53900 43700 1 0 0 12V-plus-1.sym
C 50200 42200 1 0 0 gnd-1.sym
C 54000 42200 1 0 0 gnd-1.sym
C 50300 43600 1 0 0 output-2.sym
{
T 50500 43900 5 10 1 0 0 0 1
net=gs:1
}
C 53200 46400 1 0 0 12V-plus-1.sym
C 53300 44200 1 0 0 gnd-1.sym
C 53500 45500 1 90 0 resistor-2.sym
{
T 53150 45900 5 10 0 0 90 0 1
device=RESISTOR
T 52900 46200 5 10 1 1 0 0 1
refdes=RD
T 52900 46000 5 10 1 1 0 0 1
value=2.9
}
C 50600 44600 1 0 0 input-2.sym
{
T 51200 44900 5 10 1 0 0 0 1
net=gs:1
}
N 53400 45500 53400 45300 4
{
T 53500 45400 5 10 1 1 0 0 1
netname=ds
}
C 52900 44500 1 0 0 nmos-3.sym
{
T 53500 45000 5 10 0 0 0 0 1
device=IC
T 53600 45100 5 10 1 1 0 0 1
refdes=X1
T 53600 44900 5 10 1 1 0 0 1
value=irf540n
T 53600 44700 5 10 1 0 0 0 1
model-name=irf540n
T 52900 44500 5 10 1 0 0 0 1
file=irf540n.sub
}
C 52000 44600 1 0 0 resistor-2.sym
{
T 52400 44950 5 10 0 0 0 0 1
device=RESISTOR
T 52200 44900 5 10 1 1 0 0 1
refdes=RG
T 52200 44400 5 10 1 1 0 0 1
value=9.1
}
C 52000 49100 1 0 0 spice-include-1.sym
{
T 52100 49400 5 10 0 1 0 0 1
device=include
T 52100 49500 5 10 1 1 0 0 1
refdes=A10
T 52300 48900 5 10 1 0 0 0 1
file=irf540n.sub
T 52200 48600 5 10 1 0 0 0 1
value=irf540n.sub
}
