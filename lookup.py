import numpy as np
import pandas as pd
from constants import CHANGES, CHUNKSIZE, LANES, PEOPLE


sample_column_names = [
    "chromosome",
    "position",
    "change",
    "num changes",
    "num consensus molecules",
    "sample ID",
]


id_df = pd.read_csv(
    "data_files\\id.txt",
    header=None,
    names=["lane1", "lane2", "lane3", "lane4", "ID"],
    index_col=-1,
)

seq_df = pd.read_csv(
    "data_files\\illumina_80Genes_panel.bed",
    header=None,
    names=["chromosome", "start", "end", "who tf knows", "length", "strand"],
    sep="\t",
)
seq_df.sort_values(
    "chromosome", inplace=True, kind="mergesort", ignore_index=True
)  # use mergesort for stability
seq_df.to_csv("spam.csv")


def separating_sequences(sequence_numbers):
    reduced_seq_df = seq_df.loc[sequence_numbers]
    seq_dfs = []
    for i in range(len(sequence_numbers)):
        seq_dfs.append(pd.DataFrame(columns=sample_column_names))

    for j, chunk in enumerate(
        pd.read_csv(
            "data_files\\full_data.txt",
            chunksize=CHUNKSIZE,
            header=None,
            names=sample_column_names,
            sep="\t",
        )
    ):
        print("chunk {}".format(j))
        for i, sequence in reduced_seq_df.iterrows():
            # print("sequence {}".format(i))

            seq_dfs[i] = seq_dfs[i].append(
                chunk.loc[
                    (chunk["position"] >= sequence["start"])
                    & (chunk["position"] <= sequence["end"])
                ],
                ignore_index=True,
            )

    for i, df in zip(sequence_numbers, seq_dfs):
        df.to_csv("data_files\\sequences\\seq_{}.csv".format(i))


def big_df():
    df = pd.DataFrame(columns=sample_column_names)
    df = pd.read_csv(
        "data_files\\full_data.txt", header=None, names=sample_column_names, sep="\t",
    )
    return df


def downsample_df():
    rng = np.random.default_rng()
    df = big_df()
    N_0 = np.percentile(df["num consensus molecules"], 0.1)
    print("N_0 = {}".format(N_0))

    df = df[df["num consensus molecules"] >= N_0]
    df["num changes"] = rng.binomial(
        n=N_0, p=df["num changes"] / df["num consensus molecules"]
    )
    df.drop(labels="num consensus molecules", axis=1)
    df.to_csv("data_files\\downsample.txt")
    return df


def lookup(
    chromosome, positions, change=CHANGES, people=PEOPLE, lanes=LANES, downsample=False
):
    """
    Looks up a given people, ages (given by lanes) and transitions (e.g. AC).
    "lane1" = age0, "lane2" = age7, "lane3" = age17, "lane4" = age24
    """
    sample_ids = np.zeros(
        people.size * lanes.size, dtype="U14"
    )  # string length 14, keep an eye on this

    for j in range(people.size):
        for i in range(lanes.size):
            sample_ids[j * lanes.size + i] = id_df.at[people[j], lanes[i]][:14]

    if downsample:
        df = downsample_df()
    else:
        df = big_df()

    df = df.loc[
        np.isin(df["sample ID"], sample_ids)
        & np.isin(df["position"], positions)
        & (df["chromosome"] == chromosome)
        & np.isin(df["change"], change)
    ]
    return df


def figuring_out_the_data():
    seq_df = pd.DataFrame(columns=["chromosome", "start", "end", "length"])
    start_position = 0
    current_position = 0
    current_chr = ""
    counter = 0
    df = pd.read_csv(
        "data_files\\full_data.txt", header=None, names=sample_column_names, sep="\t",
    )
    start_position = df.at[0, "position"]
    current_position = start_position
    current_chr = df.at[0, "chromosome"]
    for i in np.arange(len(df.index)):
        chromosome = df.at[i, "chromosome"]
        position = df.at[i, "position"]
        if chromosome != current_chr or (
            position != current_position and position != (current_position + 1)
        ):
            print("{}: {} to {}".format(current_chr, start_position, current_position))
            seq_df.append(
                {
                    "chromosome": current_chr,
                    "start": start_position,
                    "end": current_position,
                    "length": current_position - start_position + 1,
                },
                ignore_index=True,
            )

            current_chr = chromosome
            start_position = position
            current_position = start_position
        elif position == current_position + 1:
            current_position += 1
    print("{};{};{}".format(current_chr, start_position, current_position))
    seq_df.append(
        {
            "chromosome": current_chr,
            "start": start_position,
            "end": current_position,
            "length": current_position - start_position + 1,
        },
        ignore_index=True,
    )
    seq_df.to_csv("data_files\\sequences2.txt")
    return


separating_sequences(np.arange(0, 100))
