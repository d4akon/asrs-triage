import json
from pathlib import Path

import nbformat as nbf

SCRIPTS = ["evaluate.py", "baseline.py", "train_transformer.py"]
OUT = Path("notebooks/train_kaggle.ipynb")
META = Path("notebooks/kernel-metadata.json")


def main() -> None:
    cells = ["!pip install -q peft sentencepiece\n!pip uninstall -y -q torchao\n!mkdir -p scripts"]
    for name in SCRIPTS:
        cells.append(f"%%writefile scripts/{name}\n" + Path("scripts", name).read_text())
    cells.append(
        "import torch\nfrom pathlib import Path\n\n"
        "data_dir = next(Path('/kaggle/input').rglob('train.csv')).parent\n"
        "print(data_dir, torch.cuda.is_available(), "
        "torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'no GPU')"
    )
    cells.append("!python scripts/train_transformer.py --data-dir {data_dir} --out-dir /kaggle/working/transformer --epochs 6 --truncation head_tail")
    cells.append(
        "import json\n"
        "print(json.dumps(json.load(open('/kaggle/working/transformer/metrics.json'))['history'], indent=2))"
    )
    nb = nbf.v4.new_notebook()
    nb["cells"] = [nbf.v4.new_code_cell(src) for src in cells]
    nb["metadata"] = {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"}}
    nbf.write(nb, OUT)

    meta = json.loads(META.read_text())
    meta["dataset_sources"] = ["d4akon/asrs-triage-splits"]
    META.write_text(json.dumps(meta, indent=2) + "\n")
    print(f"wrote {OUT} with {len(cells)} cells")


if __name__ == "__main__":
    main()
