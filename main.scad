use <Getriebe.scad>
use <./pump.scad>
use <./pitman.scad>
use <./chassi.scad>

rotation = $t * 360 ;

// Gear traction will be given by these
threads = 3;
central_teeth = 40;
pitman_radius = 50;
pitman_length = 400;
pump_distance = 120;

// Just a reasonable number, it will be calculated
peripheral_teeth = 60;

// Gearbox dimensions
modul = 3;
vertical_distance = 32;
worm_length = 40;
worm_holder_length = 10;
central_gear_height = 42;
central_gear_angle = 20;
peripheral_gear_height = 10;
pitman_distance = 20;
rod_diameter = 8;

// Gear traction angles
central_pressure_angle = 20;
central_helix_angle = 10;
peripheral_pressure_angle = 20;
peripheral_helix_angle = -30;

// Pump
pump_min_length = 205.5;

// Case
case_thickness = 3;

pi = 3.14159;

peripheral_gear_radius = modul * central_teeth / 2 + modul * threads / (2 * sin(central_helix_angle));

peripheral_modul = 2 * peripheral_gear_radius / peripheral_teeth;

d = peripheral_gear_radius;

module worm(modul, teeth, threads, central_pressure_angle, central_helix_angle, length, rotation) {
  teeth_space = modul * pi / cos(central_helix_angle);
  parity_modifier = threads == floor(threads / 2) * 2 ? 0.5 : 1;
  translate([0, (ceil(length / (2 * teeth_space)) - parity_modifier) * teeth_space, 0])
  rotate([90, 180 / threads, 0])
    rotate(rotation * teeth / threads, [0, 0, 1])
    schnecke(modul, threads, length, rod_diameter, central_pressure_angle, central_helix_angle);
  translate([0, length / 2 + 10 - 1, 0])
  rotate(90, [1, 0, 0])
    difference() {
    cylinder(r=rod_diameter + case_thickness, h=worm_holder_length);
    translate([0, 0, -1])
      cylinder(r=rod_diameter / 2, h=45);
  }
}

module central_gear(modul, teeth, threads, height, central_helix_angle, worm_angle, rotation) {
  // Pitch cone radius
  radius_gear = modul * teeth / 2;
  radius_worm = modul * threads / (2 * sin(worm_angle));
  // base rotation of the gear
  gamma = -90 * height * sin(worm_angle) / (pi * radius_gear);
  translate([0, 0, -height / 2])
    rotate([0, 0, gamma + rotation])
    stirnrad(modul, teeth, height, 0, central_helix_angle, -worm_angle, false);
}

module peripheral_gear(helix_angle) {
  pfeilrad(modul=peripheral_modul,
           zahnzahl=peripheral_teeth,
           breite=peripheral_gear_height,
           bohrung=0,
           eingriffswinkel=peripheral_pressure_angle,
           schraegungswinkel=helix_angle,
           optimiert=false);
}

module half_reel() {
  gap = modul * (threads / (2 * sin(central_helix_angle)));
  width = peripheral_modul * peripheral_teeth / 2;
  translate([0, 0, -vertical_distance])
    rotate_extrude(angle=360, convexity=10)
    difference() {
    square([width, vertical_distance - central_gear_height / 2]);
    translate([width, gap, 0])
      circle(gap);
  }
}

module gear_reel(central_angle, peripheral_angle, helix_angle) {
  difference() {
    union() {
      central_gear(modul, central_teeth, threads, central_gear_height, central_gear_angle, central_helix_angle, central_angle);

      translate([0, 0, vertical_distance])
        rotate(peripheral_angle, [0, 0, 1])
        peripheral_gear(helix_angle);

      translate([0, 0, -vertical_distance - peripheral_gear_height])
        rotate(peripheral_angle, [0, 0, 1])
        peripheral_gear(-helix_angle);

      half_reel();
      rotate(180, [0, 1, 0])
        half_reel();
    }
    translate([pitman_radius * cos(central_angle),
               pitman_radius * sin(central_angle),
               -vertical_distance - peripheral_gear_height - 20])
      cylinder(r=rod_diameter/2, h=2 * vertical_distance + 2 * peripheral_gear_height + 40);

  }
}

module engine() {
  // The central driver, attached to the windmill helix
  worm(modul, central_teeth, threads, central_pressure_angle, central_helix_angle, worm_length, rotation);

  // The first gear reel, with three gears
  translate([-d, 0, 0])
    gear_reel(rotation,
              rotation,
              peripheral_helix_angle);

  rotation_b = -rotation - 180 / central_teeth + 180;

  // Second gear reel, on opposite side of worm
  translate([d, 0, 0])
    gear_reel(rotation_b,
              -rotation - 180 / peripheral_teeth,
              -peripheral_helix_angle);


  // The two rods that holding pitman arms
  translate([pitman_radius * cos(rotation) - d,
             pitman_radius * sin(rotation),
             -vertical_distance - peripheral_gear_height - pitman_distance])
    cylinder(r=rod_diameter/2, h=2 * vertical_distance + 2 * peripheral_gear_height + 2 * pitman_distance);

  translate([pitman_radius * cos(rotation_b) + d,
             pitman_radius * sin(rotation_b),
             -vertical_distance - peripheral_gear_height - pitman_distance])
    cylinder(r=rod_diameter/2, h=2 * vertical_distance + 2 * peripheral_gear_height + 2 * pitman_distance);

  // The pitman arms
  x = pitman_radius * cos(rotation);
  y = pitman_radius * sin(rotation);
  z = vertical_distance + peripheral_gear_height + pitman_distance;

  pitman_angle = asin((d - x) / pitman_length);

  translate([x - d, y, z])
    rotate([0, 0, pitman_angle])
    pitman_arm(pitman_length);
  translate([-x + d, y, z])
    rotate([0, 0, -pitman_angle])
    pitman_arm(pitman_length);

  translate([x - d, y, -z])
    rotate([0, 0, pitman_angle])
    pitman_arm(pitman_length);
  translate([-x + d, y, -z])
    rotate([0, 0, -pitman_angle])
    pitman_arm(pitman_length);

  // The pump handle holder
  translate([0,
             y - pitman_length * cos(pitman_angle),
             -z])
  cylinder(r=rod_diameter / 2,
           h=2 * z);

  // The pump
  pump_course = -y + pitman_length * cos(pitman_angle) - pump_min_length - pump_distance;

  translate([0,
             -pump_distance,
             0])
  rotate(90, [1, 0, 0])
    pump(pump_course);
}


module windmill() {
  engine();
  chassi(
         gear_distance = d,
         gear_radius = central_teeth * modul / 2,
         gear_height = central_gear_height,
         rod_diameter = rod_diameter,
         thickness = case_thickness,
         clearance = modul / 2
         );
}

windmill();
