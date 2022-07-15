
body_diameter = 24.5;
body_length = 124;

end_diameter = 29.5;
end_length = 9.5;

tip_diameter = 16;
tip_length = 9;

pump_length = 121;
pump_diameter = 10;

handle_length = 53.5;
handle_diameter = 15;
handle_width = 53.5;

max_course = 121;

module pump(course=0) {
  course = max(course, 0);
  course = min(course, max_course);

  // body
  translate([0, 0, end_length])
  cylinder(r=body_diameter / 2,
           h=body_length);
  cylinder(r=end_diameter / 2,
           h=end_length);
  translate([0, 0, body_length + end_length])
    cylinder(r=end_diameter / 2,
             h=end_length);

  // tip
  translate([0, 0, -tip_length])
    cylinder(r=tip_diameter / 2,
             h=tip_length);

  // pump rod
  translate([0, 0, body_length + 2 * end_length])
    cylinder(r=pump_diameter / 2,
             h=course);

  // handle
  translate([0, 0, body_length + 2 * end_length + course])
    handle();
}

module handle() {
  cylinder(r=handle_diameter / 2,
           h=handle_length);
  translate([0, handle_width / 2, handle_length])
    rotate(90, [1, 0, 0])
    cylinder(r=handle_diameter / 2,
             h=handle_length);
}
