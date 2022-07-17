from solid import (difference, union,
                   translate, rotate,
                   cylinder, cube)
bearing_height = 7;
bearing_radius = 11;
tolerance = 0.4;

# FIXME this is redundant, pass as parameter
worm_length = 40;
worm_holder_length = 10;

def gear_belt(distance, radius, height, thickness, clearance):
  t = thickness;
  c = clearance;

  # set clearance on all variables
  d = distance + c;
  r = radius + c;
  h = height - 2 * c;

  depth = worm_length / 2 + worm_holder_length + 2 * clearance ;

  return(
      translate([0, 0, -height / 2 + clearance])(
          difference()(
              # Add thickness to make the case
              union()(
                  translate([-d - t, 0, 0])(
                      cylinder(r=r + t, h=h)
                  ),
                  translate([d + t, 0, 0])(
                      cylinder(r=r + t, h=h)
                  ),
                  translate([-d - t, -depth, 0])(
                      cube([2 * (d + t), 2 * depth, h])
                  ),
              ),
              # Now without thickness. +2 and -1 is for
              # extrapolating holes for better preview
              translate([-d, 0, -1])(
                  cylinder(r=r, h=h + 2)
              ),
              translate([d, 0, -1])(
                  cylinder(r=r, h=h + 2)
              ),
              translate([-d, -depth + t , -1])(
                  cube([2 * d, 2 * depth - 2 * t, h + 2])
              ),
          )
      )
  )

def bearing_holder(thickness):
    return (
        difference()(
            cylinder(r=bearing_radius + thickness + tolerance,
                     h=bearing_height + thickness + tolerance),

            cylinder(r=bearing_radius - thickness,
                     h=bearing_height + thickness + tolerance + 1),
            cylinder(r=bearing_radius,
                     h=bearing_height + tolerance),
        )
    )

def bearing_holders(radius, height, thickness, clearance):
    depth = worm_length / 2 + 3 * thickness + 3 * clearance
    return union()(
        translate([0, depth, 0])(
            rotate(-90, [1, 0, 0])(
                bearing_holder(thickness)
            )
        ),
        translate([0, -depth + thickness, 0])(
            rotate(-90, [1, 0, 0])(
                bearing_holder(thickness)
            )
        ),
    )


def chassi(gear_distance, gear_radius, gear_height, rod_diameter, thickness, clearance):
    c = clearance
    t = thickness

    return (
        difference()(
            union()(
                gear_belt(gear_distance, gear_radius, gear_height, thickness, clearance),
                bearing_holders(gear_radius, gear_height, thickness, clearance),
            ),
            translate([0, gear_radius + thickness + clearance + 1])(
                rotate(90, [1, 0, 0])(
                    cylinder(r=rod_diameter / 2 + clearance,
                             h=(gear_radius + thickness + clearance) * 2 + 2)
                )
            ),
        )
    )
