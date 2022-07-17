from solid import (import_scad,
                   translate, rotate,
                   union, difference,
                   cube, cylinder)

ISOThread = import_scad('ISOThread.scad')

def bolt_with_nut():
    ISOThread.hex_nut(3);
    return union()(
        cylinder(r=1.7, h=13),
        translate([0, 0, 9.5])(
            cylinder(r=3.7, h=.5),
        ),
        translate([0, 0, 10])(
            cylinder(r=3, h=3)
        ),
    )

def rotated_bolt_with_nut():
    return (
        translate([0, 0, 13])(
            rotate(180, [1, 0, 0])(
                bolt_with_nut()
            )
        )
    )

def half_pitman_arm(l):
    return (
        rotate(180, [0, 0, 1])(
            difference()(
                union()(
                    cylinder(h=6.5, r=13),
                    translate([-10, 0, 0])(
                        cube([20, l, 6.5])
                    ),
                    translate([0, l, 0])(
                        cylinder(h=6.5, r=13)
                    )
                ),
                translate([0, 0, 3])(
                    cylinder(r=11, h=17)
                ),
                translate([0, l, 3])(
                    cylinder(r=11, h=7)
                ),
                cylinder(h=7, r=6),
                translate([0, l, 0])(
                    cylinder(h=7, r=6)
                ),
            )
        )
    )

def pitman_left(l):
    return (
        difference()(
            half_pitman_arm(l),
            translate([0, -20, 0])(
                bolt_with_nut()
            ),
            translate([0, -l / 2, 0])(
                rotated_bolt_with_nut()
            ),
            translate([0, -l + 20, 0])(
                bolt_with_nut()
            ),
        )
    )

def pitman_right(l):
    return (
        translate([0, 0, 13])(
            rotate(180, [0, 1, 0])(
                difference()(
                    half_pitman_arm(l),
                    translate([0, -20, 0])(
                        rotated_bolt_with_nut()
                    ),
                    translate([0, -l / 2, 0])(
                        bolt_with_nut()
                    ),
                    translate([0, -l + 20, 0])(
                        rotated_bolt_with_nut()
                    ),
                )
            )
        )
    )

def pitman_arm(l):
    return pitman_left(l) + pitman_right(l)
