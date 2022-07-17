#!/usr/bin/env python

from solid import (import_scad, scad_render_animated,
                   translate, rotate, difference, union,
                   square, circle, rotate_extrude,
                   cylinder)
from math import pi, ceil
from math_degree import sin, cos, asin

import pump, pitman, chassi

# Gear traction will be given by these
threads = 3;
central_teeth = 40;
pitman_radius = 50;
pitman_length = 400;
pump_distance = 120;

# Just a reasonable number, modul will be calculated to fit
peripheral_teeth = 60;

# Gearbox dimensions
modul = 3;
vertical_distance = 32;
worm_length = 40;
worm_holder_length = 10;
central_gear_height = 42;
central_gear_angle = 20;
peripheral_gear_height = 10;
pitman_distance = 20;
rod_diameter = 8;

# Gear traction angles
central_pressure_angle = 20;
central_helix_angle = 10;
peripheral_pressure_angle = 20;
peripheral_helix_angle = -30;

# Pump
pump_min_length = 205.5;

# Case
case_thickness = 3;

# Import dependencies
# https://www.thingiverse.com/thing:1604369
Getriebe = import_scad('Getriebe.scad')

# Setup other parameters

peripheral_gear_radius = modul * central_teeth / 2 + modul * threads / (2 * sin(central_helix_angle));

peripheral_modul = 2 * peripheral_gear_radius / peripheral_teeth;

d = peripheral_gear_radius;

def worm(modul, teeth, threads, central_pressure_angle, central_helix_angle, length, rotation):
    """The worm gear, connected to the helixes to drive the whole gear"""
    teeth_space = modul * pi / cos(central_helix_angle);
    parity_modifier = 1 if int(threads) % 2 else 0.5
    worm = (
        translate([0, (ceil(length / (2 * teeth_space)) - parity_modifier) * teeth_space, 0])(
            rotate([90, 180 / threads, 0])(
                rotate(rotation * teeth / threads, [0, 0, 1])(
                    Getriebe.schnecke(modul, threads, length, rod_diameter, central_pressure_angle, central_helix_angle),
                )
            )
        )
    )
    worm += (
        translate([0, length / 2 + 10 - 1, 0])(
            rotate(90, [1, 0, 0])(
                difference()(
                    cylinder(r=rod_diameter + case_thickness, h=worm_holder_length),
                    translate([0, 0, -1])(
                        cylinder(r=rod_diameter / 2, h=45)
                    ),
                )
            )
        )
    )
    return worm

def central_gear(modul, teeth, threads, height, central_helix_angle, worm_angle, rotation):
    """The central gear in each gear reel, driven by to the worm"""
    # Pitch cone radius
    radius_gear = modul * teeth / 2;
    radius_worm = modul * threads / (2 * sin(worm_angle));
    # base rotation of the gear
    gamma = -90 * height * sin(worm_angle) / (pi * radius_gear);
    return (
        translate([0, 0, -height / 2])(
            rotate([0, 0, gamma + rotation])(
                Getriebe.stirnrad(modul, teeth, height, 0, central_helix_angle, -worm_angle, False)
            )
        )
    )

def peripheral_gear(helix_angle):
    """Two peripheral gears will be connected on each side of the central gear,
    spinning in same angular speed of it, in a single piece shaped as a a reel.
    Each peripheral gear is connected to the peripheral gear of the opposite reel,
    driving and being driven by it, while driving a pitman arm."""

    return Getriebe.pfeilrad(
        modul=peripheral_modul,
        zahnzahl=peripheral_teeth,
        breite=peripheral_gear_height,
        bohrung=0,
        eingriffswinkel=peripheral_pressure_angle,
        schraegungswinkel=helix_angle,
        optimiert=False)


def half_reel():
    """This is the body that meshes the central gear to one peripheral gear"""
    gap = modul * (threads / (2 * sin(central_helix_angle)))
    width = peripheral_modul * peripheral_teeth / 2
    return (
        translate([0, 0, -vertical_distance])(
            rotate_extrude(angle=360, convexity=10)(
                difference()(
                    square([width, vertical_distance - central_gear_height / 2]),
                    translate([width, gap, 0])(
                        circle(gap)
                    ),
                )
            )
        )
    )


def gear_reel(central_angle, peripheral_angle, peripheral_teeth_angle):
    """A single piece, containing one central gear, two peripheral gears and two half reels.
    It's driven by the worm and drives two pitman arms, synchronized with the opposite reel.

    * central_angle: Z axis rotation of central gear, synchronized with worm depending on reel side
    * peripheral_angle: Z axis rotation of peripheral gears, synchronized with opposite peripheral gear
    * peripheral_teeth_angle: the angle of the teeth of peripheral gear, to fit into the opposite gear teeth
    """
    return (
        difference()(
            union()(
                central_gear(modul, central_teeth, threads, central_gear_height, central_gear_angle, central_helix_angle, central_angle),

                translate([0, 0, vertical_distance])(
                    rotate(peripheral_angle, [0, 0, 1])(
                        peripheral_gear(peripheral_teeth_angle)
                    )
                ),

                translate([0, 0, -vertical_distance - peripheral_gear_height])(
                    rotate(peripheral_angle, [0, 0, 1])(
                        peripheral_gear(-peripheral_teeth_angle)
                    )
                ),

                half_reel(),
                rotate(180, [0, 1, 0])(
                    half_reel(),
                ),
            ),

            translate([pitman_radius * cos(central_angle),
                       pitman_radius * sin(central_angle),
                       -vertical_distance - peripheral_gear_height - 20])(
                           cylinder(r=rod_diameter/2,
                                    h=2 * vertical_distance + 2 * peripheral_gear_height + 40)
                       ),
        )
    )


def engine(rotation):
    engine = union()(
        # The main driver, attached to the windmill helix, driving two gear reels
        worm(modul, central_teeth, threads, central_pressure_angle, central_helix_angle, worm_length, rotation),

        # The first gear reel
        translate([-d, 0, 0])(
            gear_reel(rotation,
                      rotation,
                      peripheral_helix_angle)
        ),

        # On second reel angles are inverted and shifted since it's on opposite side
        translate([d, 0, 0])(
            gear_reel(-rotation - 180 / central_teeth + 180,
                      -rotation - 180 / peripheral_teeth,
                      -peripheral_helix_angle)
        ),
    )

    # The pitman arms
    x = pitman_radius * cos(rotation)
    y = pitman_radius * sin(rotation)
    z = vertical_distance + peripheral_gear_height + pitman_distance
    pitman_angle = asin((d - x) / pitman_length)

    engine += union()(
        # Two rod passing through each gear reel to hold a pitman arm in each side
        translate([x - d, y, -z])(
            cylinder(r=rod_diameter/2, h=2 * vertical_distance + 2 * peripheral_gear_height + 2 * pitman_distance)
        ),

        translate([-x + d, y, -z])(
            cylinder(r=rod_diameter/2, h=2 * vertical_distance + 2 * peripheral_gear_height + 2 * pitman_distance)
        ),

        # Now the four pitman arms
        translate([x - d, y, z])(
            rotate([0, 0, pitman_angle])(
                pitman.pitman_arm(pitman_length)
            )
        ),
        translate([-x + d, y, z])(
            rotate([0, 0, -pitman_angle])(
                pitman.pitman_arm(pitman_length)
            )
        ),
        translate([x - d, y, -z])(
            rotate([0, 0, pitman_angle])(
                pitman.pitman_arm(pitman_length)
            )
        ),
        translate([-x + d, y, -z])(
            rotate([0, 0, -pitman_angle])(
                pitman.pitman_arm(pitman_length)
            )
        ),
    )

    # Adjust y to match the end of all pitman arms
    y -= pitman_length * cos(pitman_angle)
    pump_course = -y - pump_min_length - pump_distance;

    engine += union()(
        # The pump handle holder, connecting all pitman arms
        translate([0, y, -z])(
            cylinder(r=rod_diameter / 2, h=2 * z)
        ),

        # The pump
        translate([0, -pump_distance, 0])(
            rotate(90, [1, 0, 0])(
                pump.pump(pump_course)
            )
        ),
    )

    return engine

def windmill(_time=0):
    rotation = _time * 360
    return union()(
        engine(rotation),
        chassi.chassi(
            gear_distance = d,
            gear_radius = central_teeth * modul / 2,
            gear_height = central_gear_height,
            rod_diameter = rod_diameter,
            thickness = case_thickness,
            clearance = modul / 2
        ),
    )

scad_code = scad_render_animated(
    windmill,
    steps=360,
    back_and_forth=False,
)

open('windmill.scad', 'w').write(scad_code)
