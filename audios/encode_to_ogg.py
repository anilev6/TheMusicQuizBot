from pathlib import Path
from pydub import AudioSegment
from pydub.utils import which
import shutil

from logs.mylogging import time_log_decorator


ALLOWED_EXTENSIONS = [".mp3"]  # TODO test and add formats


@time_log_decorator
def encode_to_ogg_opus(input_file_path, output_file_path):
    """This format is the only .ogg understood by iphones"""
    AudioSegment.converter = which("ffmpeg")
    audio = AudioSegment.from_file(input_file_path)
    result = audio.export(output_file_path, format="ogg", codec="libopus")
    return result.name


@time_log_decorator
def encode_to_ogg_and_replace(input_file_path):
    file_stem = Path(input_file_path).stem
    output_file_path = f"{Path(__file__).parent}/{file_stem}.ogg"
    result = encode_to_ogg_opus(input_file_path, output_file_path)
    shutil.move(input_file_path, result)
    return result


if __name__ == "__main__":
    # for generating the defaults
    ALLOWED_FORMATS = [".mp3"]
    LIST_OF_MUSIC_PATHS_ALL = [
        path
        for path in Path(__file__).parent.iterdir()
        if (path.suffix in ALLOWED_FORMATS and "_encoded.ogg" not in path.name)
    ]
    LIST_OF_MUSIC_NAMES_ALL = [str(p.stem).strip() for p in LIST_OF_MUSIC_PATHS_ALL]
    for track_path, track_name in zip(LIST_OF_MUSIC_PATHS_ALL, LIST_OF_MUSIC_NAMES_ALL):

        input_file_path = track_path
        output_file_path = Path(__file__).parent / (track_name + "_encoded.ogg")
        encode_to_ogg_opus(input_file_path, output_file_path)
