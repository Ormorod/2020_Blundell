import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from lookup import chromosome_tiles_map, exon_tiles_map, tile_df, tile_data_df
from constants import VARIANTS
from scipy.stats import betabinom, poisson
from scipy.optimize import curve_fit
from collections.abc import Iterable


def mean_var(tile_numbers, variant, trim_and_flip):
    """
    Returns  of mean and var for a given tile and variant.
    """
    df = pd.DataFrame()
    if not isinstance(tile_numbers, Iterable):
        tile_numbers = [tile_numbers]
    for tile_number in tile_numbers:
        df = df.append(tile_data_df(tile_number, trim_and_flip=trim_and_flip))

    if True == df.empty:
        return 0, 0
    df = df.loc[df["variant"] == variant]

    mean = np.mean(df["downsample"])
    variance = np.var(df["downsample"])
    return mean, variance


def plot_all_mean_var(
    show_strands=True, save=True, trim_and_flip=True, group_chromosomes=False
):
    """
    Plots the mean, variance and the index of dispersion for all tiles.
    """
    for variant in VARIANTS:
        print(variant)
        fig, ax = plt.subplots(3, figsize=(8, 8))

        for j, chromosome in enumerate(pd.unique(tile_df["chromosome"])):
            chr_tile_df = tile_df.loc[
                (tile_df["chromosome"] == chromosome) & (tile_df["strand"] == "+")
            ]
            if group_chromosomes:
                means, variances = mean_var(chr_tile_df.index, variant, trim_and_flip)
                xs = j
            else:
                means = np.zeros(len(chr_tile_df.index))
                variances = np.zeros(len(chr_tile_df.index))
                for i, index in enumerate(chr_tile_df.index):
                    print(i)
                    means[i], variances[i] = mean_var(index, variant, trim_and_flip)
                xs = chr_tile_df.index  # janky trick to get x axis to work
            if show_strands:
                marker = "$+$"
            else:
                marker = "${}$".format(chromosome)

            ax[0].plot(
                xs, means, label="means", marker=marker, linestyle="None",
            )

            ax[1].plot(
                xs, variances, label="variances", marker=marker, linestyle="None",
            )
            if means != 0:
                ax[2].plot(
                    xs,
                    variances / means,
                    label="index of dispersion",
                    marker=marker,
                    linestyle="None",
                )
        for j, chromosome in enumerate(pd.unique(tile_df["chromosome"])):
            chr_tile_df = tile_df.loc[
                (tile_df["chromosome"] == chromosome) & (tile_df["strand"] == "-")
            ]
            if group_chromosomes:
                means, variances = mean_var(chr_tile_df.index, variant, trim_and_flip)
                xs = j
            else:
                means = np.zeros(len(chr_tile_df.index))
                variances = np.zeros(len(chr_tile_df.index))
                for i, index in enumerate(chr_tile_df.index):
                    print(i)
                    means[i], variances[i] = mean_var(index, variant, trim_and_flip)
                xs = chr_tile_df.index  # janky trick to get x axis to work
            if show_strands:
                marker = "$-$"
            else:
                marker = "${}$".format(chromosome)

            ax[0].plot(
                xs, means, label="means", marker=marker, linestyle="None",
            )

            ax[1].plot(
                xs, variances, label="variances", marker=marker, linestyle="None",
            )
            if means != 0:
                ax[2].plot(
                    xs,
                    variances / means,
                    label="means",
                    marker=marker,
                    linestyle="None",
                )
        ax[0].set(
            title="{} means".format(variant), xlabel="tile", ylabel="mean", yscale="log"
        )
        ax[1].set(title="variances", xlabel="tile", ylabel="variance", yscale="log")
        ax[2].set(
            title="Index of dispersion",
            xlabel="tile",
            ylabel="D = Var/mean",
            yscale="log",
        )
        fig.tight_layout()
        if save:
            file_name = "plots\\means_and_variances\\{}_mean_var".format(variant)
            if show_strands:
                file_name += "_strands"
            if trim_and_flip:
                file_name += "_t&f"
            if group_chromosomes:
                file_name += "_group_chromosomes"
            fig.savefig(file_name + ".png")
            fig.savefig(file_name + ".svg", dpi=1200)
        else:
            plt.show()
        plt.close("all")


def plot_all_mean_var_chromosomes(show_strands=True, save=True, trim_and_flip=True):
    """
    Plots the mean, variance and the index of dispersion for all tiles.
    """
    for variant in VARIANTS:
        print(variant)
        fig, ax = plt.subplots(3, figsize=(8, 8))

        for chromosome in pd.unique(tile_df["chromosome"]):
            chr_tile_df = tile_df.loc[
                (tile_df["chromosome"] == chromosome) & (tile_df["strand"] == "+")
            ]
            means = np.zeros(len(chr_tile_df.index))
            variances = np.zeros(len(chr_tile_df.index))
            for i, index in enumerate(chr_tile_df.index):
                print(i)
                means[i], variances[i] = mean_var(index, variant, trim_and_flip)

            if show_strands:
                marker = "$+$"
            else:
                marker = "${}$".format(chromosome)

            ax[0].plot(
                chr_tile_df.index,
                means,
                label="means",
                marker=marker,
                linestyle="None",
            )

            ax[1].plot(
                chr_tile_df.index,
                variances,
                label="variances",
                marker=marker,
                linestyle="None",
            )

            ax[2].plot(
                chr_tile_df.index,
                variances / means,
                label="index of dispersion",
                marker=marker,
                linestyle="None",
            )
        for chromosome in pd.unique(tile_df["chromosome"]):
            chr_tile_df = tile_df.loc[
                (tile_df["chromosome"] == chromosome) & (tile_df["strand"] == "-")
            ]
            means = np.zeros(len(chr_tile_df.index))
            variances = np.zeros(len(chr_tile_df.index))
            for i, index in enumerate(chr_tile_df.index):
                print(i)
                means[i], variances[i] = mean_var(index, variant, trim_and_flip)

            if show_strands:
                marker = "$-$"
            else:
                marker = "${}$".format(chromosome)

            ax[0].plot(
                chr_tile_df.index,
                means,
                label="means",
                marker=marker,
                linestyle="None",
            )

            ax[1].plot(
                chr_tile_df.index,
                variances,
                label="variances",
                marker=marker,
                linestyle="None",
            )

            ax[2].plot(
                chr_tile_df.index,
                variances / means,
                label="means",
                marker=marker,
                linestyle="None",
            )
        ax[0].set(
            title="{} means".format(variant), xlabel="tile", ylabel="mean", yscale="log"
        )
        ax[1].set(title="variances", xlabel="tile", ylabel="variance", yscale="log")
        ax[2].set(
            title="Index of dispersion",
            xlabel="tile",
            ylabel="D = Var/mean",
            yscale="log",
        )
        fig.tight_layout()
        if save:
            file_name = "plots\\means_and_variances\\{}_mean_var".format(variant)
            if show_strands:
                file_name += "_strands"
            if trim_and_flip:
                file_name += "_t&f"
            fig.savefig(file_name + ".png")
            fig.savefig(file_name + ".svg", dpi=1200)
        else:
            plt.show()
        plt.close("all")


def plot_exon_mean_var(exon_number, save=True, trim_and_flip=True):
    df = exon_tiles_map[exon_number]
    means = np.zeros(len(df.index))
    variances = np.zeros(len(df.index))

    for variant in VARIANTS:
        print(variant)
        fig, ax = plt.subplots(3, figsize=(8, 8))
        for i in df.index:
            print(i)
            means[i], variances[i] = mean_var(i, variant, trim_and_flip)
        ax[0].plot(df.index, means, label="means", marker="+", linestyle="None")
        ax[0].set(title="means", xlabel="tile", ylabel="mean", yscale="log")

        ax[1].plot(df.index, variances, label="variances", marker="+", linestyle="None")
        ax[1].set(title="variances", xlabel="tile", ylabel="variance", yscale="log")

        ax[2].plot(
            df.index, variances / means, label="means", marker="+", linestyle="None"
        )
        ax[2].set(title="ratios", xlabel="tile", ylabel="ratios", yscale="log")
        fig.tight_layout()
        if save:
            fig.savefig("plots\\means_and_variances\\{}_mean_var.png".format(variant))
        else:
            plt.show()
        plt.close("all")


def plot_chromosome_variant_hist(
    chromosome, fit=None, save=True, strand=None, bins_to_fit=-1
):
    """
    Plots a histogram of the number of downsampled variants for a given tile

    fit = None/"Poisson"/"Beta-binomial"

    strand = None/"+"/"-"
    """
    tile_numbers = chromosome_tiles_map[str(chromosome)].index
    df = pd.DataFrame()
    for tile_number in tile_numbers:
        if strand is None or tile_df.at[tile_number, "strand"] == strand:
            df = df.append(tile_data_df(tile_number))
            print(tile_number)

    for variant in VARIANTS:
        print(variant)
        fig, ax = plt.subplots()
        change_df = df.loc[variant == df["variant"]]
        mean = np.mean(change_df["downsample"])
        variance = np.var(change_df["downsample"])
        D = variance / mean  # index of dispersion
        print("mean: {}, variance: {}, variance/mean: {}".format(mean, variance, D))
        n = 6348  # 50th percentile of smaller data file
        N = len(change_df.index)  # To adjust normalisation of distributions

        maximum = np.amax(change_df["downsample"])
        print(maximum)

        bins = np.arange(-0.5, maximum + 1.5)
        xs = np.arange(maximum + 1)

        hs, hs_bin_edges = np.histogram(change_df["downsample"], bins)
        print(hs)

        ax.hist(
            change_df["downsample"], bins=bins, color="c", linestyle="-", edgecolor="k",
        )

        if fit == "Poisson":
            ys = poisson.pmf(xs, mean) * N
            ax.plot(xs, ys, color="k", marker="+")

        if fit == "Beta-binomial":

            def b(a):
                return a * (n / mean - 1.0)

            def f(x, a):
                return N * betabinom.pmf(x, n, a, b(a))

            a, pcov = curve_fit(f, xs[:bins_to_fit], hs[bins_to_fit])
            fit_mean = betabinom.mean(n, a, b(a))
            print("fit mean: {}".format(fit_mean))
            fit_var = betabinom.var(n, a, b(a))
            print("fit variance: {}".format(fit_var))

            ax.plot(xs, f(xs, a), color="k", marker="+")

        plot_title = variant
        if strand is not None:
            plot_title += " " + strand
        ax.set(
            title=plot_title,
            xlabel="number of variants",
            ylabel="frequency",
            yscale="log",
        )
        ax.text(0.8, 0.9, "D = {:.2f}".format(D), transform=ax.transAxes)
        if save:
            file_name = "plots\\variant_histograms\\variant_hist_chr{}_{}".format(
                chromosome, variant
            )
            if fit is not None:
                file_name += "_" + fit
            if strand is not None:
                file_name += "_" + strand
            fig.savefig(file_name + ".png")
            fig.savefig(file_name + ".svg", dpi=1200)
        else:
            plt.show()
