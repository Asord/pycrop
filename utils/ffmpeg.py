from sys import argv
from pathlib import Path
from binascii import b2a_hex
from os import urandom
from subprocess import check_output, STDOUT
from os import listdir

_APP_PATH = Path(argv[0]).resolve().parent
_FFMPEG_PATH = _APP_PATH.joinpath("vendor\\ffmpeg\\bin").resolve()
__DEBUG = False

_commands = {
    "crop":             ( 'ffmpeg.exe', '-i "{file_path}" -filter:v "crop={new_dim}" "{output}" -y'),
    "screenshot":       ( 'ffmpeg.exe', '-ss {timestamp} -i "{file_path}" -vframes 1 -q:v 2 "{tmp_name}"'),
    "screenshot_crop":  ( 'ffmpeg.exe', '-ss {timestamp} -i "{file_path}" -vf "crop={new_dim}" -vframes 1 "{tmp_name}"'),
    "length":           ('ffprobe.exe', '-i "{file_path}" -show_entries format=duration -v quiet -of csv="p=0"'),
}

def call(cmd_name, **kwargs):

    if cmd_name in _commands:
        _app = _FFMPEG_PATH.joinpath(_commands[cmd_name][0])
        _args = _commands[cmd_name][1].format(**kwargs)
        cmd = "%s %s" % (_app, _args)
    else:
        cmd = cmd_name
    if __DEBUG:
        print("Call: %s" % cmd_name)
        print(cmd)
    return check_output(cmd, shell=True, stderr=STDOUT)

class FFMPEG:
    def __init__(self, file_path: Path, output_folder="", output_prefix="c_", tmp_folder: Path=None):
        self._file_path = file_path

        self._output_folder = output_folder
        self._output_prefix = output_prefix

        self._tmp_folder = tmp_folder
        
        if self._tmp_folder is None: 
            self._tmp_folder = Path(file_path.parent).joinpath("tmp")
        self._tmp_folder.mkdir(exist_ok=True)

    def _createTmpFile(self):
        return  "%s/%s.jpg" % (self._tmp_folder, b2a_hex(urandom(3)).decode("utf-8"))

    def _createDim(self, new_dim):
        return ":".join([str(k) for k in new_dim])
    
    def getScreenshot(self, timestamp):
        _tmp_name = self._createTmpFile()
        call("screenshot", timestamp=timestamp, file_path=self._file_path, tmp_name=_tmp_name)
        return _tmp_name

    def getLength(self):
        res = call("length", file_path=self._file_path)
        return float(res)

    def crop(self, new_dim):
        new_dim = self._createDim(new_dim)
        output = Path(self._output_folder).joinpath("%s%s" % (self._output_prefix, self._file_path.name))
        call("crop", file_path=self._file_path, new_dim=new_dim, output=output)
        return output

    def createPreviewCrop(self, new_dim, timestamp):
        _tmp_name = self._createTmpFile()
        _new_dim = self._createDim(new_dim)
        call("screenshot_crop", timestamp=timestamp, file_path=self._file_path, new_dim=_new_dim, tmp_name=_tmp_name)
        
        try:  call("explorer.exe %s" % Path(_tmp_name).resolve()) 
        except Exception as e: pass # explorer love sending -1 errlvl for nothing...

    def __del__(self):        
        for file in listdir(self._tmp_folder): 
            Path(self._tmp_folder).joinpath(file).unlink()
        self._tmp_folder.rmdir()