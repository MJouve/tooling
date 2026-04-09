#!/usr/bin/env python3
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import uuid
from dataclasses import dataclass
from pathlib import Path

from flask import Flask, Response, jsonify, render_template, request, send_file


ROOT = Path(__file__).resolve().parent.parent
SPRITE_SCRIPT = ROOT / "mp4-to-sprite.py"


@dataclass
class Job:
    created_at: float
    dir_path: Path
    png_path: Path
    json_path: Path


app = Flask(__name__)
_jobs: dict[str, Job] = {}


def _cleanup_old_jobs(ttl_seconds: int = 30 * 60) -> None:
    now = time.time()
    to_delete = [job_id for job_id, job in _jobs.items() if now - job.created_at > ttl_seconds]
    for job_id in to_delete:
        job = _jobs.pop(job_id, None)
        if job:
            shutil.rmtree(job.dir_path, ignore_errors=True)


def _parse_bool(value: str | None) -> bool:
    if value is None:
        return False
    return value.lower() in {"1", "true", "yes", "on", "o", "oui"}


def _parse_int(value: str | None, default: int | None = None) -> int | None:
    if value is None or value == "":
        return default
    return int(value)


def _parse_float(value: str | None, default: float | None = None) -> float | None:
    if value is None or value == "":
        return default
    return float(value)

def _resolve_output_dir(output_dir_raw: str | None) -> Path | None:
    if output_dir_raw is None:
        return None
    output_dir = output_dir_raw.strip()
    if output_dir == "":
        return None

    p = Path(os.path.expanduser(output_dir))
    if not p.is_absolute():
        # Chemin relatif: on l’interprète depuis mp4-to-png/
        p = (ROOT / p).resolve()
    else:
        p = p.resolve()
    return p


@app.get("/")
def index() -> str:
    return render_template("index.html")

@app.post("/pick-output-dir")
def pick_output_dir() -> Response:
    """
    Ouvre un sélecteur de dossier natif sur la machine locale (serveur),
    et retourne le chemin sélectionné.
    """
    _cleanup_old_jobs()
    try:
        import tkinter as tk
        from tkinter import filedialog

        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        selected = filedialog.askdirectory(title="Choisir le dossier de sortie")
        root.destroy()

        if not selected:
            return jsonify({"ok": True, "selected": None})

        return jsonify({"ok": True, "selected": selected})
    except Exception as e:
        return jsonify(
            {
                "ok": False,
                "error": (
                    "Impossible d’ouvrir le sélecteur de dossier (tkinter). "
                    "Utilise la saisie manuelle dans le champ.\n"
                    f"Détails: {e}"
                ),
            }
        ), 400


@app.post("/generate")
def generate() -> Response:
    _cleanup_old_jobs()

    if not SPRITE_SCRIPT.exists():
        return jsonify({"ok": False, "error": f"Script introuvable: {SPRITE_SCRIPT}"}), 500

    if "file" not in request.files:
        return jsonify({"ok": False, "error": "Aucun fichier MP4 fourni (champ 'file')."}), 400

    file = request.files["file"]
    if not file.filename:
        return jsonify({"ok": False, "error": "Nom de fichier vide."}), 400

    job_id = uuid.uuid4().hex
    job_dir = Path(tempfile.mkdtemp(prefix=f"mp4-to-png-ui-{job_id}-"))
    input_path = job_dir / "input.mp4"
    file.save(input_path)

    # Paramètres
    size = _parse_int(request.form.get("size"), 128)
    width = _parse_int(request.form.get("width"), None)
    fps = _parse_int(request.form.get("fps"), 10)
    start = _parse_float(request.form.get("start"), 0.0)
    end = _parse_float(request.form.get("end"), None)
    transparent = _parse_bool(request.form.get("transparent"))
    tolerance = _parse_int(request.form.get("tolerance"), 30)
    crop = (request.form.get("crop") or "").strip() or None
    out_format = (request.form.get("format") or "png").strip().lower()
    webp_quality = _parse_int(request.form.get("webpQuality"), 80)
    webp_lossless = _parse_bool(request.form.get("webpLossless"))

    output_name = (request.form.get("outputName") or "sprite").strip()
    safe_name = "".join(ch for ch in output_name if ch.isalnum() or ch in {"-", "_"}).strip("-_")
    if not safe_name:
        safe_name = "sprite"

    output_dir = _resolve_output_dir(request.form.get("outputDir"))
    output_png_tmp = job_dir / f"{safe_name}.png"

    cmd: list[str] = [
        sys.executable,
        str(SPRITE_SCRIPT),
        str(input_path),
        "--size",
        str(size),
        "--fps",
        str(fps),
        "--start",
        str(start),
        "--output",
        str(output_png_tmp),
    ]

    if width is not None:
        cmd.extend(["--width", str(width)])
    if end is not None:
        cmd.extend(["--end", str(end)])
    if transparent:
        cmd.append("--transparent")
        cmd.extend(["--tolerance", str(tolerance)])
    if crop:
        cmd.extend(["--crop", crop])
    if out_format in {"png", "webp", "both"}:
        cmd.extend(["--format", out_format])
    if webp_quality is not None:
        cmd.extend(["--webp-quality", str(webp_quality)])
    if webp_lossless:
        cmd.append("--webp-lossless")

    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, check=True, cwd=str(ROOT))
    except subprocess.CalledProcessError as e:
        stderr = (e.stderr or "").strip()
        stdout = (e.stdout or "").strip()
        combined = "\n".join(x for x in [stdout, stderr] if x)
        shutil.rmtree(job_dir, ignore_errors=True)
        return jsonify({"ok": False, "error": combined or "Erreur lors de la génération."}), 400

    output_json_tmp = output_png_tmp.with_suffix(".json")
    if not output_png_tmp.exists() or not output_json_tmp.exists():
        shutil.rmtree(job_dir, ignore_errors=True)
        return jsonify({"ok": False, "error": "Sortie attendue manquante (PNG/JSON)."}), 500

    # Si un dossier de sortie est fourni, on y écrit directement les fichiers finals.
    final_png = output_png_tmp
    final_json = output_json_tmp
    final_dir_str = None
    if output_dir is not None:
        try:
            output_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            shutil.rmtree(job_dir, ignore_errors=True)
            return jsonify({"ok": False, "error": f"Impossible de créer le dossier de sortie: {output_dir}\n{e}"}), 400

        final_png = output_dir / f"{safe_name}.png"
        final_json = output_dir / f"{safe_name}.json"

        try:
            shutil.copy2(output_png_tmp, final_png)
            shutil.copy2(output_json_tmp, final_json)
        except Exception as e:
            shutil.rmtree(job_dir, ignore_errors=True)
            return jsonify({"ok": False, "error": f"Impossible d’écrire les fichiers dans: {output_dir}\n{e}"}), 400

        final_dir_str = str(output_dir)

    # Petit enrichissement: on renvoie le JSON parsé pour affichage rapide côté UI
    try:
        json_data = json.loads(final_json.read_text(encoding="utf-8"))
    except Exception:
        json_data = None

    _jobs[job_id] = Job(
        created_at=time.time(),
        dir_path=job_dir,
        png_path=final_png,
        json_path=final_json,
    )

    return jsonify(
        {
            "ok": True,
            "jobId": job_id,
            "downloads": {
                "png": f"/download/{job_id}/png",
                "json": f"/download/{job_id}/json",
            },
            "stdout": (proc.stdout or "").strip(),
            "meta": json_data,
            "writtenTo": final_dir_str,
        }
    )


@app.get("/download/<job_id>/<kind>")
def download(job_id: str, kind: str):
    _cleanup_old_jobs()
    job = _jobs.get(job_id)
    if not job:
        return jsonify({"ok": False, "error": "Job expiré ou inconnu."}), 404

    if kind == "png":
        return send_file(job.png_path, as_attachment=True, download_name=job.png_path.name)
    if kind == "json":
        return send_file(job.json_path, as_attachment=True, download_name=job.json_path.name)

    return jsonify({"ok": False, "error": "Type de fichier invalide."}), 400


def main() -> None:
    port = int(os.environ.get("PORT", "5179"))
    host = os.environ.get("HOST", "127.0.0.1")
    print(f"UI: http://{host}:{port}")
    app.run(host=host, port=port, debug=True)


if __name__ == "__main__":
    main()

