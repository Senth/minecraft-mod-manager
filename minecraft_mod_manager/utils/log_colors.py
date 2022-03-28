from colored import attr, fg


class LogColors:
    add = fg("green")
    updated = fg("green")
    remove = fg("red")
    error = fg("red")
    found = fg("cyan")
    command = fg("blue")
    skip = fg("yellow")
    not_found = fg("yellow")
    header = attr("bold")
    no_color = attr("reset")
