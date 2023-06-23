from matplotlib import pyplot as plt

from phdscripts.data import G_EQDSK

# Fitz 2018
# Taken from plotter script provided by Alexandre Fil


def plot_geqdsk(geqdsk: G_EQDSK) -> None:
    fig = plt.figure()

    x_label = "$\\bar\psi$"  # noqa: W605

    ax = fig.add_subplot(232)
    ax.plot(geqdsk["psi_n"], geqdsk["pressure"])
    ax.set_title("$\,$ p", fontsize=20)  # noqa: W605
    ax.ticklabel_format(style="sci", scilimits=(-1, 2), axis="y")
    plt.setp(ax.get_xticklabels(), visible=False)

    ax = fig.add_subplot(233, sharex=ax)
    ax.plot(geqdsk["psi_n"], geqdsk["q"])
    ax.set_title("$q$ ", fontsize=20)
    ax.ticklabel_format(style="sci", scilimits=(-1, 2), axis="y")
    plt.setp(ax.get_xticklabels(), visible=False)

    ax = fig.add_subplot(235, sharex=ax)
    ax.plot(geqdsk["psi_n"], geqdsk["pprime"])
    ax.set_title("$p\,^\\prime$ ", fontsize=20)  # noqa: W605
    ax.ticklabel_format(style="sci", scilimits=(-1, 2), axis="y")
    plt.xlabel(x_label, fontsize=20)

    ax = fig.add_subplot(236, sharex=ax)
    ax.plot(geqdsk["psi_n"], geqdsk["ffprime"])
    ax.set_title("$ff\,^\\prime$", fontsize=20)  # noqa: W605
    ax.ticklabel_format(style="sci", scilimits=(-1, 2), axis="y")
    plt.xlabel(x_label, fontsize=20)

    ax = fig.add_subplot(131, aspect="equal")
    ax.set_frame_on(False)
    ax.contour(
        geqdsk["grid_R"],
        geqdsk["grid_Z"],
        geqdsk["psi_grid"].transpose(),
        geqdsk["resolution"][0],
    )
    ax.plot(
        [x[0] for x in geqdsk["boundary"]], [x[1] for x in geqdsk["boundary"]], "-."
    )
    ax.plot(
        [x[0] for x in geqdsk["limiter_surface"]],
        [x[1] for x in geqdsk["limiter_surface"]],
    )
    plt.ylabel("Z", fontsize=20)
    plt.xlabel("R", fontsize=20)

    plt.show()
