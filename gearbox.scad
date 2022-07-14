use <Getriebe.scad>;

rotation = $t * 360 ;

// Gear traction will be given by central_teeth / threads
threads = 3;
central_teeth = 40;

// Just a reasonable number, git will be calculated
peripheral_teeth = 60;

// Gearbox dimensions
modul = 2;
vertical_distance = 24;
worm_length = 32;
central_gear_height = 20;
central_gear_angle = 20;
peripheral_gear_height = 10;
rod_diameter = 8;


// Gear traction angles
central_pressure_angle = 20;
central_helix_angle = 10;
peripheral_pressure_angle = 20;
peripheral_helix_angle = -30;

pitman_radius = 50;

pi = 3.14159;

peripheral_gear_radius = modul * central_teeth / 2 + modul * threads / (2 * sin(central_helix_angle));

//d == peripheral_teeth * modul / 2;
peripheral_modul = 2 * peripheral_gear_radius / peripheral_teeth;

d = peripheral_gear_radius;

module worm(modul, teeth, threads, central_pressure_angle, central_helix_angle, length, rotation) {
  teeth_space = modul * pi / cos(central_helix_angle);
  parity_modifier = threads == floor(threads / 2) * 2 ? 0.5 : 1;
  translate([0, (ceil(length / (2 * teeth_space)) - parity_modifier) * teeth_space, 0])
  rotate([90, 180 / threads, 0])
    rotate(rotation * teeth / threads, [0, 0, 1])
    schnecke(modul, threads, length, rod_diameter, central_pressure_angle, central_helix_angle);
}

module central_gear(modul, teeth, threads, height, central_helix_angle, worm_angle, rotation) {
  // Pitch cone radius
  radius_gear = modul * teeth / 2;
  radius_worm = modul * threads / (2 * sin(worm_angle));
  // base rotation of the gear
  gamma = -90 * height * sin(worm_angle) / (pi * radius_gear);
  translate([0, 0, -height / 2])
    rotate([0, 0, gamma + rotation])
    stirnrad(modul, teeth, height, radius_gear * 2, central_helix_angle, -worm_angle, false);
}

module peripheral_gear(helix_angle) {
  pfeilrad(modul=peripheral_modul,
           zahnzahl=peripheral_teeth,
           breite=peripheral_gear_height,
           bohrung=8,
           eingriffswinkel=peripheral_pressure_angle,
           schraegungswinkel=helix_angle,
           optimiert=false);
}

module triple_gear(central_angle, peripheral_angle, helix_angle) {
  central_gear(modul, central_teeth, threads, central_gear_height, central_gear_angle, central_helix_angle, central_angle);
  translate([0, 0, vertical_distance])
    rotate(peripheral_angle, [0, 0, 1])
    peripheral_gear(helix_angle);
  translate([0, 0, -vertical_distance - peripheral_gear_height])
    rotate(peripheral_angle, [0, 0, 1])
    peripheral_gear(-helix_angle);
}

module gearbox() {
  worm(modul, central_teeth, threads, central_pressure_angle, central_helix_angle, worm_length, rotation);

  translate([-d, 0, 0])
    triple_gear(rotation,
                rotation,
                peripheral_helix_angle);

  translate([d, 0, 0])
    triple_gear(- rotation - 180 / central_teeth,
                -rotation - 180 / peripheral_teeth,
                -peripheral_helix_angle);
}

gearbox();