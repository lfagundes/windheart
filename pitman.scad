use <ISOThread.scad>


module bolt_with_nut() {
  hex_nut(3);
  cylinder(r=1.7, h=13);
  translate([0, 0, 9.5])
    cylinder(r=3.7, h=.5);
  translate([0, 0, 10])
    cylinder(r=3, h=3);

}

module rotated_bolt_with_nut() {
  translate([0, 0, 13])
    rotate(180, [1, 0, 0])
    bolt_with_nut();
}

module half_pitman_arm(l) {
  rotate(180, [0, 0, 1])
    difference() {
    union() {
      cylinder(h=6.5, r=13);
      translate([-10, 0, 0])
        cube([20, l, 6.5]);
      translate([0, l, 0])
        cylinder(h=6.5, r=13);
    }
    translate([0, 0, 3])
      cylinder(r=11, h=17);
    translate([0, l, 3])
      cylinder(r=11, h=7);
    cylinder(h=7, r=6);
    translate([0, l, 0])
      cylinder(h=7, r=6);
  }
}

module pitman_left(l) {
  difference() {
    half_pitman_arm(l);
    translate([0, -20, 0])
      bolt_with_nut();
    translate([0, -l / 2, 0])
      rotated_bolt_with_nut();
    translate([0, -l + 20, 0])
      bolt_with_nut();
  }
}

module pitman_right(l) {
  translate([0, 0, 13])
  rotate(180, [0, 1, 0])
  difference() {
    half_pitman_arm(l);
    translate([0, -20, 0])
      rotated_bolt_with_nut();
    translate([0, -l / 2, 0])
      bolt_with_nut();
    translate([0, -l + 20, 0])
      rotated_bolt_with_nut();
  }
}

module pitman_arm(l) {
  pitman_left(l);
  pitman_right(l);
}
