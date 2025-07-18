import json
import os
import shutil

import bids2nda


def test_taskname(tmpdir):
    """
    Task name can be from bids sidecar .json
    if that doesn't exist, pull from filename
    """
    # setup new dedicated bids input dir
    funcdir = tmpdir.join("in/sub-a/func")
    os.makedirs(funcdir)
    for ext in [".json", ".nii.gz"]:
        shutil.copyfile(
            os.path.join(
                os.getcwd(), "examples/bids-noses/sub-a/func/sub-a_task-rest_bold" + ext
            ),
            funcdir.join("sub-a_task-rest_bold" + ext),
        )
    shutil.copyfile(
        os.path.join(os.getcwd(), "examples/bids-noses/participants.tsv"),
        tmpdir / "in/participants.tsv",
    )
    shutil.copyfile(
        os.path.join(os.getcwd(), "examples/bids-noses/sub-a/sub-a_scans.tsv"),
        funcdir / "../sub-a_scans.tsv",
    )

    # run
    args = bids2nda.parse_args(
        [str(tmpdir / "in/"), "examples/guid_map.txt", str(tmpdir / "out")]
    )
    imgdf = bids2nda.run(args)
    assert imgdf.shape[0] == 1
    assert imgdf.image_description[0] == "bold rest"

    #  run again with TaskName in json
    sidecar_fname = funcdir.join("sub-a_task-rest_bold.json")
    with open(sidecar_fname, "r") as f:
        sidecar = json.load(f)
    sidecar["TaskName"] = "NOTREST"
    with open(sidecar_fname, "w") as f:
        f.write(json.dumps(sidecar))
    imgdf = bids2nda.run(args)
    assert imgdf.shape[0] == 1
    assert imgdf.image_description[0] == "bold NOTREST"
