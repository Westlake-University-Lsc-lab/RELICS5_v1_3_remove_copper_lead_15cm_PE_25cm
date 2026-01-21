###############################################################
## Sorting the raw G4 output to clustered energy depositions
## based on XYZT
################################################################

import argparse

import h5py
import numpy as np
from dtypes import (
    cluster_dtype,
    energy_dtype,
    event_dtype,
    primary_dtype,
    set_nan_defaults,
)
from ROOT import TFile  # pyright: ignore[reportAttributeAccessIssue]
from sklearn.cluster import DBSCAN
from tqdm import tqdm

parser = argparse.ArgumentParser(
    description="Cluster energy deposition based on position"
)

parser.add_argument(
    "--InputFile",
    dest="InputFile",
    action="store",
    required=True,
    help="Input Geant4 ROOT file",
)

parser.add_argument(
    "--OutputFile",
    dest="OutputFile",
    action="store",
    required=True,
    help="Output .h5 file name",
)

parser.add_argument(
    "--ClusteringEps",
    dest="ClusteringEps",
    type=float,
    action="store",
    default=0.3,  # mm
    help="Spatial resolution for micro-clustering",
)

args = parser.parse_args()

InputFile = args.InputFile
OutputFile = args.OutputFile
ClusteringEps = args.ClusteringEps
print(f"Using {ClusteringEps}mm clustering parameter")

# Load input ROOT file

Infile = TFile(InputFile)
tree = Infile.Get("mcTree")

eventN = int(tree.GetEntries())

print(f"Loading: {InputFile}")
print(f"Total event number = {eventN}")


def is_nr(group):
    nr = group["depositionProcess"] == "ionIoni"
    nr |= (group["depositionProcess"] == "hadElastic") & (group["type"] == "neutron")
    return nr


def combine(group):
    dt = np.zeros(1, dtype=cluster_dtype)
    set_nan_defaults(dt)
    ed = group["energy"]
    nr = is_nr(group)
    dt["nr"] = ed[nr].sum()
    dt["er"] = ed[~nr].sum()
    dt["energy"] = ed.sum()
    for r, ne in zip(["er", "nr"], [~nr, nr]):
        if ne.sum() == 0:
            continue
        max_index = np.argmax(ed[ne], axis=0)
        for x in ["x", "y", "z", "t"]:
            dt[f"{r}_{x}"] = np.sum((group[x] * ed)[ne]) / ed[ne].sum()
        for s in [
            "parentId",
            "type",
            "parentType",
            "creatorProcess",
            "depositionProcess",
            "volume",
        ]:
            dt[f"{r}_{s}"] = group[s][ne][max_index]
    return dt


nr_x_offset = 1e4  # in mm


def clustering(tree, ClusteringEps):
    """
    DBSCAN density based clustering, http://scikit-learn.org/stable/modules/generated/sklearn.cluster.DBSCAN.html
    """

    scale_to_ns = (
        1e9 * ClusteringEps / 10
    )  # separate scatters that are 10ns away from each other

    nHits = int(tree.nHits)
    df = np.zeros(nHits, dtype=energy_dtype)
    df["runId"] = [int(tree.runId)] * nHits
    df["eventId"] = [int(tree.eventId)] * nHits
    df["x"], df["y"], df["z"] = list(tree.xd), list(tree.yd), list(tree.zd)
    df["t"] = list(tree.td)
    df["t"] *= scale_to_ns
    df["energy"] = list(tree.energy)
    # these field will be object in dataframe
    df["parentId"] = list(tree.parentId)
    df["type"] = [str(s) for s in list(tree.type)]
    df["parentType"] = [str(s) for s in list(tree.parentType)]
    df["creatorProcess"] = [str(s) for s in list(tree.creatorProcess)]
    df["depositionProcess"] = [str(s) for s in list(tree.depositionProcess)]
    df["volume"] = [str(s) for s in list(tree.volume)]

    df = df[df["energy"] > 0]
    df = np.sort(df, kind="stable", order="energy")[::-1]
    df = np.sort(df, kind="stable", order="t")

    nr = is_nr(df)
    df["x"][nr] += nr_x_offset  # Separately cluttering ER & NR

    highEflag = 1
    detE = df["energy"][df["volume"] == "lxenon"].sum() / 1e6
    if detE > 1.0:
        highEflag = 0
        print(
            f"Deposited {detE:.2f}GeV energy in LXe detector, will not perform micro clustering"
        )

    if ClusteringEps > 1e-6 and len(df) > 0 and highEflag:
        X = np.vstack(df[["x", "y", "z", "t"]].tolist())
        # X = np.vstack(df[['x', 'y', 'z']].tolist())
        try:
            # algorithm='brute' might be buggy
            # If memory usage exceed 10 GB, switch to ball_tree
            assert (4 * len(X) * len(X) * X.dtype.itemsize) / 1e9 < 10
            Y = np.sqrt((np.power(X - X[:, None], 2)).sum(axis=-1))
            db = DBSCAN(
                eps=ClusteringEps,
                min_samples=1,
                metric="precomputed",
                algorithm="brute",
            )
            label = db.fit_predict(Y)
        except Exception:
            print("Have to use ball tree, probably due to memory limit")
            db = DBSCAN(eps=ClusteringEps, min_samples=1, algorithm="ball_tree")
            label = db.fit_predict(X)
    else:
        label = np.arange(len(df))
        # Force NR-ER cluster
        # nr = is_nr(df)
        # label[nr] = 0
        # label[~nr] = 1
    df["label"] = label
    df["x"][nr] -= nr_x_offset

    df = np.sort(df, order="label")
    labels, index = np.unique(df["label"], return_index=True)
    index = np.append(index, len(df))

    dt = np.zeros(len(labels), dtype=cluster_dtype)
    set_nan_defaults(dt)
    for i in range(len(labels)):
        dt[i] = combine(df[index[i] : index[i + 1]])

    # scale back to second
    dt["er_t"] = dt["er_t"] / scale_to_ns
    dt["nr_t"] = dt["nr_t"] / scale_to_ns
    return dt


# Loop over & clustering

nHits = []
nPrimaries = []
for ii in range(eventN):
    tree.GetEntry(ii)
    nHits.append(int(tree.nHits))
    nPrimaries.append(int(tree.nPrimaries))

cluster = np.zeros(sum(nHits), dtype=cluster_dtype)
set_nan_defaults(cluster)
event = np.zeros(eventN, dtype=event_dtype)
set_nan_defaults(event)
primary = np.zeros(sum(nPrimaries), dtype=primary_dtype)
set_nan_defaults(primary)

estart = 0
eend = 0
pstart = 0
pend = 0
for ii in tqdm(range(eventN)):
    tree.GetEntry(ii)

    dt = clustering(tree, ClusteringEps)

    pend = pstart + int(tree.nPrimaries)
    primary[pstart:pend]["runId"] = int(tree.runId)
    primary[pstart:pend]["eventId"] = int(tree.eventId)
    primary[pstart:pend]["nPrimaries"] = int(tree.nPrimaries)
    primary[pstart:pend]["primaryEnergy"] = list(tree.primaryEnergy)
    primary[pstart:pend]["primaryPx"] = list(tree.primaryPx)
    primary[pstart:pend]["primaryPy"] = list(tree.primaryPy)
    primary[pstart:pend]["primaryPz"] = list(tree.primaryPz)
    primary[pstart:pend]["primaryX"] = list(tree.primaryX)
    primary[pstart:pend]["primaryY"] = list(tree.primaryY)
    primary[pstart:pend]["primaryZ"] = list(tree.primaryZ)
    primary[pstart:pend]["primaryId"] = list(tree.primaryId)
    primary[pstart:pend]["primaryType"] = [str(s) for s in list(tree.primaryType)]

    event[ii]["runId"] = int(tree.runId)
    event[ii]["eventId"] = int(tree.eventId)
    event[ii]["nHits"] = int(tree.nHits)
    event[ii]["nClusters"] = len(dt)
    event[ii]["nPrimaries"] = int(tree.nPrimaries)

    eend = estart + len(dt)
    if len(dt) > 0:
        cluster[estart:eend] = dt
        cluster[estart:eend]["runId"] = event[ii]["runId"]
        cluster[estart:eend]["eventId"] = event[ii]["eventId"]

        nr = dt["nr"] > 0
        for r, ne in zip(["er", "nr"], [~nr, nr]):
            in_veto = dt[f"{r}_volume"] == "OuterLXe"
            in_detector = dt[f"{r}_volume"] == "lxenon"
            for v, iv in zip(["veto_", ""], [in_veto, in_detector]):
                neiv = ne & iv
                argsort = dt[r][neiv].argsort()
                for a, ia in zip(["max", "alt"], [-1, -2]):
                    if neiv.sum() >= abs(ia):
                        event[ii][f"{v}{a}_{r}"] = dt[r][neiv][argsort[ia]]
                        for x in ["x", "y", "z", "t"]:
                            event[ii][f"{v}{a}_{r}_{x}"] = dt[f"{r}_{x}"][neiv][
                                argsort[ia]
                            ]
                        for s in [
                            "parentId",
                            "type",
                            "parentType",
                            "creatorProcess",
                            "depositionProcess",
                        ]:
                            event[ii][f"{v}{a}_{r}_{s}"] = dt[f"{r}_{s}"][neiv][
                                argsort[ia]
                            ]
                event[ii][f"{v}sum_{r}"] = dt[r][neiv].sum()
                event[ii][f"{v}num_{r}"] = neiv.sum()

    del dt
    pstart = pend
    estart = eend

cluster = cluster[:eend]

with h5py.File(OutputFile, "w") as opt:
    opt.create_dataset("primaries", data=primary, compression="gzip")
    opt.create_dataset("events", data=event, compression="gzip")
    opt.create_dataset("clusters", data=cluster, compression="gzip")

print(f"Saving: {OutputFile}")
print(f"Total cluster number = {event['nClusters'].sum()}")
